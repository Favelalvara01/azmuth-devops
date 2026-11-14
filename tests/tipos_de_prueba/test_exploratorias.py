"""
PRUEBAS EXPLORATORIAS (automatizadas)
=====================================
En la prueba exploratoria el tester aprende, diseña y ejecuta al mismo
tiempo, siguiendo una "carta" (charter) en vez de un guion fijo. Aquí se
automatiza la exploración con FUZZING: se generan cientos de frases y
peticiones al azar (mezclando palabras reales, signos, emojis, mayúsculas,
textos larguísimos) y se observa si Azmuth truena, se cuelga o responde
algo inválido. La semilla se imprime para poder repetir cualquier hallazgo.

Cartas exploradas:
  C1 - Explorar el enrutador de skills con frases mezcladas para descubrir caídas.
  C2 - Explorar la API con datos raros para descubrir errores 500.
  C3 - Explorar la fecha/hora con distintos idiomas del sistema (halló DEF-021).

Ejecutar:  py -3.13 -m pytest -m exploratoria -v -s
"""
import random
import string
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import estado
import idioma
import servidor
import skills
import tematicas
from skills import tiempo

pytestmark = pytest.mark.exploratoria


@pytest.fixture(autouse=True)
def exploracion_segura(monkeypatch):
    """Las frases al azar pueden decir "abre ..." o "habla en inglés": nada se abre
    de verdad en Windows y al terminar se regresa a español / modo voz."""
    import subprocess
    monkeypatch.setattr(subprocess, "Popen", mock.MagicMock(name="subprocess.Popen"))
    yield
    idioma.cambiar("es", guardar=False)
    estado._modo_actual = "voz"
    tematicas._preferencia = None


SEMILLA = 2026
PALABRAS = ["abre", "cierra", "pon", "toma nota", "recuérdame", "busca", "volumen", "pestaña", "siguiente",
            "modo", "escritorio", "qué", "hora", "clima", "olvídate", "borra", "mis", "notas", "a las", "pm",
            "%", "_", "'", '"', ";", "--", "DROP TABLE notas", "<script>", "🦖", "ñ", "¿", "!", "\n", "0", "99"]


def _frase_aleatoria(rnd: random.Random) -> str:
    n = rnd.randint(1, 8)
    partes = [rnd.choice(PALABRAS) for _ in range(n)]
    if rnd.random() < 0.2:
        partes.append("".join(rnd.choices(string.printable, k=rnd.randint(1, 40))))
    frase = " ".join(partes)
    return frase.upper() if rnd.random() < 0.15 else frase


def test_ce_01_enrutador_con_500_frases_aleatorias(capsys):
    """CE-01 (carta C1): ninguna frase hace tronar a las skills; la respuesta es texto o None."""
    rnd = random.Random(SEMILLA)
    resueltas = 0
    for _ in range(500):
        frase = _frase_aleatoria(rnd)
        respuesta, skill = skills.procesar(frase)
        assert respuesta is None or isinstance(respuesta, str), frase
        assert (respuesta is None) == (skill is None), frase
        resueltas += respuesta is not None
    print(f"\n[semilla {SEMILLA}] 500 frases: {resueltas} las resolvió una skill, {500 - resueltas} irían a la IA")


def test_ce_02_api_con_datos_raros_no_da_error_500():
    """CE-02 (carta C2): la API valida la entrada y nunca responde 500."""
    rnd = random.Random(SEMILLA)
    cliente = TestClient(servidor.app, raise_server_exceptions=False)
    raros = ["", " ", "x" * 5000, "🦖" * 50, "<script>alert(1)</script>", "'; DROP TABLE chats;--", None, 123, [], {}]
    with mock.patch.object(servidor, "_hablar_en_segundo_plano"):
        chat_id = cliente.post("/chats").json()["id"]
        for dato in raros + [_frase_aleatoria(rnd) for _ in range(40)]:
            for metodo, ruta, cuerpo in (
                ("post", f"/chats/{chat_id}/mensajes", {"texto": dato}),
                ("patch", f"/chats/{chat_id}", {"titulo": dato}),
                ("post", "/modo", {"modo": dato}),
                ("post", "/idioma", {"idioma": dato}),
                ("post", "/tematica", {"tematica": dato}),
            ):
                r = getattr(cliente, metodo)(ruta, json=cuerpo)
                assert r.status_code < 500, (ruta, dato, r.text)
        for accion in ["", "../../etc/passwd", "vol_up;rm", "%00", "A" * 300]:
            assert cliente.get("/comando", params={"accion": accion}).status_code < 500


def test_ce_03_fecha_no_depende_del_idioma_del_sistema():
    """CE-03 (carta C3): hallazgo DEF-021 — la fecha salía en inglés ("Thursday ... November")."""
    respuesta = tiempo.intentar("qué día es hoy")
    dias_en = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
    assert not any(d in respuesta.lower() for d in dias_en)
    assert any(m in respuesta for m in tiempo._MESES)
