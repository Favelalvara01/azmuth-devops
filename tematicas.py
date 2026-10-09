"""Temáticas de temporada de Azmuth: normal (Omnitrix), Halloween, Día de Muertos y Navidad.

La temática cambia los colores y animaciones de la ventana (azmuth.html), el saludo al
iniciar, un sonido corto de bienvenida y un toque ligero en las respuestas de la IA.

Por defecto es "auto": se pone sola según la fecha. También se puede elegir a mano
(por voz, chat o el botón 🎨) y la elección se guarda en la tabla `ajustes`.
"""
import datetime
import io
import math
import random
import struct
import wave

TEMAS = {
    "normal": {"es": "normal", "en": "normal"},
    "halloween": {"es": "Halloween", "en": "Halloween"},
    "muertos": {"es": "Día de Muertos", "en": "Day of the Dead"},
    "navidad": {"es": "Navidad", "en": "Christmas"},
}

# (mes, día) de inicio y fin de cada temporada; Navidad cruza el año nuevo.
_TEMPORADAS = (
    ("halloween", (10, 1), (10, 31)),
    ("muertos", (11, 1), (11, 3)),
    ("navidad", (12, 1), (12, 31)),
    ("navidad", (1, 1), (1, 6)),
)

_SALUDOS = {
    "normal": ("Sistema iniciado. A sus órdenes.", "System online. At your service."),
    "halloween": ("Sistema iniciado... justo a tiempo para la noche más tenebrosa. ¡Feliz Halloween, señor! A sus órdenes.",
                  "System online... just in time for the spookiest night. Happy Halloween, sir! At your service."),
    "muertos": ("Sistema iniciado. Las velas están encendidas y el cempasúchil marca el camino. "
                "¡Feliz Día de Muertos, señor! A sus órdenes.",
                "System online. The candles are lit and the marigolds light the way. "
                "Happy Day of the Dead, sir! At your service."),
    "navidad": ("Sistema iniciado. Huele a ponche y a luces nuevas. ¡Felices fiestas, señor! A sus órdenes.",
                "System online. Smells like hot punch and fresh lights. Happy holidays, sir! At your service."),
}

_TOQUES = {
    "halloween": "Halloween (calabazas, murciélagos, fantasmas) 🎃",
    "muertos": "Día de Muertos (cempasúchil, ofrendas, pan de muerto, calaveritas) 🌼",
    "navidad": "Navidad y fin de año (luces, ponche, posadas, regalos) 🎄",
}

_preferencia = None  # "auto" o el nombre de una temática; None = aún no se lee de la BD


def _hoy() -> datetime.date:
    return datetime.date.today()


def por_fecha(fecha: datetime.date = None) -> str:
    """Temática que toca en esa fecha (la de hoy si no se indica)."""
    fecha = fecha or _hoy()
    dia = (fecha.month, fecha.day)
    for nombre, inicio, fin in _TEMPORADAS:
        if inicio <= dia <= fin:
            return nombre
    return "normal"


def preferencia() -> str:
    """Lo que eligió el usuario: "auto" o el nombre de una temática."""
    global _preferencia
    if _preferencia is None:
        try:
            import chats
            valor = chats.obtener_ajuste("tematica", "auto")
        except Exception:
            valor = "auto"
        _preferencia = valor if valor == "auto" or valor in TEMAS else "auto"
    return _preferencia


def obtener() -> str:
    """Temática que se ve ahora mismo."""
    pref = preferencia()
    return por_fecha() if pref == "auto" else pref


def cambiar(nombre: str, guardar: bool = True) -> str:
    """Elige una temática ("auto" = según la fecha). Regresa la que queda activa."""
    global _preferencia
    nombre = (nombre or "").lower().strip()
    if nombre != "auto" and nombre not in TEMAS:
        return obtener()
    _preferencia = nombre
    if guardar:
        try:
            import chats
            chats.guardar_ajuste("tematica", nombre)
        except Exception:
            pass
    return obtener()


def nombre_visible(tema: str = None) -> str:
    import idioma
    return TEMAS[tema or obtener()][idioma.obtener()]


def saludo() -> str:
    import idioma
    es, en = _SALUDOS[obtener()]
    return idioma.t(es, en)


