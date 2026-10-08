"""Idioma de Azmuth: español (por defecto) o inglés.

Afecta a todo a la vez: el reconocimiento de voz (es-MX / en-US), las
respuestas de Claude, los comandos (skills/ingles.py traduce los comandos en
inglés a los de español) y los textos de la interfaz. Se guarda en la tabla
`ajustes`, así que se conserva al reiniciar.
"""
import threading

IDIOMAS = {
    "es": {"nombre": "español", "voz": "es-MX"},
    "en": {"nombre": "English", "voz": "en-US"},
}
_actual = "es"
_candado = threading.Lock()


def obtener() -> str:
    return _actual


def es_ingles() -> bool:
    return _actual == "en"


def codigo_voz() -> str:
    return IDIOMAS[_actual]["voz"]


def t(espanol: str, ingles: str) -> str:
    """Devuelve el texto en el idioma activo."""
    return ingles if _actual == "en" else espanol


def cambiar(codigo: str, guardar: bool = True) -> str:
    global _actual
    codigo = (codigo or "").lower().strip()[:2]
    if codigo not in IDIOMAS:
        return _actual
    with _candado:
        _actual = codigo
    if guardar:
        try:
            import chats
            chats.guardar_ajuste("idioma", codigo)
        except Exception:
            pass
    return _actual


def cargar():
    """Restaura el idioma guardado (se llama al arrancar la app)."""
    try:
        import chats
        cambiar(chats.obtener_ajuste("idioma", "es"), guardar=False)
    except Exception:
        pass
    return _actual
