"""
chats.py — Conversaciones escritas del MODO ESCRITORIO de Azmuth.

Cada chat es una conversación independiente (como en ChatGPT o Claude):
tiene título, mensajes del usuario ("user") y de Azmuth ("assistant"),
y vive en las tablas "chats" y "mensajes" de datos/azmuth.db.

También guarda cuál es el chat ACTIVO (tabla "ajustes"), para que los
comandos de voz que se digan en modo escritorio aparezcan en ese chat.
"""
from datetime import datetime

from basedatos import conectar

_MAX_TITULO = 48
_MENSAJES_DE_CONTEXTO = 20  # cuántos mensajes recientes se mandan a Claude


def _ahora():
    return datetime.now().isoformat(timespec="seconds")


def _titulo_desde(texto: str) -> str:
    limpio = " ".join((texto or "").split())
    if len(limpio) <= _MAX_TITULO:
        return limpio or "Nuevo chat"
    return limpio[:_MAX_TITULO].rsplit(" ", 1)[0] + "…"


# ------------------------------------------------------------------ chats
def crear_chat(titulo: str = "Nuevo chat") -> int:
    with conectar() as con:
        cur = con.execute("INSERT INTO chats (titulo, creado, actualizado) VALUES (?, ?, ?)",
                          (titulo, _ahora(), _ahora()))
        chat_id = cur.lastrowid
    fijar_activo(chat_id)
    return chat_id


def listar_chats():
    """Chats del más reciente al más antiguo, con su número de mensajes."""
    with conectar() as con:
        filas = con.execute("""
            SELECT c.id, c.titulo, c.actualizado, COUNT(m.id) AS mensajes
            FROM chats c LEFT JOIN mensajes m ON m.chat_id = c.id
            GROUP BY c.id ORDER BY c.actualizado DESC, c.id DESC
        """).fetchall()
    return [dict(f) for f in filas]


def existe(chat_id: int) -> bool:
    with conectar() as con:
        return con.execute("SELECT 1 FROM chats WHERE id = ?", (chat_id,)).fetchone() is not None


def renombrar_chat(chat_id: int, titulo: str):
    titulo = _titulo_desde(titulo)
    with conectar() as con:
        con.execute("UPDATE chats SET titulo = ? WHERE id = ?", (titulo, chat_id))
    return titulo


def borrar_chat(chat_id: int):
    with conectar() as con:
        con.execute("DELETE FROM mensajes WHERE chat_id = ?", (chat_id,))
        con.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    if obtener_activo(crear_si_no_hay=False) == chat_id:
        _set_ajuste("chat_activo", "")


# --------------------------------------------------------------- mensajes
def agregar_mensaje(chat_id: int, rol: str, texto: str, origen: str = "texto") -> dict:
    """Guarda un mensaje. El primer mensaje del usuario le pone título al chat."""
    with conectar() as con:
        cur = con.execute("INSERT INTO mensajes (chat_id, rol, texto, origen, fecha) VALUES (?, ?, ?, ?, ?)",
                          (chat_id, rol, texto, origen, _ahora()))
        con.execute("UPDATE chats SET actualizado = ? WHERE id = ?", (_ahora(), chat_id))
        if rol == "user":
            fila = con.execute("SELECT titulo, (SELECT COUNT(*) FROM mensajes WHERE chat_id = ? AND rol = 'user') n "
                               "FROM chats WHERE id = ?", (chat_id, chat_id)).fetchone()
            if fila and fila["n"] == 1 and fila["titulo"] == "Nuevo chat":
                con.execute("UPDATE chats SET titulo = ? WHERE id = ?", (_titulo_desde(texto), chat_id))
        return {"id": cur.lastrowid, "rol": rol, "texto": texto, "origen": origen}


def obtener_mensajes(chat_id: int):
    with conectar() as con:
        filas = con.execute("SELECT id, rol, texto, origen, fecha FROM mensajes WHERE chat_id = ? ORDER BY id",
                            (chat_id,)).fetchall()
    return [dict(f) for f in filas]


def historial_para_ia(chat_id: int):
    """Últimos mensajes en el formato de la API de Claude: alternando
    user/assistant y empezando siempre con un mensaje del usuario."""
    mensajes = obtener_mensajes(chat_id)[-_MENSAJES_DE_CONTEXTO:]
    resultado = []
    for m in mensajes:
        if resultado and resultado[-1]["role"] == m["rol"]:
            resultado[-1]["content"] += "\n\n" + m["texto"]  # junta dos seguidos del mismo rol
        else:
            resultado.append({"role": m["rol"], "content": m["texto"]})
    while resultado and resultado[0]["role"] != "user":
        resultado.pop(0)
    return resultado


# ----------------------------------------------------------- chat activo
def _set_ajuste(clave, valor):
    with conectar() as con:
        con.execute("INSERT INTO ajustes (clave, valor) VALUES (?, ?) "
                    "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (clave, str(valor)))


def obtener_ajuste(clave, por_defecto=None):
    try:
        with conectar() as con:
            fila = con.execute("SELECT valor FROM ajustes WHERE clave = ?", (clave,)).fetchone()
        return fila["valor"] if fila and fila["valor"] != "" else por_defecto
    except Exception:
        return por_defecto


def guardar_ajuste(clave, valor):
    _set_ajuste(clave, valor)


def fijar_activo(chat_id: int):
    _set_ajuste("chat_activo", chat_id)


def obtener_activo(crear_si_no_hay: bool = True):
    valor = obtener_ajuste("chat_activo")
    if valor and valor.isdigit() and existe(int(valor)):
        return int(valor)
    if crear_si_no_hay:
        return crear_chat()
    return None