def extra_prompt() -> str:
    """Toque de temporada para la IA (vacío en la temática normal)."""
    toque = _TOQUES.get(obtener())
    if not toque:
        return ""
    return (f"\n\nTEMPORADA: la temática activa es {toque}. Puedes darle de vez en cuando un toque ligero "
            "de esa temporada a tus respuestas (una referencia breve o un emoji), sin exagerar y sin "
            "cambiar ni inventar información.")


# ----------------------------------------------------------------------------
# Sonido de bienvenida: se sintetiza en memoria (sin archivos) y se toca con
# winsound, que viene con Python en Windows. En otros sistemas no suena.
# ----------------------------------------------------------------------------
_TASA = 22050


def _nota(muestras, inicio, dur, frec, vol=0.4, decaimiento=3.0, parciales=((1, 1.0),), vibrato=0.0, glide_a=None):
    i0 = int(inicio * _TASA)
    n = int(dur * _TASA)
    fase = 0.0
    for k in range(n):
        t = k / _TASA
        f = frec if glide_a is None else frec + (glide_a - frec) * (t / dur)
        if vibrato:
            f *= 1 + vibrato * math.sin(2 * math.pi * 5.5 * t)
        fase += 2 * math.pi * f / _TASA
        ataque = min(1.0, t / 0.01)
        env = ataque * math.exp(-decaimiento * t) * min(1.0, (dur - t) / 0.03)
        valor = sum(a * math.sin(fase * m) for m, a in parciales)
        if 0 <= i0 + k < len(muestras):
            muestras[i0 + k] += vol * env * valor


def _cascabeles(muestras, inicio, dur, vol=0.12):
    rnd = random.Random(7)
    i0 = int(inicio * _TASA)
    previo = 0.0
    for k in range(int(dur * _TASA)):
        t = k / _TASA
        ruido = rnd.uniform(-1, 1)
        agudo = ruido - previo  # filtro sencillo: deja pasar lo agudo (cascabel)
        previo = ruido
        if 0 <= i0 + k < len(muestras):
            muestras[i0 + k] += vol * agudo * math.exp(-14 * (t % 0.12))


def _sintetizar(tema: str) -> bytes:
    dur = {"halloween": 2.6, "muertos": 1.9, "navidad": 2.2}.get(tema)
    if not dur:
        return b""
    m = [0.0] * int(dur * _TASA)
    if tema == "halloween":
        organo = ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15))
        for f in (146.83, 174.61, 220.0, 277.18):  # acorde menor tenebroso (con séptima)
            _nota(m, 0.0, 1.2, f, vol=0.18, decaimiento=1.2, parciales=organo)
        _nota(m, 0.9, 1.7, 620, vol=0.35, decaimiento=0.6, vibrato=0.025, glide_a=260)  # "uuuuh" de teremín
    elif tema == "muertos":
        marimba = ((1, 1.0), (4, 0.25), (10, 0.05))
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5, 1318.5)):
            _nota(m, i * 0.14, 0.6, f, vol=0.32, decaimiento=7, parciales=marimba)
        for f in (523.25, 659.25, 783.99):
            _nota(m, 1.0, 0.9, f, vol=0.2, decaimiento=4, parciales=marimba)
    elif tema == "navidad":
        campana = ((1, 1.0), (2.76, 0.4), (5.4, 0.2))
        ritmo = ((0, .22), (.25, .22), (.5, .45), (1.0, .22), (1.25, .22), (1.5, .6))
        for inicio, d in ritmo:  # "jingle bells, jingle bells"
            _nota(m, inicio, d + 0.3, 659.25, vol=0.3, decaimiento=5, parciales=campana)
        _cascabeles(m, 0.0, dur)
    pico = max(abs(x) for x in m) or 1.0
    salida = io.BytesIO()
    with wave.open(salida, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_TASA)
        w.writeframes(b"".join(struct.pack("<h", int(32767 * 0.8 * x / pico)) for x in m))
    return salida.getvalue()


def _reproducir(datos: bytes):
    import winsound
    winsound.PlaySound(datos, winsound.SND_MEMORY)


def reproducir_sonido(tema: str = None) -> bool:
    """Toca el sonido de la temática (espera a que termine). False si no hay o no se pudo."""
    datos = _sintetizar(tema or obtener())
    if not datos:
        return False
    try:
        _reproducir(datos)
        return True
    except Exception:
        return False
