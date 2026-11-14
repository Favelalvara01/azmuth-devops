"""
PRUEBAS DE USABILIDAD (automatizadas)
=====================================
La usabilidad mide qué tan FÁCIL, rápido y agradable es usar Azmuth
(ISO 9241-11: eficacia, eficiencia y satisfacción). Una parte se automatiza
revisando reglas objetivas de las heurísticas de Nielsen y de accesibilidad
(WCAG 2.1); la otra parte (satisfacción) se mide con usuarios reales y el
cuestionario SUS (ver el reporte, sección de pruebas manuales).

Heurísticas revisadas:
  H1 Visibilidad del estado      -> la interfaz muestra en qué estado está Azmuth
  H2 Lenguaje del usuario         -> mensajes en español, sin trazas técnicas
  H5 Prevención de errores        -> entiende frases sin acentos o con signos
  H7 Eficiencia                   -> respuesta de skills en menos de 1 segundo, Enter para enviar
  H10 Ayuda                       -> el comando "ayuda" explica qué se puede hacer
  WCAG 2.5.5 / 1.1.1 / 3.1.1      -> botones de 44 px, imágenes con alt, idioma declarado

Ejecutar:  py -3.13 -m pytest -m usabilidad -v
"""
import re
import time
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

import servidor
import skills

pytestmark = pytest.mark.usabilidad
cliente = TestClient(servidor.app)


class _Botones(HTMLParser):
    """Junta cada <button> con su texto visible y su title (nombre accesible)."""

    def __init__(self):
        super().__init__()
        self.botones, self._actual = [], None

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            self._actual = {"title": dict(attrs).get("title", ""), "texto": ""}

    def handle_data(self, data):
        if self._actual is not None:
            self._actual["texto"] += data

    def handle_endtag(self, tag):
        if tag == "button" and self._actual is not None:
            self.botones.append(self._actual)
            self._actual = None


def test_cu_01_interfaz_declara_idioma_viewport_y_titulo():
    """CU-01 (WCAG 3.1.1): idioma español, adaptable a pantalla y con título."""
    html = cliente.get("/").text
    assert '<html lang="es">' in html
    assert 'name="viewport"' in html
    assert re.search(r"<title>.+</title>", html)


def test_cu_02_todos_los_botones_tienen_nombre_accesible():
    """CU-02 (WCAG 4.1.2): ningún botón queda sin texto ni descripción."""
    lector = _Botones()
    lector.feed(cliente.get("/").text)
    assert len(lector.botones) >= 8
    sin_nombre = [b for b in lector.botones if not (b["texto"].strip() or b["title"].strip())]
    assert sin_nombre == []


def test_cu_03_botones_del_reloj_son_faciles_de_tocar():
    """CU-03 (WCAG 2.5.5): los botones táctiles del reloj miden al menos 44 px."""
    html = cliente.get("/reloj").text
    alto = int(re.search(r"\.menu-btn\s*{[^}]*?height:\s*(\d+)px", html).group(1))
    assert alto >= 44
    assert 'alt="${item.name}"' in html           # imágenes con texto alternativo (WCAG 1.1.1)


def test_cu_04_estado_visible_y_enter_para_enviar():
    """CU-04 (H1, H7): hay texto de estado y se envía el mensaje con Enter."""
    html = cliente.get("/").text
    assert 'id="statusText"' in html and 'id="estadoChat"' in html
    assert "ev.key === 'Enter' && !ev.shiftKey" in html
    assert 'placeholder="Escríbale a Azmuth…"' in html


@pytest.mark.parametrize("frase", ["que hora es", "¿Qué hora es?", "QUÉ HORA ES", "  qué hora es  ", "Qué hora es."])
def test_cu_05_entiende_frases_imperfectas(frase):
    """CU-05 (H5): el usuario no tiene que escribir 'perfecto' para que lo entienda."""
    assert skills.procesar(frase)[1] == "tiempo"


def test_cu_06_respuestas_rapidas_y_cortas_para_voz():
    """CU-06 (H7): las skills responden en < 1 s y con frases cortas (se dicen en voz alta)."""
    for frase in ("qué hora es", "toma nota: estudiar", "mis notas", "volumen a 30", "modo voz"):
        inicio = time.perf_counter()
        respuesta, _ = skills.procesar(frase)
        assert time.perf_counter() - inicio < 1.0
        assert len(respuesta) <= 160, respuesta


def test_cu_07_ayuda_explica_que_puede_hacer():
    """CU-07 (H10): "ayuda" menciona las funciones principales."""
    respuesta, _ = skills.procesar("ayuda")
    for funcion in ("notas", "recordatorios", "música", "aplicación"):
        assert funcion in respuesta


def test_cu_08_errores_en_lenguaje_del_usuario():
    """CU-08 (H2, H9): los errores se explican en español y sin detalles técnicos."""
    r1 = cliente.post("/idioma", json={"idioma": "francés"})
    r2 = cliente.post("/chats/999999/mensajes", json={"texto": "hola"})
    r3 = cliente.post("/modo", json={"modo": "turbo"})
    assert (r1.json()["detail"], r2.json()["detail"]) == ("Idioma no soportado", "Ese chat no existe")
    assert "usa 'voz' o 'escritorio'" in r3.json()["detail"]
    for r in (r1, r2, r3):
        assert "Traceback" not in r.text
