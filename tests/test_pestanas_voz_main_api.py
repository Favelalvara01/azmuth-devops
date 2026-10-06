import sys
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import config
import servidor
import skills
import voice
from skills import pestanas

pyautogui = sys.modules["pyautogui"]


@pytest.mark.parametrize("frase,respuesta,teclas", [
    ("cambia de pestaña", "Cambiando a la siguiente pestaña.", ("ctrl", "tab")),
    ("pestaña anterior", "Cambiando a la pestaña anterior.", ("ctrl", "shift", "tab")),
    ("pestaña 3", "Cambiando a la pestaña 3.", ("ctrl", "3")),
    ("ve a la pestaña dos", "Cambiando a la pestaña 2.", ("ctrl", "2")),
    ("pestaña nueve", "Cambiando a la última pestaña.", ("ctrl", "9")),
    ("cierra esta pestaña", "Pestaña cerrada.", ("ctrl", "w")),
    ("nueva pestaña", "Abriendo nueva pestaña.", ("ctrl", "t")),
    ("cambia de ventana", "Alternando ventana.", ("alt", "tab")),
])
def test_pestanas(frase, respuesta, teclas):
    pyautogui.hotkey.reset_mock()
    assert pestanas.intentar(frase) == respuesta
    pyautogui.hotkey.assert_called_with(*teclas)


@pytest.mark.xfail(strict=True, reason="DEF-013: multimedia ('^siguiente') se roba 'siguiente pestaña' porque va antes que pestanas")
def test_siguiente_pestana_llega_a_pestanas():
    _, skill = skills.procesar("siguiente pestaña")
    assert skill == "pestanas"


# ---------- voice.py ----------
def test_voz_sin_clave_usa_voz_de_windows(monkeypatch):
    monkeypatch.setattr(config, "ELEVENLABS_API_KEY", "")
    with mock.patch.object(voice, "_hablar_con_windows") as reserva:
        voice.hablar("hola")
    reserva.assert_called_once_with("hola")


def test_voz_si_falla_elevenlabs_usa_reserva(monkeypatch):
    monkeypatch.setattr(config, "ELEVENLABS_API_KEY", "clave-falsa")
    monkeypatch.setitem(sys.modules, "elevenlabs", None)  # fuerza ImportError
    with mock.patch.object(voice, "_hablar_con_windows") as reserva:
        voice.hablar("hola")
    reserva.assert_called_once()


# ---------- main.procesar_comando (flujo completo sin micrófono) ----------
@pytest.fixture
def main_sin_voz(monkeypatch):
    import main
    monkeypatch.setattr(main.voice, "hablar", mock.MagicMock())
    monkeypatch.setattr(main.time, "sleep", lambda *_: None)
    return main


def test_flujo_skill_local(main_sin_voz):
    main_sin_voz.procesar_comando("Azmuth, toma nota: repasar métricas")
    main_sin_voz.voice.hablar.assert_called_with('Nota guardada: "repasar métricas".')
    assert "1. Notas" in skills.habitos.intentar("mis hábitos")


def test_flujo_app_directa(main_sin_voz):
    main_sin_voz.procesar_comando("paint")
    # "paint" a secas se convierte en "abre paint" y lo resuelve la skill aplicaciones
    dicho = main_sin_voz.voice.hablar.call_args.args[0]
    assert "paint" in dicho


def test_flujo_va_a_claude(main_sin_voz, monkeypatch):
    monkeypatch.setattr(main_sin_voz.cerebro, "preguntar", lambda t: "Respuesta de Claude")
    main_sin_voz.procesar_comando("explícame qué es DevOps")
    main_sin_voz.voice.hablar.assert_called_with("Respuesta de Claude")


# ---------- servidor: todas las acciones remotas responden ----------
ACCIONES = ["musica", "chapa", "play_pause", "next", "prev", "vol_up", "vol_down", "mute", "alt_tab",
            "nueva_pestana", "next_tab", "prev_tab", "fortnite", "roblox", "edge", "vscode", "teams",
            "cerrar_pestana", "cerrar_app", "bloquear", "task_manager", "terminal", "escritorio",
            "brillo_up", "brillo_down", "local_tunes"]


@pytest.mark.parametrize("accion", ACCIONES)
def test_acciones_remotas(accion):
    r = TestClient(servidor.app).get("/comando", params={"accion": accion})
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_accion_desconocida():
    r = TestClient(servidor.app).get("/comando", params={"accion": "volar"})
    assert r.json() == {"status": "error", "mensaje": "Comando 'volar' no reconocido"}


def test_vista_reloj():
    assert TestClient(servidor.app).get("/reloj").status_code == 200
