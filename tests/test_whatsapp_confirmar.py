"""WhatsApp: Azmuth lee el mensaje, pregunta "¿Lo envío?" y solo con un "sí" lo envía."""
import time
from unittest import mock

import pytest

import confirmaciones
import main
import skills
from skills import contactos, web


@pytest.fixture
def whatsapp_app(monkeypatch):
    """Simula WhatsApp de escritorio: se abre y su ventana queda al frente."""
    abiertos, enter = [], mock.MagicMock()
    monkeypatch.setattr(web, "_abrir_whatsapp", lambda numero, mensaje: abiertos.append((numero, mensaje)) or "app")
    monkeypatch.setattr(web, "_ventana_whatsapp_al_frente", lambda segundos=15: True)
    monkeypatch.setattr(web.time, "sleep", lambda s: None)
    import pyautogui
    monkeypatch.setattr(pyautogui, "press", enter)
    contactos.intentar("guarda el contacto de Jesús como 6561234567")
    return abiertos, enter


def test_lee_el_mensaje_y_pregunta(whatsapp_app):
    abiertos, enter = whatsapp_app
    respuesta, skill = skills.procesar("mándale un whatsapp a Jesús que diga Voy en camino")
    assert respuesta == "Le voy a mandar a Jesús: «Voy en camino». ¿Lo envío?" and skill == "web"
    assert abiertos == [] and not enter.called and confirmaciones.hay_pendiente()


@pytest.mark.parametrize("si", ["sí", "Sí, envíalo", "dale", "mándalo", "sí por favor", "yes"])
def test_con_si_lo_envia(whatsapp_app, si):
    abiertos, enter = whatsapp_app
    skills.procesar("mándale un whatsapp a Jesús que diga Voy en camino")
    respuesta, skill = skills.procesar(si)
    assert respuesta == "Listo, le envié el WhatsApp a Jesús." and skill == "confirmacion"
    assert abiertos == [("5216561234567", "Voy en camino")]
    enter.assert_called_once_with("enter")
    assert not confirmaciones.hay_pendiente()


@pytest.mark.parametrize("no", ["no", "cancela", "mejor no", "no lo envíes"])
def test_con_no_no_envia(whatsapp_app, no):
    abiertos, enter = whatsapp_app
    skills.procesar("mándale un whatsapp a Jesús que diga hola")
    assert skills.procesar(no)[0] == "Listo, no envié el mensaje."
    assert abiertos == [] and not enter.called


def test_otra_cosa_cancela_y_se_atiende_normal(whatsapp_app):
    abiertos, enter = whatsapp_app
    skills.procesar("mándale un whatsapp a Jesús que diga hola")
    respuesta, skill = skills.procesar("qué hora es")
    assert skill == "tiempo" and respuesta.startswith("Son las")
    assert skills.procesar("sí")[1] != "confirmacion"  # un "sí" después ya no envía nada
    assert abiertos == [] and not enter.called


def test_si_a_medias_no_envia(whatsapp_app):
    abiertos, enter = whatsapp_app
    skills.procesar("mándale un whatsapp a Jesús que diga hola")
    skills.procesar("sí pero cámbiale el mensaje")
    assert abiertos == [] and not enter.called


def test_la_pregunta_caduca(whatsapp_app, monkeypatch):
    abiertos, enter = whatsapp_app
    skills.procesar("mándale un whatsapp a Jesús que diga hola")
    ahora = time.time()
    monkeypatch.setattr(confirmaciones.time, "time", lambda: ahora + 200)
    skills.procesar("sí")
    assert abiertos == [] and not enter.called


def test_sin_ventana_al_frente_no_presiona_enter(whatsapp_app, monkeypatch):
    abiertos, enter = whatsapp_app
    monkeypatch.setattr(web, "_ventana_whatsapp_al_frente", lambda segundos=15: False)
    skills.procesar("mándale un whatsapp a Jesús que diga hola")
    assert "presione Enter" in skills.procesar("sí")[0]
    assert not enter.called  # nunca teclea en otra ventana


def test_abrir_chat_sin_mensaje_no_pregunta(whatsapp_app):
    abiertos, _ = whatsapp_app
    assert skills.procesar("abre whatsapp con Jesús")[0] == "Le abro la conversación con jesús."
    assert not confirmaciones.hay_pendiente()


def test_por_voz_escucha_la_respuesta_sin_palabra_clave(whatsapp_app, monkeypatch):
    """Dice el comando con la palabra clave y luego contesta "sí" a secas."""
    abiertos, enter = whatsapp_app
    dichos = []
    monkeypatch.setattr(main.voice, "hablar", dichos.append)
    monkeypatch.setattr(main.time, "sleep", lambda s: None)
    monkeypatch.setattr(main, "escuchar", lambda *a, **k: "sí")
    assert main.atender(f"{main.PALABRA_CLAVE} mándale un whatsapp a Jesús que diga ya llegué", None, None)
    assert dichos == ["Le voy a mandar a Jesús: «Ya llegué». ¿Lo envío?", "Listo, le envié el WhatsApp a Jesús."]
    enter.assert_called_once_with("enter")


def test_por_voz_si_no_contesta_no_envia(whatsapp_app, monkeypatch):
    abiertos, enter = whatsapp_app
    dichos = []
    monkeypatch.setattr(main.voice, "hablar", dichos.append)
    monkeypatch.setattr(main.time, "sleep", lambda s: None)
    monkeypatch.setattr(main, "escuchar", lambda *a, **k: None)
    main.atender(f"{main.PALABRA_CLAVE} mándale un whatsapp a Jesús que diga hola", None, None)
    assert dichos[-1] == "No escuché su respuesta, así que no lo envié."
    assert abiertos == [] and not enter.called
