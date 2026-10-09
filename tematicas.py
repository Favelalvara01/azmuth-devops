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
    "halloween": ("Sistema iniciado... justo a tiempo para la noche más tenebrosa. ¡Feliz Halloween, {trato}! A sus órdenes.",
                  "System online... just in time for the spookiest night. Happy Halloween, {trato}! At your service."),
    "muertos": ("Sistema iniciado. Las velas están encendidas y el cempasúchil marca el camino. "
                "¡Feliz Día de Muertos, {trato}! A sus órdenes.",
                "System online. The candles are lit and the marigolds light the way. "
                "Happy Day of the Dead, {trato}! At your service."),
    "navidad": ("Sistema iniciado. Huele a ponche y a luces nuevas. ¡Felices fiestas, {trato}! A sus órdenes.",
                "System online. Smells like hot punch and fresh lights. Happy holidays, {trato}! At your service."),
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
    return idioma.bienvenida() + idioma.t(es, en).format(trato=idioma.trato())


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


# --- Voz sintetizada por formantes (risa de bruja y "¡jo, jo, jo!" de Santa) ---
# Fuente: pulso glotal de Rosenberg (como las cuerdas vocales) + ruido para la "j";
# filtro: resonadores en las frecuencias de cada vocal ("a", "i", "o").
_VOCAL_A_AGUDA = ((1000, 110, 1.0), (1650, 140, 0.7), (2900, 200, 0.35), (3700, 260, 0.2))
_VOCAL_I_AGUDA = ((420, 90, 1.0), (2600, 160, 0.8), (3300, 220, 0.4))
_VOCAL_O_GRAVE = ((480, 80, 1.0), (820, 90, 0.7), (2450, 160, 0.12), (3100, 200, 0.06))


def _resonador(x, frec, ancho):
    r = math.exp(-math.pi * ancho / _TASA)
    c, d, g = 2 * r * math.cos(2 * math.pi * frec / _TASA), -r * r, 1 - r
    y1 = y2 = 0.0
    salida = []
    for v in x:
        y = g * v + c * y1 + d * y2
        salida.append(y)
        y2, y1 = y1, y
    return salida


def _silaba(dur, f0_ini, f0_fin, vocal, rnd, aire=0.03, vibrato=0.0, ronco=0.0):
    """Una sílaba: aire al inicio (la "j") y luego la vocal, con el tono de f0_ini a f0_fin."""
    n = int(dur * _TASA)
    fuente, fase, previo = [], 0.0, 0.0
    for k in range(n):
        t = k / _TASA
        f0 = (f0_ini + (f0_fin - f0_ini) * t / dur) * (1 + vibrato * math.sin(2 * math.pi * 6.5 * t)
                                                         + 0.012 * rnd.uniform(-1, 1))
        fase = (fase + f0 / _TASA) % 1.0
        if fase < 0.6:
            flujo = 0.5 * (1 - math.cos(math.pi * fase / 0.6))
        elif fase < 0.75:
            flujo = math.cos(math.pi * (fase - 0.6) / 0.3)
        else:
            flujo = 0.0
        pulso = (flujo - previo) * _TASA / max(f0, 1) * 0.15
        previo = flujo
        ruido = rnd.uniform(-1, 1)
        fuente.append(ruido * 0.6 * t / aire if t < aire else pulso + ronco * ruido)
    voz = [0.0] * n
    for frec, ancho, ganancia in vocal:
        for i, v in enumerate(_resonador(fuente, frec, ancho)):
            voz[i] += ganancia * v
    return [v * min(1.0, k / _TASA / 0.012) * min(1.0, (dur - k / _TASA) / 0.04) for k, v in enumerate(voz)]


def _mezclar(muestras, inicio, sonido, vol):
    i0 = int(inicio * _TASA)
    pico = max((abs(v) for v in sonido), default=1.0) or 1.0
    for k, v in enumerate(sonido):
        if 0 <= i0 + k < len(muestras):
            muestras[i0 + k] += vol * v / pico


