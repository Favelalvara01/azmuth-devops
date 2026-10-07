"""
Skill: modos — cambia entre el MODO VOZ (ventana pequeña con el núcleo
animado) y el MODO ESCRITORIO (ventana grande con chat escrito).

Funciona igual por voz ("omnitrix, modo escritorio") que escrito en el
chat ("modo voz"). El cambio de tamaño de la ventana lo hace
app_desktop.py, que escucha los cambios de modo en estado.py.
"""
import re

import estado

_PREFIJO = r"^(?:(?:cambia|cambiar|pasa|pasar|ponte|activa|activar|entra|entrar|abre|abrir|vamos)\s+(?:a|al|en)?\s*(?:el\s+)?)?"
_ESCRITORIO = re.compile(_PREFIJO + r"modo\s+(?:escritorio|chat|texto|escrito)\b")
_VOZ = re.compile(_PREFIJO + r"modo\s+(?:voz|normal|compacto)\b|^sal(?:ir)?\s+del\s+modo\s+escritorio\b")


def intentar(texto: str):
    t = (texto or "").lower().strip()
    if _ESCRITORIO.match(t):
        if estado.obtener_modo() == "escritorio":
            return "Ya estamos en modo escritorio, señor. Escríbame lo que necesite."
        estado.set_modo("escritorio")
        return "Modo escritorio activado. Puede escribirme o seguir hablándome."
    if _VOZ.match(t):
        if estado.obtener_modo() == "voz":
            return "Ya estamos en modo voz."
        estado.set_modo("voz")
        return "Modo voz activado. Lo escucho, señor."
    return None
