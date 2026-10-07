from types import SimpleNamespace
from unittest import mock

from fastapi.testclient import TestClient

import cerebro
import config
import estado
import servidor
from skills import memoria


# ---------- estado.py (núcleo visual) ----------
def test_estado_valido_e_invalido():
    estado.set_estado("escuchando", "x" * 300)
    e = estado.obtener_estado()
    assert e["estado"] == "escuchando" and len(e["detalle"]) == 120
    estado.set_estado("bailando")
    assert estado.obtener_estado()["estado"] == "reposo"


def test_log_se_recorta_pero_el_contador_solo_crece():
    antes = estado.obtener_estado()["log_total"]
    for i in range(estado._MAX_HISTORIAL + 10):
        estado.log(f"linea {i}")
    e = estado.obtener_estado()
    assert len(e["log"]) == estado._MAX_HISTORIAL
    assert e["log_total"] == antes + estado._MAX_HISTORIAL + 10


# ---------- servidor.py (API FastAPI) ----------
cliente = TestClient(servidor.app)


def test_endpoint_raiz_sirve_la_interfaz():
    r = cliente.get("/")
    assert r.status_code == 200 and "<html" in r.text.lower()


def test_endpoint_estado():
    r = cliente.get("/estado")
    assert r.status_code == 200 and set(r.json()) >= {"estado", "detalle", "log", "log_total"}


def test_endpoint_comando_conocido():
    r = cliente.get("/comando", params={"accion": "PLAY_PAUSE"})
    assert r.json() == {"status": "ok", "mensaje": "Play / Pausa"}


def test_endpoint_comando_sin_parametro():
    assert cliente.get("/comando").status_code == 422


# ---------- cerebro.py (IA: Claude) ----------
def test_extraer_memoria_automatica():
    limpio = cerebro._extraer_y_guardar_memoria("¡Claro, señor!\n[MEMORIA: estudia DSM en la UTCJ]")
    assert limpio == "¡Claro, señor!"
    assert memoria.recordar_todo() == ["estudia DSM en la UTCJ"]


def test_sin_clave_responde_aviso(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    assert "No tengo configurada mi clave" in cerebro.preguntar("hola")


def test_preguntar_con_claude_simulado(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    falso = mock.MagicMock()
    falso.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Buenas tardes. [MEMORIA: le gusta el béisbol]")]
    )
    monkeypatch.setattr(cerebro, "_cliente", falso)
    cerebro.borrar_historial()
    assert cerebro.preguntar("hola, me encanta el béisbol") == "Buenas tardes."
    kwargs = falso.messages.create.call_args.kwargs
    assert kwargs["model"] == config.MODELO_CLAUDE
    assert "le gusta el béisbol" in memoria.recordar_todo()


def test_error_de_red_con_claude_no_truena(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    falso = mock.MagicMock()
    falso.messages.create.side_effect = RuntimeError("timeout")
    monkeypatch.setattr(cerebro, "_cliente", falso)
    assert "Tuve un problema conectando" in cerebro.preguntar("hola")


def test_modelo_configurado_no_es_uno_retirado():
    """Regresión DEF-010: el modelo claude-3-5-sonnet-20241022 fue retirado y daba 404."""
    assert "20241022" not in config.MODELO_CLAUDE
