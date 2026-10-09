"""Acciones que esperan un "sí" antes de hacerse (por ejemplo, enviar un WhatsApp).

Una skill llama a pedir(...) y regresa la pregunta ("¿Lo envío?"). La siguiente frase
del usuario pasa primero por resolver(): "sí" / "envíalo" → se hace la acción; "no" /
"cancela" → se cancela; cualquier otra cosa → se olvida la pendiente (para que un "sí"
dicho mucho después nunca mande nada por sorpresa) y la frase se atiende normal.
"""
import re
import threading
import time

_ESPERA_MAXIMA = 90  # segundos: después de esto la pregunta caduca
_pendiente = None
_candado = threading.Lock()

# Un "sí" solo cuenta si TODA la frase es de aceptación ("sí", "sí, envíalo", "dale, mándalo
# por favor"): así "sí, pero cámbiale el mensaje" no envía nada.
_PALABRAS_SI = {"si", "sí", "sii", "síí", "claro", "dale", "dele", "va", "órale", "orale", "simón", "simon", "ok",
                "okay", "okey", "adelante", "hazlo", "envíalo", "envialo", "envíale", "enviale", "envía", "envia",
                "mándalo", "mandalo", "mándale", "mandale", "manda", "ya", "porfa", "yes", "yeah", "yep", "sure",
                "please", "send", "it", "do", "go", "ahead", "por", "favor", "de", "acuerdo", "perfecto", "exacto"}
_NO = re.compile(r"^(?:no|nel|nop|nope|cancela(?:lo)?|cancelar|mejor no|ahorita no|todav[ií]a no|"
                 r"d[eé]jalo|olv[ií]dalo|cancel|don'?t|stop)\b")


def _limpio(texto: str) -> str:
    t = re.sub(r"[¿?¡!.,]", " ", (texto or "").lower())
    t = re.sub(r"^(?:(?:hey|oye|ok)\s+)?(?:azmuth\s+)?", "", " ".join(t.split()))
    return t.strip()


def pedir(accion, al_cancelar: str = "Cancelado."):
    """Deja una acción esperando confirmación. `accion()` regresa el texto a responder."""
    global _pendiente
    with _candado:
        _pendiente = {"accion": accion, "cancelado": al_cancelar, "hora": time.time()}


def hay_pendiente() -> bool:
    with _candado:
        return _pendiente is not None and time.time() - _pendiente["hora"] < _ESPERA_MAXIMA


def cancelar():
    global _pendiente
    with _candado:
        _pendiente = None


def clasificar(texto: str):
    """'si', 'no' o None."""
    t = _limpio(texto)
    if _NO.match(t):
        return "no"
    palabras = t.split()
    if palabras and len(palabras) <= 6 and all(p in _PALABRAS_SI for p in palabras) \
            and any(p not in {"por", "favor", "de", "it", "do", "go", "ya"} for p in palabras):
        return "si"
    return None


def resolver(texto: str):
    """Si hay algo pendiente y el texto lo contesta, regresa la respuesta; si no, None."""
    global _pendiente
    if not hay_pendiente():
        cancelar()
        return None
    decision = clasificar(texto)
    with _candado:
        pendiente, _pendiente = _pendiente, None  # se resuelva o no, ya no queda pendiente
    if decision == "si":
        return pendiente["accion"]()
    if decision == "no":
        return pendiente["cancelado"]
    return None
