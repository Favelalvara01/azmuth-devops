"""DeepSeek (de pago) y el orden de respaldo entre IAs: Claude > DeepSeek > Groq > Gemini."""
from unittest import mock

import pytest

import cerebro
import config
import deepseek_ia
import groq_ia


class Resp:
    def __init__(self, codigo, datos):
        self.status_code, self._datos, self.text = codigo, datos, str(datos)

    def json(self):
        return self._datos


def ok(texto):
    return Resp(200, {"choices": [{"message": {"content": texto}}]})


@pytest.fixture
def claves(monkeypatch):
    def poner(**k):
        for nombre in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"):
            monkeypatch.setattr(config, nombre, k.get(nombre.split("_")[0].lower(), ""))
    monkeypatch.setattr(config, "DEEPSEEK_MODELO", "deepseek-flash")
    monkeypatch.setattr(deepseek_ia, "_modelo_que_funciona", None)
    monkeypatch.setattr(groq_ia, "_modelo_que_funciona", None)
    monkeypatch.setattr(deepseek_ia.requests, "get", mock.MagicMock(side_effect=OSError("sin red")))
    monkeypatch.setattr(groq_ia.requests, "get", mock.MagicMock(side_effect=OSError("sin red")))
    return poner


def test_orden_de_preferencia(claves):
    claves(deepseek="d", groq="g", gemini="m")
    assert cerebro.proveedores() == ["deepseek", "groq", "gemini"]
    assert cerebro.proveedor(con_imagen=True) == "gemini"
    assert cerebro.descripcion_ia() == "DeepSeek → Groq → Gemini (pantalla: Gemini)"
    claves(anthropic="a", deepseek="d")
    assert cerebro.proveedor() == "claude"


def test_conversa_con_deepseek(claves, monkeypatch):
    claves(deepseek="clave-ds")
    post = mock.MagicMock(return_value=ok("Hola desde DeepSeek."))
    monkeypatch.setattr(deepseek_ia.requests, "post", post)
    assert cerebro.preguntar("hola") == "Hola desde DeepSeek."
    datos = post.call_args.kwargs["json"]
    assert datos["model"] == "deepseek-flash" and datos["thinking"] == {"type": "disabled"}
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer clave-ds"
    assert post.call_args.args[0] == "https://api.deepseek.com/chat/completions"


def test_si_no_acepta_thinking_repite_sin_eso(claves, monkeypatch):
    claves(deepseek="d")
    post = mock.MagicMock(side_effect=[Resp(400, {"error": {"message": "unknown field thinking"}}), ok("listo")])
    monkeypatch.setattr(deepseek_ia.requests, "post", post)
    assert deepseek_ia.completar("s", [{"role": "user", "content": "x"}]) == "listo"
    assert "thinking" not in post.call_args.kwargs["json"]


def test_modelo_retirado_pasa_al_siguiente(claves, monkeypatch):
    claves(deepseek="d")
    post = mock.MagicMock(side_effect=[Resp(404, {"error": {"message": "Model Not Exist"}}), ok("con otro")])
    monkeypatch.setattr(deepseek_ia.requests, "post", post)
    assert deepseek_ia.completar("s", [{"role": "user", "content": "x"}]) == "con otro"
    assert post.call_args.kwargs["json"]["model"] == "deepseek-v4-pro"


def test_sin_saldo_pasa_a_groq(claves, monkeypatch):
    claves(deepseek="d", groq="g")
    sin_saldo = Resp(402, {"error": {"message": "Insufficient Balance"}})
    monkeypatch.setattr(deepseek_ia.requests, "post", mock.MagicMock(return_value=sin_saldo))
    monkeypatch.setattr(groq_ia.requests, "post", mock.MagicMock(return_value=ok("Respondió Groq.")))
    assert cerebro.preguntar("hola") == "Respondió Groq."


def test_clave_de_claude_mala_pasa_a_groq(claves, monkeypatch):
    """El caso del amigo: ANTHROPIC con clave inválida → antes salía 'invalid x-api-key'."""
    claves(anthropic="mala", groq="g")
    cliente = mock.MagicMock()
    cliente.messages.create.side_effect = RuntimeError("Error code: 401 invalid x-api-key")
    monkeypatch.setattr(cerebro, "_obtener_cliente", lambda: cliente)
    monkeypatch.setattr(groq_ia.requests, "post", mock.MagicMock(return_value=ok("Hola, soy Groq.")))
    assert cerebro.preguntar("hola") == "Hola, soy Groq."


def test_si_fallan_todas_dice_por_que(claves, monkeypatch):
    claves(deepseek="d", groq="g")
    monkeypatch.setattr(deepseek_ia.requests, "post", mock.MagicMock(return_value=Resp(401, {"error": {"message": "bad key"}})))
    monkeypatch.setattr(groq_ia.requests, "post", mock.MagicMock(return_value=Resp(429, {})))
    respuesta = cerebro.preguntar("hola")
    assert "DeepSeek" in respuesta and "Groq" in respuesta


@pytest.mark.parametrize("valor, esperado", [
    ("tu_clave_de_anthropic_aqui", ""), ("tu_token_de_ngrok_aqui", ""), ("tu-dominio-fijo.ngrok-free.dev", ""),
    ("tu_clave_de_elevenlabs_aqui", ""), ("  gsk_abc123  ", "gsk_abc123"), ("", ""),
])
def test_textos_de_ejemplo_cuentan_como_vacios(valor, esperado, monkeypatch):
    monkeypatch.setenv("CLAVE_PRUEBA", valor)
    assert config._clave("CLAVE_PRUEBA") == esperado
