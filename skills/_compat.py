"""
Compatibilidad para cuando Azmuth corre SIN Windows ni pantalla (contenedor
Docker / VM Ubuntu Server de la hiperconvergencia).

DEF-022 (pruebas de API en la VM): skills/multimedia.py y skills/pestanas.py
hacían "import pyautogui" al cargarse; en Linux sin pantalla esa librería no
existe y CUALQUIER mensaje del chat escrito respondía error 500, aunque fuera
"toma nota". Ahora se usa este sustituto: solo fallan (con un aviso claro)
los comandos que de verdad necesitan teclado o ventanas.
"""


class SinPantalla:
    """Se hace pasar por pyautogui / pygetwindow y avisa al usarse."""

    def __init__(self, nombre: str):
        self._nombre = nombre

    def __getattr__(self, atributo):
        def _no_disponible(*args, **kwargs):
            raise RuntimeError(f"{self._nombre}.{atributo} necesita Windows con pantalla")
        return _no_disponible


def cargar_pyautogui():
    try:
        import pyautogui
        return pyautogui
    except Exception:  # ImportError o KeyError('DISPLAY') en Linux sin pantalla
        return SinPantalla("pyautogui")
