"""Pruebas del MODO ESCRITORIO: chats guardados, cambio de modo por voz,
texto o botón, respuestas con historial del chat y la API del servidor."""
from types import SimpleNamespace
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import cerebro
import chats
import config
import estado
import nucleo
import servidor
import voice
from skills import modos


@pytest.fixture(autouse=True)
def modo_voz_al_inicio():
    estado._modo_actual = "voz"
    estado._escuchas_modo.clear()
    yield
    estado._modo_actual = "voz"
    estado._escuchas_modo.clear()


@pytest.fixture
def claude_simulado(monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    falso = mock.MagicMock()
    falso.messages.create.return_value = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="**DevOps** une desarrollo y operaciones.")])
    monkeypatch.setattr(cerebro, "_cliente", falso)
    return falso


# ---------------------------------------------------------------- chats.py
def test_crear_chat_lo_deja_activo_y_titulo_automatico():
    cid = chats.crear_chat()
    assert chats.obtener_activo() == cid
    chats.agregar_mensaje(cid, "user", "Explícame cómo funciona GitHub Actions con un ejemplo de pipeline completo")
    titulo = chats.listar_chats()[0]["titulo"]
    assert titulo.startswith("Explícame cómo funciona") and titulo.endswith("…") and len(titulo) <= 49


def test_historial_para_ia_alterna_y_empieza_con_usuario():
    cid = chats.crear_chat()
    chats.agregar_mensaje(cid, "assistant", "Hola, soy Azmuth")      # no debe ir primero
    chats.agregar_mensaje(cid, "user", "uno")
    chats.agregar_mensaje(cid, "user", "dos")                       # dos seguidos se juntan
    chats.agregar_mensaje(cid, "assistant", "respuesta")
    h = chats.historial_para_ia(cid)
    assert [m["role"] for m in h] == ["user", "assistant"]
    assert h[0]["content"] == "uno\n\ndos"


def test_renombrar_y_borrar_chat():
    cid = chats.crear_chat()
    assert chats.renombrar_chat(cid, "  Tarea de métricas  ") == "Tarea de métricas"
    chats.agregar_mensaje(cid, "user", "hola")
    chats.borrar_chat(cid)
    assert not chats.existe(cid)
    assert chats.obtener_mensajes(cid) == []
    assert chats.obtener_activo(crear_si_no_hay=False) is None


def test_ajustes_persisten():
    assert chats.obtener_ajuste("modo", "voz") == "voz"
    chats.guardar_ajuste("modo", "escritorio")
    assert chats.obtener_ajuste("modo") == "escritorio"


# ------------------------------------------------------ cambio de modo
def test_set_modo_avisa_a_los_escuchas_solo_si_cambia():
    vistos = []
    estado.al_cambiar_modo(vistos.append)
    estado.set_modo("escritorio")
    estado.set_modo("escritorio")
    estado.set_modo("inventado")
    assert vistos == ["escritorio"] and estado.obtener_modo() == "escritorio"
    assert estado.obtener_estado()["modo"] == "escritorio"


@pytest.mark.parametrize("frase,modo", [
    ("modo escritorio", "escritorio"), ("cambia a modo chat", "escritorio"), ("activa el modo texto", "escritorio"),
    ("modo voz", "voz"), ("pasa a modo normal", "voz"), ("sal del modo escritorio", "voz"),
])
def test_skill_modos(frase, modo):
    estado.set_modo("voz" if modo == "escritorio" else "escritorio")
    assert modos.intentar(frase) is not None
    assert estado.obtener_modo() == modo


def test_skill_modos_no_se_roba_otras_frases():
    assert modos.intentar("busca modo escritorio de windows") is None
    assert modos.intentar("toma nota: modo escritorio") is None


# ------------------------------------------------------ nucleo + cerebro
def test_chat_con_skill_guarda_pregunta_y_respuesta():
    respuesta, categoria, cid = nucleo.responder_en_chat("toma nota: repasar PERT")
    assert categoria == "notas" and "repasar PERT" in respuesta
    assert [m["rol"] for m in chats.obtener_mensajes(cid)] == ["user", "assistant"]