def _risa_de_bruja(muestras, inicio):
    """ "Jiiii... ja-ja-ja-ja-jaaa": chillona, rasposa y bajando de tono."""
    rnd = random.Random(3)
    _mezclar(muestras, inicio, _silaba(0.45, 520, 1150, _VOCAL_I_AGUDA, rnd, aire=0.05, vibrato=0.04, ronco=0.25), 0.6)
    t = inicio + 0.5
    for i in range(13):
        f = 980 - i * 32 + rnd.uniform(-25, 25)
        ultima = i == 12
        _mezclar(muestras, t, _silaba(0.42 if ultima else 0.095, f * 1.05, f * (0.7 if ultima else 0.92), _VOCAL_A_AGUDA, rnd,
                                      aire=0.028, vibrato=0.06 if ultima else 0.03, ronco=0.3), 0.8 - i * 0.025)
        t += 0.125


def _jo_jo_jo(muestras, inicio):
    """ "¡Jo, jo, jo!" grave y alegre, cada "jo" un poco más bajo."""
    rnd = random.Random(5)
    for t, dur, f_ini, f_fin in ((0.0, 0.42, 128, 104), (0.55, 0.42, 124, 100), (1.1, 0.75, 120, 88)):
        _mezclar(muestras, inicio + t, _silaba(dur, f_ini, f_fin, _VOCAL_O_GRAVE, rnd, aire=0.09, vibrato=0.02, ronco=0.02), 0.85)


def _sintetizar(tema: str) -> bytes:
    dur = {"halloween": 3.0, "muertos": 1.9, "navidad": 3.8}.get(tema)
    if not dur:
        return b""
    m = [0.0] * int(dur * _TASA)
    if tema == "halloween":
        organo = ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15))
        for f in (73.42, 87.31, 110.0):  # acorde de órgano grave y bajito, de fondo
            _nota(m, 0.0, 3.0, f, vol=0.05, decaimiento=0.5, parciales=organo)
        _risa_de_bruja(m, 0.05)
    elif tema == "muertos":
        marimba = ((1, 1.0), (4, 0.25), (10, 0.05))
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5, 783.99, 1046.5, 1318.5)):
            _nota(m, i * 0.14, 0.6, f, vol=0.32, decaimiento=7, parciales=marimba)
        for f in (523.25, 659.25, 783.99):
            _nota(m, 1.0, 0.9, f, vol=0.2, decaimiento=4, parciales=marimba)
    elif tema == "navidad":
        _jo_jo_jo(m, 0.0)
        campana = ((1, 1.0), (2.76, 0.4), (5.4, 0.2))
        ritmo = ((0, .22), (.25, .22), (.5, .45), (1.0, .22), (1.25, .22), (1.5, .6))
        for inicio, d in ritmo:  # luego "jingle bells, jingle bells" con cascabeles
            _nota(m, 2.0 + inicio * 0.8, d + 0.3, 659.25, vol=0.22, decaimiento=5, parciales=campana)
        _cascabeles(m, 1.9, dur - 1.9, vol=0.08)
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


def archivo_propio(tema: str):
    """Si el usuario puso su propio sonido en datos/sonidos/<tema>.wav, se usa ese."""
    import os
    import rutas
    ruta = os.path.join(rutas.CARPETA_DATOS, "sonidos", f"{tema}.wav")
    return ruta if os.path.isfile(ruta) else None


def reproducir_sonido(tema: str = None) -> bool:
    """Toca el sonido de la temática (espera a que termine). False si no hay o no se pudo."""
    tema = tema or obtener()
    try:
        propio = archivo_propio(tema)
        datos = open(propio, "rb").read() if propio else _sintetizar(tema)
        if not datos:
            return False
        _reproducir(datos)
        return True
    except Exception:
        return False
