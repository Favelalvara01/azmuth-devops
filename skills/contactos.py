"""
Skill: contactos — pequeña libreta de contactos propia de Azmuth
(nombre -> número), en la tabla "contactos".

WhatsApp no tiene ninguna forma de abrir un chat por nombre desde afuera
de la app -el enlace wa.me y el protocolo whatsapp:// solo entienden
números-, así que esta es la única manera real de que "mándale un
whatsapp a Jesús" funcione: Azmuth guarda su propia lista y hace la
traducción nombre -> número antes de armar el enlace. skills/web.py usa
buscar() para esto.
"""
import re

from basedatos import conectar

# Código de país + el "1" de celular que se agrega automáticamente cuando
# el número dado tiene pinta de ser un número nacional (10 dígitos, sin
# código de país). El "1" después del 52 ya no se usa para marcar por
# teléfono desde 2019, pero varias fuentes reportan que WhatsApp por
# dentro TODAVÍA lo pide para reconocer números celulares mexicanos.
# Cambia este valor si el usuario no vive en México.
_CODIGO_PAIS_DEFAULT = "521"


def normalizar_numero(numero: str) -> str:
    """Deja el número listo para WhatsApp (código de país + número,
    puros dígitos, sin "+"). Si son exactamente 10 dígitos, asumimos que
    es un número nacional mexicano y le anteponemos código de país + 1."""
    limpio = re.sub(r"[^\d]", "", numero or "")
    if len(limpio) == 10:
        return _CODIGO_PAIS_DEFAULT + limpio
    return limpio


def buscar(nombre: str):
    """Número guardado para ese nombre (sin importar mayúsculas), o None
    si no está guardado. La usa skills/web.py para resolver WhatsApp."""
    with conectar() as con:
        fila = con.execute(
            "SELECT numero FROM contactos WHERE lower(nombre) = ?", (nombre.strip().lower(),)
        ).fetchone()
    return fila["numero"] if fila else None


def intentar(texto: str):
    t = texto.strip()
    tl = t.lower()

    # --- BORRAR ---
    m = re.match(r"^borra\s+(?:el\s+)?contacto\s+(?:de\s+)?(.+)", tl)
    if m:
        nombre_buscado = m.group(1).strip()
        with conectar() as con:
            fila = con.execute(
                "SELECT nombre FROM contactos WHERE lower(nombre) = ?", (nombre_buscado,)
            ).fetchone()
            if not fila:
                return f'No tengo guardado ningún contacto llamado "{nombre_buscado}".'
            con.execute("DELETE FROM contactos WHERE nombre = ?", (fila["nombre"],))
        return f"Borré el contacto de {fila['nombre']}."

    # --- GUARDAR ---
    m = re.match(
        r"^guarda(?:\s+el)?\s+contacto\s+(?:de\s+)?(.+?)\s+(?:como|con el n[uú]mero|es)\s+([\d\s+]{7,})$",
        t, re.IGNORECASE,
    )
    if m:
        nombre = m.group(1).strip()
        numero = normalizar_numero(m.group(2))
        with conectar() as con:
            con.execute(
                "INSERT INTO contactos (nombre, numero) VALUES (?, ?) "
                "ON CONFLICT(nombre) DO UPDATE SET numero = excluded.numero",
                (nombre, numero),
            )
        return f"Listo, guardé a {nombre} con el número {numero}."

    # --- LISTAR ---
    if re.match(r"^(mis contactos|ver contactos|qué contactos tengo)", tl):
        with conectar() as con:
            filas = con.execute("SELECT nombre, numero FROM contactos ORDER BY nombre").fetchall()
        if not filas:
            return "No tiene contactos guardados."
        lineas = [f"{i + 1}. {f['nombre']} — {f['numero']}" for i, f in enumerate(filas)]
        return "Sus contactos:\n" + "\n".join(lineas)

    return None