def test_chat_con_ia_usa_historial_del_chat_y_modo_escritorio(claude_simulado):
    cid = chats.crear_chat()
    nucleo.responder_en_chat("¿qué es devops?", cid)
    respuesta, categoria, _ = nucleo.responder_en_chat("dame un ejemplo", cid)
    assert categoria == "ia" and "DevOps" in respuesta
    kwargs = claude_simulado.messages.create.call_args.kwargs
    assert kwargs["max_tokens"] == 2000 and "MODO ESCRITORIO" in kwargs["system"]
    assert [m["role"] for m in kwargs["messages"]] == ["user", "assistant", "user"]
    assert cerebro._historial == [] or all(m["content"] != "dame un ejemplo" for m in cerebro._historial)


def test_voz_sigue_corta_y_con_su_propio_historial(claude_simulado):
    cerebro.borrar_historial()
    cerebro.preguntar("hola")
    kwargs = claude_simulado.messages.create.call_args.kwargs
    assert kwargs["max_tokens"] == 800 and "MODO ESCRITORIO" not in kwargs["system"]
    assert len(cerebro._historial) == 2


def test_texto_para_voz_quita_markdown_y_recorta():
    md = "# Título\n**Hola** señor. Vea `x`:\n```python\nprint(1)\n```\n- uno\n- [dos](http://a.b)"
    t = voice.texto_para_voz(md)
    assert "**" not in t and "#" not in t and "print(1)" not in t and "código en pantalla" in t and "dos" in t
    largo = voice.texto_para_voz("Esta es una oración bastante larga. " * 30)
    assert largo.endswith("El resto se lo dejé en pantalla.") and len(largo) < 400


def test_voz_en_modo_escritorio_queda_en_el_chat(monkeypatch):
    import main
    monkeypatch.setattr(main.voice, "hablar", mock.MagicMock())
    monkeypatch.setattr(main.time, "sleep", lambda *_: None)
    estado.set_modo("escritorio")
    main.procesar_comando("Azmuth, toma nota: comprar café")
    mensajes = chats.obtener_mensajes(chats.obtener_activo())
    assert [(m["rol"], m["origen"]) for m in mensajes] == [("user", "voz"), ("assistant", "voz")]


# ---------------------------------------------------------- API (servidor)
cliente = TestClient(servidor.app)


def test_api_modo():
    assert cliente.get("/modo").json()["modo"] == "voz"
    assert cliente.post("/modo", json={"modo": "escritorio"}).json() == {"modo": "escritorio"}
    assert cliente.post("/modo", json={"modo": "volar"}).status_code == 400
    assert cliente.post("/voz_chat", json={"activa": False}).json() == {"voz_chat": False}
    assert cliente.get("/modo").json()["voz_chat"] is False


def test_api_chats_flujo_completo():
    chats.guardar_ajuste("voz_chat", "0")
    cid = cliente.post("/chats").json()["id"]
    r = cliente.post(f"/chats/{cid}/mensajes", json={"texto": "toma nota: entregar reporte"}).json()
    assert r["categoria"] == "notas" and r["chat_id"] == cid
    assert len(cliente.get(f"/chats/{cid}/mensajes").json()["mensajes"]) == 2
    lista = cliente.get("/chats").json()
    assert lista["activo"] == cid and lista["chats"][0]["titulo"] == "toma nota: entregar reporte"
    assert cliente.patch(f"/chats/{cid}", json={"titulo": "Pendientes"}).json() == {"titulo": "Pendientes"}
    assert cliente.post(f"/chats/{cid}/activar").json() == {"activo": cid}
    assert cliente.post(f"/chats/{cid}/mensajes", json={"texto": "   "}).status_code == 400
    assert cliente.delete(f"/chats/{cid}").json() == {"borrado": cid}
    assert cliente.get(f"/chats/{cid}/mensajes").status_code == 404


def test_api_cambio_de_modo_escrito_en_el_chat():
    chats.guardar_ajuste("voz_chat", "0")
    cid = cliente.post("/chats").json()["id"]
    r = cliente.post(f"/chats/{cid}/mensajes", json={"texto": "modo voz"}).json()
    assert r["categoria"] == "modos"


def test_api_habla_en_segundo_plano_si_la_voz_esta_activa(monkeypatch):
    hablado = []
    monkeypatch.setattr(voice, "hablar", hablado.append)
    chats.guardar_ajuste("voz_chat", "1")
    cid = cliente.post("/chats").json()["id"]
    with mock.patch("servidor.threading.Thread") as hilo:
        hilo.side_effect = lambda target, args, daemon: SimpleNamespace(start=lambda: target(*args))
        cliente.post(f"/chats/{cid}/mensajes", json={"texto": "toma nota: algo"})
    assert hablado and "algo" in hablado[0]
