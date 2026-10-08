"""Groq: IA gratuita y muy rápida para conversar cuando no hay clave de Anthropic."""
from unittest import mock

import pytest

import cerebro
import config
import gemini
import groq_ia


class Resp:
    def __init__(self, codigo, datos):
        self.status_code, self._datos, self.text = codigo, datos, str(datos)

    def json(self):
        return self._datos


def ok(texto):
    return Resp(200, {"choices": [{"message": {"content": texto}}]})


@pytest.fixture
def solo_groq(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "clave-groq")
    monkeypatch.setattr(config, "GROQ_MODELO", "openai/gpt-oss-120b")
    monkeypatch.setattr(groq_ia, "_modelo_que_funciona", None)
    post = mock.MagicMock(return_value=ok("Hola desde Groq."))
    monkeypatch.setattr(groq_ia.requests, "post", post)
    monkeypatch.setattr(groq_ia.requests, "get", mock.MagicMock(side_effect=OSError("sin red")))
    return post


def test_prioridades(monkeypatch):
    for k, v in (("ANTHROPIC_API_KEY", ""), ("GROQ_API_KEY", "g"), ("GEMINI_API_KEY", "m")):
        monkeypatch.setattr(config, k, v)
    assert cerebro.proveedor() == "groq"                 # texto: la gratuita más rápida
    assert cerebro.proveedor(con_imagen=True) == "gemini"  # imágenes: Gemini
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "a")
    assert cerebro.proveedor() == cerebro.proveedor(con_imagen=True) == "claude"


def test_conversacion_con_groq(solo_groq):
    assert cerebro.preguntar("hola") == "Hola desde Groq."
    datos = solo_groq.call_args.kwargs["json"]
    assert datos["messages"][0]["role"] == "system"
    assert datos["messages"][-1] == {"role": "user", "content": "hola"}
    assert datos["reasoning_effort"] == "low"  # gpt-oss razona poco para contestar rápido
    assert solo_groq.call_args.kwargs["headers"]["Authorization"] == "Bearer clave-groq"


def test_pantalla_sin_gemini_avisa(solo_groq):
    assert "Gemini" in cerebro.analizar_imagen(b"jpg", "¿qué ves?")
    solo_groq.assert_not_called()


def test_pantalla_con_groq_y_gemini_usa_gemini(solo_groq, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "m")
    monkeypatch.setattr(gemini, "completar", mock.MagicMock(return_value="Veo VS Code."))
    assert cerebro.analizar_imagen(b"jpg", "¿qué ves?") == "Veo VS Code."
    solo_groq.assert_not_called()


def test_si_groq_falla_responde_gemini(solo_groq, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "m")
    solo_groq.return_value = Resp(503, {"error": {"message": "over capacity"}})
    monkeypatch.setattr(gemini, "completar", mock.MagicMock(return_value="Respondió Gemini."))
    assert cerebro.preguntar("hola") == "Respondió Gemini."


def test_modelo_que_falla_pasa_al_siguiente_y_lo_recuerda(solo_groq):
    solo_groq.side_effect = [Resp(400, {"error": {"message": "model decommissioned"}}), ok("uno"), ok("dos")]
    groq_ia.completar("s", [{"role": "user", "content": "x"}])
    groq_ia.completar("s", [{"role": "user", "content": "y"}])
    usados = [c.kwargs["json"]["model"] for c in solo_groq.call_args_list]
    assert usados[0] == "openai/gpt-oss-120b" and usados[1] == usados[2] != usados[0]


def test_lento_pasa_al_siguiente(solo_groq):
    solo_groq.side_effect = [groq_ia.requests.Timeout(), ok("rápido")]
    assert groq_ia.completar("s", [{"role": "user", "content": "x"}]) == "rápido"


def test_busca_modelos_disponibles_si_todos_fallan(solo_groq, monkeypatch):
    lista = Resp(200, {"data": [{"id": "whisper-large-v3"}, {"id": "llama-nuevo"}]})
    monkeypatch.setattr(groq_ia.requests, "get", mock.MagicMock(return_value=lista))
    solo_groq.side_effect = [Resp(404, {})] * 3 + [ok("con el modelo nuevo")]
    assert groq_ia.completar("s", [{"role": "user", "content": "x"}]) == "con el modelo nuevo"
    assert solo_groq.call_args.kwargs["json"]["model"] == "llama-nuevo"  # whisper no es de chat


def test_limite_y_clave_invalida(solo_groq):
    solo_groq.return_value = Resp(429, {})
    assert "límite gratuito de Groq" in cerebro.preguntar("hola")
    solo_groq.return_value = Resp(401, {"error": {"message": "Invalid API Key"}})
    assert "no es válida" in cerebro.preguntar("hola")
