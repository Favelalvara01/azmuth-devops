"""
PRUEBAS DE SISTEMA (automatizadas)
==================================
Se prueba Azmuth COMPLETO, como una caja negra, desde afuera: igual que lo
usaría la interfaz de escritorio o el celular. Se levanta el servidor real
(uvicorn en un puerto libre) y se le habla por HTTP, recorriendo escenarios
de punta a punta (end-to-end). Lo único simulado es el hardware de Windows
(micrófono, teclado) y la IA externa.

Ejecutar:  py -3.13 -m pytest -m sistema -v
"""
import socket
import threading
import time
from unittest import mock

import pytest
import requests
import uvicorn

import cerebro
import config
import estado
import idioma
import servidor

pytestmark = pytest.mark.sistema


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def azmuth_en_marcha(monkeypatch):
    """Arranca el servidor REAL de Azmuth en segundo plano y regresa su URL."""
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    monkeypatch.setattr(cerebro, "completar", lambda s, m, t: "Las pruebas de sistema validan el producto completo.")
    monkeypatch.setattr(servidor, "_hablar_en_segundo_plano", mock.MagicMock())
    estado._modo_actual = "voz"
    puerto = _puerto_libre()
    srv = uvicorn.Server(uvicorn.Config(servidor.app, host="127.0.0.1", port=puerto, log_level="warning"))
    hilo = threading.Thread(target=srv.run, daemon=True)
    hilo.start()
    for _ in range(100):
        if srv.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{puerto}"
    srv.should_exit = True
    hilo.join(timeout=5)
    idioma.cambiar("es", guardar=False)
    estado._modo_actual = "voz"


def test_cp_sis_01_escenario_completo_modo_escritorio(azmuth_en_marcha):
    """CP-SIS-01: arrancar -> modo escritorio -> chat -> skill -> IA -> renombrar -> borrar."""
    url = azmuth_en_marcha
    assert requests.get(f"{url}/salud", timeout=5).json()["status"] == "ok"
    assert requests.post(f"{url}/modo", json={"modo": "escritorio"}, timeout=5).json() == {"modo": "escritorio"}

    chat_id = requests.post(f"{url}/chats", timeout=5).json()["id"]
    skill = requests.post(f"{url}/chats/{chat_id}/mensajes", json={"texto": "toma nota: entregar reporte"}, timeout=5).json()
    assert skill["categoria"] == "notas"
    ia = requests.post(f"{url}/chats/{chat_id}/mensajes", json={"texto": "¿Qué son las pruebas de sistema?"}, timeout=5).json()
    assert ia["categoria"] == "ia" and "producto completo" in ia["respuesta"]

    renombrado = requests.patch(f"{url}/chats/{chat_id}", json={"titulo": "Reporte de pruebas"}, timeout=5).json()
    assert renombrado["titulo"] == "Reporte de pruebas"
    assert len(requests.get(f"{url}/chats/{chat_id}/mensajes", timeout=5).json()["mensajes"]) == 4
    assert requests.delete(f"{url}/chats/{chat_id}", timeout=5).status_code == 200
    assert requests.get(f"{url}/chats/{chat_id}/mensajes", timeout=5).status_code == 404


def test_cp_sis_02_cambio_de_idioma_y_estado_global(azmuth_en_marcha):
    """CP-SIS-02: el cambio de idioma se refleja en todo el sistema (/estado)."""
    url = azmuth_en_marcha
    assert requests.post(f"{url}/idioma", json={"idioma": "en"}, timeout=5).json() == {"idioma": "en"}
    assert requests.get(f"{url}/estado", timeout=5).json()["idioma"] == "en"
    assert requests.post(f"{url}/idioma", json={"idioma": "es"}, timeout=5).json() == {"idioma": "es"}


def test_cp_sis_03_control_remoto_desde_el_celular(azmuth_en_marcha):
    """CP-SIS-03: la vista /reloj carga y sus botones ejecutan /comando."""
    url = azmuth_en_marcha
    assert "OMNITRIX READY" in requests.get(f"{url}/reloj", timeout=5).text
    r = requests.get(f"{url}/comando", params={"accion": "vol_up"}, timeout=5).json()
    assert r == {"status": "ok", "mensaje": "Volumen +10"}
    assert any("Volumen +10" in linea for linea in requests.get(f"{url}/estado", timeout=5).json()["log"])
