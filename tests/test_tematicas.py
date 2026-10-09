"""Temáticas de temporada: normal, Halloween, Día de Muertos y Navidad."""
import datetime
import io
import wave

import pytest
from fastapi.testclient import TestClient

import cerebro
import estado
import idioma
import servidor
import skills
import tematicas
from skills import temas


@pytest.fixture(autouse=True)
def espanol_al_terminar():
    yield
    idioma.cambiar("es", guardar=False)


@pytest.mark.parametrize("fecha, tema", [
    ((2026, 10, 1), "halloween"), ((2026, 10, 31), "halloween"), ((2026, 11, 2), "muertos"),
    ((2026, 12, 24), "navidad"), ((2027, 1, 6), "navidad"), ((2027, 1, 7), "normal"), ((2026, 6, 15), "normal"),
])
def test_temporada_por_fecha(fecha, tema):
    assert tematicas.por_fecha(datetime.date(*fecha)) == tema


def test_automatica_sigue_la_fecha(monkeypatch):
    assert tematicas.preferencia() == "auto" and tematicas.obtener() == "normal"
    monkeypatch.setattr(tematicas, "_hoy", lambda: datetime.date(2026, 10, 20))
    assert tematicas.obtener() == "halloween"
    assert "Halloween" in tematicas.saludo()


@pytest.mark.parametrize("frase, tema", [
    ("temática de Halloween", "halloween"), ("Azmuth, pon el modo Halloween", "halloween"),
    ("tema día de muertos", "muertos"), ("temática del día de muertos", "muertos"),
    ("activa la temática de navidad", "navidad"), ("modo navideño", "navidad"),
    ("temática normal", "normal"), ("quita la temática", "normal"),
    ("Halloween theme", "halloween"), ("Christmas mode", "navidad"), ("day of the dead theme", "muertos"),
])
def test_cambiar_por_voz_o_chat(frase, tema, monkeypatch):
    sonidos = []
    monkeypatch.setattr(temas, "_sonar", lambda: sonidos.append(tematicas.obtener()))
    respuesta, skill = skills.procesar(frase)
    assert skill == "temas" and tematicas.obtener() == tema and respuesta
    assert sonidos == [tema]  # suena el efecto de la temática elegida


def test_se_guarda_al_reiniciar():
    skills.procesar("temática de Navidad")
    tematicas._preferencia = None  # como si Azmuth se volviera a abrir
    assert tematicas.obtener() == "navidad"


def test_automatica_y_lista():
    skills.procesar("temática de Halloween")
    respuesta, _ = skills.procesar("temática automática")
    assert tematicas.preferencia() == "auto" and "fecha" in respuesta
    respuesta, skill = skills.procesar("¿qué temáticas tienes?")
    assert skill == "temas" and "Día de Muertos" in respuesta


@pytest.mark.parametrize("frase", ["explícame el tema de la fotosíntesis", "busca disfraces de halloween",
                                   "qué es el día de muertos", "modo escritorio"])
def test_no_se_roba_otras_frases(frase):
    _, skill = skills.procesar(frase)
    assert skill != "temas"


def test_en_ingles_responde_en_ingles():
    idioma.cambiar("en", guardar=False)
    respuesta, skill = skills.procesar("Halloween theme")
    assert skill == "temas" and "Halloween theme on" in respuesta


def test_estado_y_servidor_informan_la_tematica():
    cliente = TestClient(servidor.app)
    assert cliente.post("/tematica", json={"tematica": "muertos"}).json()["tematica"] == "muertos"
    assert estado.obtener_estado()["tematica"] == "muertos"
    assert cliente.get("/tematica").json()["preferencia"] == "muertos"
    assert cliente.post("/tematica", json={"tematica": "pascua"}).status_code == 400


def test_toque_de_temporada_en_la_ia():
    assert "TEMPORADA" not in cerebro._construir_system_prompt()
    tematicas.cambiar("halloween", guardar=False)
    assert "Halloween" in cerebro._construir_system_prompt()


@pytest.mark.parametrize("tema", ["halloween", "muertos", "navidad"])
def test_sonidos_son_wav_validos(tema):
    datos = tematicas._sintetizar(tema)
    with wave.open(io.BytesIO(datos)) as w:
        assert w.getnchannels() == 1 and 1.5 < w.getnframes() / w.getframerate() < 3
    assert tematicas._sintetizar("normal") == b""


def test_sin_winsound_no_truena(monkeypatch):
    monkeypatch.setattr(tematicas, "_reproducir", lambda datos: (_ for _ in ()).throw(ImportError("winsound")))
    assert tematicas.reproducir_sonido("navidad") is False


@pytest.mark.parametrize("fuente", ["creepster.woff2", "lobster.woff2", "mountains-of-christmas.woff2"])
def test_letras_de_las_tematicas_van_incluidas(fuente):
    """Las fuentes se sirven desde el propio Azmuth: funcionan sin internet y en el .exe."""
    cliente = TestClient(servidor.app)
    assert f"/imagenes/fuentes/{fuente}" in cliente.get("/").text
    r = cliente.get(f"/imagenes/fuentes/{fuente}")
    assert r.status_code == 200 and r.content[:4] == b"wOF2"
