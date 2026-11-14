"""
PRUEBAS DE ACEPTACIÓN (automatizadas)
=====================================
Comprueban que Azmuth cumple lo que el USUARIO pidió, escritas a partir de
las historias de usuario de los sprints (metricas/datos/sprints.csv) con el
formato de criterios de aceptación BDD:

    DADO   (contexto inicial)
    CUANDO (acción del usuario)
    ENTONCES (resultado que el usuario espera ver)

Si todas pasan, la historia se considera "aceptada" (criterio de terminado).

Ejecutar:  py -3.13 -m pytest -m aceptacion -v
"""
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import config
import estado
import idioma
import nucleo
import servidor
import skills

pytestmark = pytest.mark.aceptacion


@pytest.fixture
def cliente():
    with mock.patch.object(servidor, "_hablar_en_segundo_plano"):
        yield TestClient(servidor.app)
    estado._modo_actual = "voz"
    idioma.cambiar("es", guardar=False)


def test_ca_01_hu2_guardar_y_consultar_notas_por_voz():
    """HU-02 'quiero guardar notas y recordatorios por voz'.
    DADO que no tengo notas, CUANDO digo "toma nota: comprar pan" y luego "mis notas",
    ENTONCES Azmuth confirma la nota y me la lee en la lista."""
    assert nucleo.responder("mis notas")[0] == "No tiene notas guardadas."
    assert nucleo.responder("toma nota: comprar pan")[0] == 'Nota guardada: "comprar pan".'
    assert "1. comprar pan" in nucleo.responder("mis notas")[0]


def test_ca_02_hu2_recordatorio_con_hora():
    """HU-02. DADO Azmuth activo, CUANDO digo "recuérdame entregar el reporte a las 5 pm",
    ENTONCES me confirma el texto y la hora en formato de 24 h."""
    respuesta, _ = nucleo.responder("recuérdame entregar el reporte a las 5 pm")
    assert respuesta == 'Recordatorio anotado: "entregar el reporte". Le aviso a las 17:00.'


def test_ca_03_hu8_escribirle_como_a_un_chat(cliente):
    """HU-08 'quiero escribirle a Azmuth como a una IA de chat'.
    DADO el modo escritorio, CUANDO escribo un comando en un chat nuevo,
    ENTONCES recibo la respuesta y el chat queda guardado con título automático."""
    assert cliente.post("/modo", json={"modo": "escritorio"}).json()["modo"] == "escritorio"
    chat_id = cliente.post("/chats").json()["id"]
    r = cliente.post(f"/chats/{chat_id}/mensajes", json={"texto": "qué hora es"}).json()
    assert r["respuesta"].startswith("Son las")
    chat = next(c for c in cliente.get("/chats").json()["chats"] if c["id"] == chat_id)
    assert chat["titulo"] == "qué hora es" and chat["mensajes"] == 2


def test_ca_04_hu9_escrito_funciona_igual_que_por_voz():
    """HU-09 'que los comandos escritos funcionen igual que por voz'.
    DADO que escribo sin acentos o con signos, ENTONCES responde la misma skill."""
    for frase in ("qué hora es", "que hora es", "¿Qué hora es?"):
        assert skills.procesar(frase)[1] == "tiempo"


def test_ca_05_hu10_control_remoto_protegido(monkeypatch, cliente):
    """HU-10 'proteger el control remoto'.
    DADO un TOKEN_REMOTO, CUANDO alguien sin token manda "bloquear" desde internet,
    ENTONCES se rechaza (401); CON el token, se ejecuta."""
    monkeypatch.setattr(config, "TOKEN_REMOTO", "omnitrix-2026")
    internet = {"X-Forwarded-For": "189.1.2.3"}
    assert cliente.get("/comando", params={"accion": "bloquear"}, headers=internet).status_code == 401
    ok = cliente.get("/comando", params={"accion": "bloquear"}, headers={**internet, "X-Azmuth-Token": "omnitrix-2026"})
    assert ok.json() == {"status": "ok", "mensaje": "PC bloqueada"}


def test_ca_06_hu11_azmuth_en_ingles(cliente):
    """HU-11 'que Azmuth hable inglés'.
    DADO Azmuth en español, CUANDO digo "habla en inglés",
    ENTONCES contesta en inglés y la interfaz (/estado) cambia a 'en'."""
    respuesta, skill = skills.procesar("habla en inglés")
    assert skill == "idiomas" and respuesta.startswith("Done!")
    assert cliente.get("/estado").json()["idioma"] == "en"
