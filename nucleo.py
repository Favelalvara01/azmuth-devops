"""
nucleo.py — El "cerebro de decisiones" compartido por todos los canales.

Tanto la voz (main.py) como el chat escrito del modo escritorio
(servidor.py) pasan por aquí, así que un comando funciona igual sin
importar cómo se diga:

  1. Primero intenta resolverlo una skill local (instantáneo, sin IA).
  2. Si ninguna aplica, se lo pregunta a Claude (cerebro.py).

responder_en_chat() además guarda la conversación en el chat activo
(chats.py) para que aparezca en la ventana del modo escritorio.
"""
import cerebro
import chats
import estado
import skills


def responder(texto: str, mensajes=None, modo: str = "voz"):
    """Regresa (respuesta, categoria). categoria = nombre de la skill o "ia"."""
    respuesta, categoria = skills.procesar(texto)
    if respuesta is None:
        categoria = "ia"
        respuesta = cerebro.preguntar(texto, mensajes=mensajes, modo=modo)
    skills.habitos.registrar_uso(categoria)
    return respuesta, categoria


def responder_en_chat(texto: str, chat_id=None, origen: str = "texto"):
    """Guarda el mensaje del usuario, responde con el historial del chat y
    guarda la respuesta. Regresa (respuesta, categoria, chat_id)."""
    if not chat_id or not chats.existe(chat_id):
        chat_id = chats.obtener_activo()
    chats.fijar_activo(chat_id)
    chats.agregar_mensaje(chat_id, "user", texto, origen)
    estado.aviso_chat_nuevo()
    respuesta, categoria = responder(texto, mensajes=chats.historial_para_ia(chat_id), modo="escritorio")
    chats.agregar_mensaje(chat_id, "assistant", respuesta, origen)
    estado.aviso_chat_nuevo()
    return respuesta, categoria, chat_id
