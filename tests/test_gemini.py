"""Alternativa gratuita: Google Gemini cuando no hay clave de Anthropic."""
from unittest import mock

import pytest

import cerebro
import config
import gemini


class Resp:
    def __init__(self, codigo, datos):
        self.status_code, self._datos, self.text = codigo, datos, str(datos)

    def json(self):
        return self._datos


def ok(texto):
    return Resp(200, {"candidates": [{"content": {"parts": [{"text": "pensando…", "thought": True}, {"text": texto}]}}]})


@pytest.fixture
def solo_gemini(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "clave-gemini")
    monkeypatch.setattr(config, "GEMINI_MODELO", "gemini-flash-latest")
    post = mock.MagicMock(return_value=ok("Hola, soy Azmuth con Gemini."))
    monkeypatch.setattr(gemini.requests, "post", post)
    return post


def test_proveedor_elige_bien(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "a")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "g")
    assert cerebro.proveedor() == "claude"          # Claude tiene prioridad
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    assert cerebro.proveedor() == "gemini"
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    assert cerebro.proveedor() is None


def test_sin_ninguna_clave_avisa(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    assert "GEMINI_API_KEY" in cerebro.preguntar("hola")


def test_conversacion_con_gemini(solo_gemini):
    assert cerebro.preguntar("hola") == "Hola, soy Azmuth con Gemini."
    cuerpo = solo_gemini.call_args.kwargs["json"]
    assert cuerpo["contents"][-1] == {"role": "user", "parts": [{"text": "hola"}]}
    assert "AZMUTH" in cuerpo["systemInstruction"]["parts"][0]["text"]
    assert solo_gemini.call_args.kwargs["headers"]["x-goog-api-key"] == "clave-gemini"


def test_historial_se_convierte_a_roles_de_gemini():
    cuerpo = gemini.convertir("sys", [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}], 100)
    assert [c["role"] for c in cuerpo["contents"]] == ["user", "model"]
    assert cuerpo["generationConfig"]["maxOutputTokens"] > 100


def test_pantalla_manda_la_imagen_a_gemini(solo_gemini):
    cerebro.analizar_imagen(b"jpg", "¿qué ves?")
    partes = solo_gemini.call_args.kwargs["json"]["contents"][0]["parts"]
    assert partes[0]["inline_data"]["mime_type"] == "image/jpeg" and partes[1]["text"] == "¿qué ves?"


def test_si_el_modelo_no_existe_usa_el_de_respaldo(solo_gemini):
    solo_gemini.side_effect = [Resp(404, {"error": {"message": "not found"}}), ok("respaldo")]
    assert gemini.completar("s", [{"role": "user", "content": "x"}]) == "respaldo"
    assert "gemini-2.5-flash" in solo_gemini.call_args.args[0]


def test_limite_gratuito_da_mensaje_claro(solo_gemini):
    solo_gemini.return_value = Resp(429, {})
    assert "límite gratuito" in cerebro.preguntar("hola")


def test_respuesta_bloqueada(solo_gemini):
    solo_gemini.return_value = Resp(200, {"promptFeedback": {"blockReason": "SAFETY"}})
    assert "SAFETY" in cerebro.preguntar("hola")


def test_traduccion_y_apps_tambien_usan_gemini(solo_gemini):
    solo_gemini.return_value = ok("Opening paint.")
    cerebro._cache_traducciones.clear()
    assert cerebro.traducir("Abriendo paint.") == "Opening paint."
    from skills import apps_instaladas
    solo_gemini.return_value = ok("Discord")
    app, consultada = apps_instaladas.elegir_con_ia("discor", [(0.6, {"nombre": "Discord"})])
    assert consultada and app["nombre"] == "Discord"
