"""
Skill: recordatorios.
Guarda recordatorios en la base de datos (tabla "recordatorios"). Hay
dos tipos:

1. DE UNA SOLA VEZ — "recuérdame hablar con Jesús a la 1". Suena una
   vez cuando llega esa hora y ya, se queda callado después (aunque no
   lo borres de la lista).

2. RECURRENTES — "recuérdame hacer ejercicio todos los días a las 7" o
   "recuérdame entregar el reporte los martes y jueves a las 9". Suena
   una vez por cada día que le toque, para siempre, hasta que lo borres.

Si no dices am/pm, Azmuth elige la hora más próxima en el futuro entre
las dos posibles (ej. "a la 1" sin más contexto puede ser 1pm si ya
pasó la 1am de hoy). Puedes ser explícito diciendo "de la mañana" /
"de la tarde" / "am" / "pm" si te preocupa la ambigüedad.

main.py revisa esto cada cierto tiempo en segundo plano llamando a
revisar_pendientes() — Azmuth tiene que estar corriendo a esa hora
para que el aviso suene.
"""
import re
import json
from datetime import datetime, timedelta

from basedatos import conectar

_HORA_RE = re.compile(
    r"^(.*?)\s+a\s+la[s]?\s+(\d{1,2})(?::(\d{2}))?\s*"
    r"(a\.?m\.?|p\.?m\.?|de la mañana|de la tarde|de la noche)?\s*$",
    re.IGNORECASE,
)

_DIAS_INDICE = {
    "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2, "jueves": 3,
    "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6,
}
_NOMBRES_DIAS = list(_DIAS_INDICE.keys())
_DIA_LEGIBLE = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}


def _calcular_hora_objetivo(hora_12: int, minuto: int, periodo: str):
    ahora = datetime.now()
    periodo = (periodo or "").lower()

    if periodo in ("am", "a.m.", "de la mañana"):
        candidatos = [ahora.replace(hour=hora_12 % 12, minute=minuto, second=0, microsecond=0)]
    elif periodo in ("pm", "p.m.", "de la tarde", "de la noche"):
        candidatos = [ahora.replace(hour=(hora_12 % 12) + 12, minute=minuto, second=0, microsecond=0)]
    else:
        candidatos = [
            ahora.replace(hour=hora_12 % 12, minute=minuto, second=0, microsecond=0),
            ahora.replace(hour=(hora_12 % 12) + 12, minute=minuto, second=0, microsecond=0),
        ]

    futuros = [c if c > ahora else c + timedelta(days=1) for c in candidatos]
    return min(futuros)


def _parsear(contenido: str):
    m = _HORA_RE.match(contenido)
    if not m:
        return contenido.strip(), None
    texto_limpio = m.group(1).strip()
    hora_12 = int(m.group(2))
    minuto = int(m.group(3)) if m.group(3) else 0
    periodo = m.group(4)
    hora_objetivo = _calcular_hora_objetivo(hora_12, minuto, periodo)
    return texto_limpio, hora_objetivo.isoformat()


