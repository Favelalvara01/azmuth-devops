"""
Skill: memoria — memoria a largo plazo de Azmuth (tabla "memoria").

Dos formas de llegar aquí:
  1. EXPLÍCITA — usted dice "recuerda que X" por voz.
  2. AUTOMÁTICA — cerebro.py detecta solo, durante una conversación
     libre con Claude, algo que vale la pena recordar, y lo guarda sin
     que usted tenga que pedirlo (ver guardar_hecho() y la columna
     "origen" de cada hecho guardado).

A diferencia de las notas (cosas puntuales) o los recordatorios (avisos
con hora), esto es para datos y gustos que Azmuth debe tener presentes
siempre que hable con usted. recordar_todo() la usa cerebro.py para
inyectar estos hechos en cada conversación — ese es el puente entre lo
que Azmuth aprende y cómo conversa.
"""
import re
from datetime import datetime

from basedatos import conectar


def _parecidos(a: str, b: str) -> bool:
    """Comparación simple para no duplicar el mismo hecho dos veces
    (típico de la extracción automática: el usuario puede mencionar lo
    mismo en varias conversaciones distintas)."""
    a, b = a.lower().strip(), b.lower().strip()
    return a == b or a in b or b in a


def recordar_todo():
    """Lista de textos guardados, tal cual, para que cerebro.py se los
    pase a Claude como contexto. No truena si la base no existe todavía."""
    try:
        with conectar() as con:
            filas = con.execute("SELECT texto FROM memoria ORDER BY id").fetchall()
        return [f["texto"] for f in filas]
    except Exception:
        return []


def guardar_hecho(texto: str, origen: str = "manual") -> bool:
    """Guarda un hecho nuevo si no hay ya uno muy parecido guardado.
    origen: "voz" (dijo "recuerda que..."), "automatico" (lo captó
    cerebro.py solo durante una conversación libre) o "manual".
    Regresa True si lo guardó, False si ya existía algo parecido."""
    texto = (texto or "").strip()
    if not texto:
        return False
    with conectar() as con:
        existentes = con.execute("SELECT texto FROM memoria").fetchall()
        if any(_parecidos(texto, f["texto"]) for f in existentes):
            return False
        con.execute(
            "INSERT INTO memoria (texto, fecha, origen) VALUES (?, ?, ?)",
            (texto, datetime.now().isoformat(), origen),
        )
    return True


def intentar(texto: str):
    t = texto.strip()
    tl = t.lower()

    # --- OLVIDAR TODO ---
    if re.match(r"^(?:olvida|borra)\s+todo\s+lo\s+que\s+recuerdas$", tl):
        with conectar() as con:
            con.execute("DELETE FROM memoria")
        return "Listo, borré toda mi memoria de largo plazo sobre usted."

    # --- OLVIDAR ALGO ESPECÍFICO ---
    m = re.match(r"^olv[ií]date?\s+(?:de\s+)?(?:lo\s+de\s+)?(?:que\s+)?(.+)", tl)
    if m:
        clave = m.group(1).strip()
        with conectar() as con:
            cur = con.execute("DELETE FROM memoria WHERE lower(texto) LIKE ?", (f"%{clave}%",))
            if cur.rowcount == 0:
                return f'No tengo nada guardado sobre "{clave}".'
        return f'Listo, olvidé lo de "{clave}".'

    # --- GUARDAR (explícito, por voz) ---
    m = re.match(r"^recuerda\s+que\s+(.+)", t, re.IGNORECASE)
    if m:
        contenido = m.group(1).strip()
        if guardar_hecho(contenido, origen="voz"):
            return f"Guardado. Ya sé que {contenido}."
        return "Eso ya lo tenía guardado, señor."

    # --- CONSULTAR ---
    m = re.match(r"^(?:qué recuerdas|que recuerdas|qué sabes|que sabes)(?:\s+(?:de|sobre|acerca de)\s+(.+))?$", tl)
    if m:
        clave = (m.group(1) or "").strip()
        with conectar() as con:
            if clave:
                filas = con.execute(
                    "SELECT texto FROM memoria WHERE lower(texto) LIKE ? ORDER BY id", (f"%{clave}%",)
                ).fetchall()
            else:
                filas = con.execute("SELECT texto FROM memoria ORDER BY id").fetchall()
        if not filas:
            return f'No tengo nada guardado sobre "{clave}".' if clave else "Todavía no me ha pedido que recuerde nada."
        lineas = [f"{i + 1}. {f['texto']}" for i, f in enumerate(filas)]
        return "Esto es lo que recuerdo:\n" + "\n".join(lineas)

    return None
