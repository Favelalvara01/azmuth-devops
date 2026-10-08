"""
Skill: pantalla — "¿qué hay en mi pantalla?"

Toma una captura del monitor principal y se la manda a Claude (visión) junto
con lo que preguntaste: "mira mi pantalla y dime qué error tiene",
"léeme lo que dice la pantalla", "explícame lo que tengo en pantalla".

Privacidad: la captura NO se guarda en disco; solo viaja en memoria a la API
de Anthropic para esa pregunta. Se reduce a 1568 px y JPEG para que sea
rápida y barata.
"""
import io
import re

import estado

_PANTALLA = r"(?:mi\s+|la\s+|esta\s+)?pantalla"
_DISPARADORES = re.compile(
    r"\b(?:"
    r"qu[eé]\s+(?:hay|ves|tengo|sale|aparece|dice)\s+(?:en\s+)?" + _PANTALLA +
    r"|(?:mira|lee|leeme|léeme|revisa|analiza|checa|explica|explicame|explícame|describe|"
    r"ayuda|ayudame|ayúdame|resuelve|resuelveme|corrige|traduce|traduceme|resume|resumeme)\s+"
    r"(?:(?:con|en)\s+)?(?:lo\s+que\s+(?:hay|tengo|dice|sale|aparece)\s+en\s+)?(?:(?:lo\s+)?de\s+)?" + _PANTALLA +
    r"|lo\s+que\s+(?:hay|tengo|dice|sale|aparece)\s+en\s+" + _PANTALLA +
    r"|(?:ves|puedes\s+ver)\s+" + _PANTALLA +
    r")\b"
)
_PREGUNTA_GENERICA = "Describe brevemente qué hay en mi pantalla y qué estoy haciendo."
_LADO_MAX = 1568


def es_pregunta_de_pantalla(texto: str) -> bool:
    return bool(_DISPARADORES.search((texto or "").lower()))


def capturar() -> bytes:
    """Captura el monitor principal y la devuelve como JPEG reducido."""
    from PIL import ImageGrab
    imagen = ImageGrab.grab()
    return preparar(imagen)


def preparar(imagen) -> bytes:
    imagen = imagen.convert("RGB")
    imagen.thumbnail((_LADO_MAX, _LADO_MAX))
    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", quality=80)
    return salida.getvalue()


def _pregunta(texto: str) -> str:
    resto = _DISPARADORES.sub("", texto.lower()).strip(" ,.?¿!¡y")
    return texto.strip() if len(resto) > 3 else _PREGUNTA_GENERICA


def intentar(texto: str):
    if not es_pregunta_de_pantalla(texto):
        return None
    import cerebro  # import tardío: cerebro importa skills
    try:
        estado.set_estado("procesando", "Mirando su pantalla...")
        imagen = capturar()
    except ImportError:
        return ("No pude tomar la captura: falta la librería Pillow en el Python con el que corre Azmuth. "
                "Instálela con: python -m pip install Pillow")
    except Exception as e:
        return f"No pude tomar la captura de pantalla: {e}"
    return cerebro.analizar_imagen(imagen, _pregunta(texto), modo=estado.obtener_modo())