def _extraer_dias(contenido: str):
    tl = contenido.lower()

    if re.search(r"\btodos\s+los\s+d[ií]as\b", tl):
        limpio = re.sub(r"\btodos\s+los\s+d[ií]as\b", "", contenido, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", limpio).strip(), []

    encontrados = [_DIAS_INDICE[n] for n in _NOMBRES_DIAS if re.search(rf"\b{n}\b", tl)]
    if not encontrados:
        return contenido, None

    patron_dias = r"\blos\s+(?:" + "|".join(_NOMBRES_DIAS) + r")(?:\s*(?:,|y)\s*(?:" + "|".join(_NOMBRES_DIAS) + r"))*\b"
    limpio = re.sub(patron_dias, "", contenido, flags=re.IGNORECASE)
    limpio = re.sub(r"\s{2,}", " ", limpio).strip()
    return limpio, sorted(set(encontrados))


def _describir_dias(dias):
    if not dias:
        return "todos los días"
    return "los " + ", ".join(_DIA_LEGIBLE[d] for d in dias)


def intentar(texto: str):
    t = texto.strip()
    tl = t.lower()

    # --- BORRAR TODOS ---
    if re.match(r"^(?:borra|elimina|limpia)\s+(?:todos\s+(?:los\s+)?)?(?:mis\s+)?recordatorios$", tl):
        with conectar() as con:
            con.execute("DELETE FROM recordatorios")
        return "Borré todos sus recordatorios."

    # --- BORRAR UNO ESPECÍFICO ---
    m = re.match(r"^(?:borra|elimina)\s+(?:el\s+)?recordatorio\s+(?:de|sobre)?\s*(.+)", tl)
    if m:
        clave = m.group(1).strip()
        with conectar() as con:
            cur = con.execute("DELETE FROM recordatorios WHERE lower(texto) LIKE ?", (f"%{clave}%",))
            if cur.rowcount == 0:
                return f'No encontré ningún recordatorio que mencione "{clave}".'
        return f'Borré el recordatorio sobre "{clave}".'

    # --- CREAR ---
    m = re.match(r"^(?:recuérdame|recordatorio|ponme un recordatorio)(?:\s+(?:de|para))?[:\s]+(.+)", t, re.IGNORECASE)
    if m:
        contenido = m.group(1).strip()
        contenido, dias = _extraer_dias(contenido)
        texto_limpio, hora_objetivo = _parsear(contenido)

        if dias is not None:
            # --- RECORDATORIO RECURRENTE ---
            if not hora_objetivo:
                return (
                    'Para un recordatorio que se repite necesito que me diga una hora, '
                    'por ejemplo "recuérdame hacer ejercicio los martes y jueves a las 7".'
                )
            hora_hhmm = datetime.fromisoformat(hora_objetivo).strftime("%H:%M")
            with conectar() as con:
                con.execute(
                    "INSERT INTO recordatorios (texto, recurrente, hora, dias, fecha_creado) VALUES (?, 1, ?, ?, ?)",
                    (texto_limpio, hora_hhmm, json.dumps(dias), datetime.now().isoformat()),
                )
            return f'Recordatorio recurrente anotado: "{texto_limpio}". Le aviso {_describir_dias(dias)} a las {hora_hhmm}.'

        # --- RECORDATORIO DE UNA SOLA VEZ ---
        with conectar() as con:
            con.execute(
                "INSERT INTO recordatorios (texto, recurrente, hora_objetivo, fecha_creado) VALUES (?, 0, ?, ?)",
                (texto_limpio, hora_objetivo, datetime.now().isoformat()),
            )
        if hora_objetivo:
            hora_legible = datetime.fromisoformat(hora_objetivo).strftime("%H:%M")
            return f'Recordatorio anotado: "{texto_limpio}". Le aviso a las {hora_legible}.'
        return f'Recordatorio anotado: "{texto_limpio}".'

    # --- LISTAR ---
    if re.match(r"^(mis recordatorios|ver recordatorios|qué recordatorios tengo)", tl):
        with conectar() as con:
            filas = con.execute("SELECT * FROM recordatorios ORDER BY id").fetchall()
        if not filas:
            return "No tiene recordatorios pendientes."
        lineas = []
        for i, r in enumerate(filas):
            if r["recurrente"]:
                dias = json.loads(r["dias"]) if r["dias"] else []
                lineas.append(f"{i + 1}. {r['texto']} ({_describir_dias(dias)} a las {r['hora']})")
            elif r["hora_objetivo"]:
                hora_legible = datetime.fromisoformat(r["hora_objetivo"]).strftime("%H:%M")
                lineas.append(f"{i + 1}. {r['texto']} (a las {hora_legible})")
            else:
                lineas.append(f"{i + 1}. {r['texto']}")
        return "Sus recordatorios:\n" + "\n".join(lineas)

    return None


def revisar_pendientes():
    """
    Llamada periódicamente desde main.py en segundo plano. Regresa una
    lista de textos cuya hora ya llegó y no se habían avisado todavía
    (hoy, si son recurrentes), y los marca para no repetirlos de más.
    """
    ahora = datetime.now()
    hoy_str = ahora.strftime("%Y-%m-%d")
    hoy_semana = ahora.weekday()
    avisos = []

    with conectar() as con:
        filas = con.execute("SELECT * FROM recordatorios").fetchall()
        for r in filas:
            if r["recurrente"]:
                dias = json.loads(r["dias"]) if r["dias"] else []
                if dias and hoy_semana not in dias:
                    continue
                if r["ultima_notificacion"] == hoy_str:
                    continue
                if not r["hora"]:
                    continue
                hh, mm = map(int, r["hora"].split(":"))
                objetivo_hoy = ahora.replace(hour=hh, minute=mm, second=0, microsecond=0)
                if ahora >= objetivo_hoy:
                    avisos.append(r["texto"])
                    con.execute("UPDATE recordatorios SET ultima_notificacion = ? WHERE id = ?", (hoy_str, r["id"]))
            else:
                if r["hora_objetivo"] and not r["notificado"]:
                    hora_objetivo = datetime.fromisoformat(r["hora_objetivo"])
                    if ahora >= hora_objetivo:
                        avisos.append(r["texto"])
                        con.execute("UPDATE recordatorios SET notificado = 1 WHERE id = ?", (r["id"],))
    return avisos
