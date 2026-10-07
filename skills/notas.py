"""
Skill: notas.
Guarda notas sueltas en la base de datos (tabla "notas" de basedatos.py).
A diferencia de un recordatorio, una nota no tiene hora ni avisa sola —
solo queda guardada para consultarla después ("mis notas").
"""
import re
from datetime import datetime

from basedatos import conectar


def intentar(texto: str):
    t = texto.strip()
    tl = t.lower()

    # --- BORRAR TODAS ---
    if re.match(r"^(?:borra|elimina|limpia)\s+(?:todas\s+(?:las\s+)?)?(?:mis\s+)?notas$", tl):
        with conectar() as con:
            con.execute("DELETE FROM notas")
        return "Borré todas sus notas."

    # --- BORRAR UNA ESPECÍFICA ---
    m = re.match(r"^(?:borra|elimina)\s+(?:la\s+)?nota\s+(?:de|sobre)?\s*(.+)", tl)
    if m:
        clave = m.group(1).strip()
        with conectar() as con:
            cur = con.execute("DELETE FROM notas WHERE lower(texto) LIKE ?", (f"%{clave}%",))
            if cur.rowcount == 0:
                return f'No encontré ninguna nota que mencione "{clave}".'
        return f'Borré la nota sobre "{clave}".'

    # --- CREAR ---
    m = re.match(r"^(?:toma nota|anota|apunta)(?:\s+(?:de|que))?[:\s]+(.+)", t, re.IGNORECASE)
    if m:
        contenido = m.group(1).strip()
        with conectar() as con:
            con.execute("INSERT INTO notas (texto, fecha) VALUES (?, ?)", (contenido, datetime.now().isoformat()))
        return f'Nota guardada: "{contenido}".'

    # --- LISTAR ---
    if re.match(r"^(mis notas|ver notas|qué notas tengo)", tl):
        with conectar() as con:
            filas = con.execute("SELECT texto FROM notas ORDER BY id").fetchall()
        if not filas:
            return "No tiene notas guardadas."
        lineas = [f"{i + 1}. {fila['texto']}" for i, fila in enumerate(filas)]
        return "Sus notas:\n" + "\n".join(lineas)

    return None
