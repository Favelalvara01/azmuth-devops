"""Skill pantalla: '¿qué hay en mi pantalla?' con visión de Claude."""
import base64
from unittest import mock

import pytest
from PIL import Image

import cerebro
import skills
from skills import pantalla


@pytest.mark.parametrize("frase", [
    "qué hay en mi pantalla", "¿Qué ves en la pantalla?", "mira mi pantalla y dime qué error tiene",
    "léeme lo que dice la pantalla", "explícame lo que tengo en pantalla", "puedes ver mi pantalla",
    "ayúdame con lo que hay en mi pantalla", "ayúdame con mi pantalla", "resuelve lo de mi pantalla",
    "traduce lo que dice mi pantalla", "dime lo que aparece en la pantalla"])
def test_detecta_preguntas_de_pantalla(frase):
    assert pantalla.es_pregunta_de_pantalla(frase)


@pytest.mark.parametrize("frase", ["sube el brillo de la pantalla", "baja el brillo de mi pantalla", "qué hora es", "abre paint",
                                   "ayúdame con mi tarea"])
def test_no_confunde_otras_frases(frase):
    assert not pantalla.es_pregunta_de_pantalla(frase)


def test_preparar_reduce_y_convierte_a_jpeg():
    datos = pantalla.preparar(Image.new("RGBA", (3840, 2160), "blue"))
    assert datos[:3] == b"\xff\xd8\xff"  # cabecera JPEG
    img = Image.open(__import__("io").BytesIO(datos))
    assert max(img.size) == 1568


@pytest.fixture
def captura_falsa(monkeypatch):
    monkeypatch.setattr(pantalla, "capturar", lambda: b"JPEG")
    analizar = mock.MagicMock(return_value="Veo Visual Studio Code con un error de sintaxis.")
    monkeypatch.setattr(cerebro, "analizar_imagen", analizar)
    return analizar


def test_pregunta_generica(captura_falsa):
    respuesta, categoria = skills.procesar("¿qué hay en mi pantalla?")
    assert "Visual Studio Code" in respuesta and categoria == "pantalla"
    imagen, pregunta = captura_falsa.call_args.args
    assert imagen == b"JPEG" and pregunta == pantalla._PREGUNTA_GENERICA


def test_pregunta_especifica_se_respeta(captura_falsa):
    skills.procesar("mira mi pantalla y dime qué error tiene el código")
    assert "error" in captura_falsa.call_args.args[1]


def test_usa_el_modo_actual(captura_falsa, monkeypatch):
    monkeypatch.setattr(pantalla.estado, "obtener_modo", lambda: "escritorio")
    pantalla.intentar("qué hay en mi pantalla")
    assert captura_falsa.call_args.kwargs["modo"] == "escritorio"


def test_falla_la_captura(monkeypatch):
    def falla():
        raise OSError("sin monitor")
    monkeypatch.setattr(pantalla, "capturar", falla)
    assert "No pude tomar la captura" in pantalla.intentar("qué hay en mi pantalla")


def test_analizar_imagen_manda_bloque_de_imagen(monkeypatch):
    monkeypatch.setattr(cerebro.config, "ANTHROPIC_API_KEY", "x")
    cliente = mock.MagicMock()
    cliente.messages.create.return_value.content = [mock.MagicMock(type="text", text="Una terminal.")]
    monkeypatch.setattr(cerebro, "_obtener_cliente", lambda: cliente)
    assert cerebro.analizar_imagen(b"abc", "¿qué ves?") == "Una terminal."
    contenido = cliente.messages.create.call_args.kwargs["messages"][0]["content"]
    assert contenido[0]["source"]["data"] == base64.b64encode(b"abc").decode()
    assert cliente.messages.create.call_args.kwargs["max_tokens"] == 400


def test_analizar_imagen_sin_clave(monkeypatch):
    monkeypatch.setattr(cerebro.config, "ANTHROPIC_API_KEY", "")
    assert "clave" in cerebro.analizar_imagen(b"x", "?")
