"""
PRUEBAS DE INTEGRACIÓN (automatizadas)
======================================
Verifican que VARIOS módulos funcionan bien JUNTOS: que los datos pasan
correctamente de uno a otro. En Azmuth el flujo integrado es:

   servidor.py (API)  ->  nucleo.py  ->  skills/ (enrutador)  ->  basedatos.py (SQLite)
                                     \\->  cerebro.py (IA)    ->  memoria / chats

Estrategia: integración incremental "de abajo hacia arriba" (bottom-up):
primero skills + base de datos, luego núcleo + chats, luego API completa.
Solo la IA externa se sustituye por un doble (mock) para no gastar créditos.

Ejecutar:  py -3.13 -m pytest -m integracion -v
"""
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import cerebro
import chats
import config
import nucleo
import servidor
from basedatos import conectar
from skills import memoria

pytestmark = pytest.mark.integracion


@pytest.fixture
def ia_simulada(monkeypatch):
    """Doble de la IA: Claude 'responde' sin conectarse a internet."""
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    monkeypatch.setattr(cerebro, "completar", lambda system, mensajes, max_tokens:
                        "Claro, señor. [MEMORIA: estudia en la UTCJ]")
    cerebro.borrar_historial()


def test_cp_int_01_enrutador_skill_y_base_de_datos():
    """CP-INT-01: skills.procesar() -> notas -> SQLite (los datos quedan en la tabla)."""
    respuesta, skill = nucleo.responder("toma nota: estudiar pruebas de integración")
    assert skill == "notas" and "Nota guardada" in respuesta
    with conectar() as con:
        filas = [f["texto"] for f in con.execute("SELECT texto FROM notas")]
    assert filas == ["estudiar pruebas de integración"]


def test_cp_int_02_nucleo_registra_el_habito_del_comando():
    """CP-INT-02: nucleo -> skill -> habitos: cada comando suma al conteo de hábitos."""
    nucleo.responder("qué hora es")
    nucleo.responder("qué hora es")
    with conectar() as con:
        fila = con.execute("SELECT conteo FROM habitos_categorias WHERE categoria = 'tiempo'").fetchone()
    assert fila["conteo"] == 2


def test_cp_int_03_nucleo_ia_y_memoria(ia_simulada):
    """CP-INT-03: sin skill -> cerebro (IA) -> la etiqueta [MEMORIA] se guarda en la BD."""
    respuesta, categoria = nucleo.responder("hola, ¿cómo estás?")
    assert categoria == "ia" and respuesta == "Claro, señor."
    assert "estudia en la UTCJ" in memoria.recordar_todo()


def test_cp_int_04_chat_guarda_pregunta_y_respuesta():
    """CP-INT-04: nucleo.responder_en_chat() -> chats: se guardan ambos mensajes."""
    respuesta, categoria, chat_id = nucleo.responder_en_chat("mis notas")
    mensajes = chats.obtener_mensajes(chat_id)
    assert [m["rol"] for m in mensajes] == ["user", "assistant"]
    assert mensajes[1]["texto"] == respuesta and categoria == "notas"


def test_cp_int_05_respaldo_entre_ias(monkeypatch):
    """CP-INT-05: si Claude falla, cerebro pasa automáticamente a la siguiente IA (Groq)."""
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "a")
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "g")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    llamadas = []

    def falso(nombre, system, mensajes, max_tokens):
        llamadas.append(nombre)
        if nombre == "claude":
            raise RuntimeError("sin saldo")
        return "respuesta de Groq"

    monkeypatch.setattr(cerebro, "_con", falso)
    assert cerebro.completar("sys", [{"role": "user", "content": "hola"}], 50) == "respuesta de Groq"
    assert llamadas == ["claude", "groq"]


def test_cp_int_06_api_nucleo_skill_bd():
    """CP-INT-06: POST /chats/{id}/mensajes atraviesa API -> núcleo -> skill -> BD."""
    cliente = TestClient(servidor.app)
    with mock.patch.object(servidor, "_hablar_en_segundo_plano"):
        chat_id = cliente.post("/chats").json()["id"]
        r = cliente.post(f"/chats/{chat_id}/mensajes", json={"texto": "toma nota: integrar la API"})
    assert r.status_code == 200 and r.json()["categoria"] == "notas"
    mensajes = cliente.get(f"/chats/{chat_id}/mensajes").json()["mensajes"]
    assert mensajes[0]["texto"] == "toma nota: integrar la API"


def test_cp_int_07_una_skill_que_falla_no_tumba_el_chat(monkeypatch):
    """CP-INT-07 (regresión DEF-022): si una skill lanza un error, el enrutador lo registra
    en monitoreo y el chat contesta un aviso en lugar de un error 500."""
    import monitoreo
    from skills import multimedia
    monkeypatch.setattr(multimedia, "intentar", mock.MagicMock(side_effect=RuntimeError("sin pantalla")))
    respuesta, categoria, _ = nucleo.responder_en_chat("volumen a 40")
    assert categoria == "multimedia" and "No pude completar eso" in respuesta
    assert monitoreo.resumen()["ultimos_errores"][-1]["origen"] == "skill multimedia"
