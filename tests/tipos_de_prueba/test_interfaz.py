"""
TÉCNICA: PRUEBAS DE INTERFAZ
============================
Revisan los puntos donde dos partes se comunican:

  a) Interfaz de programación (API REST de FastAPI): que cada endpoint
     respete su CONTRATO — método, código HTTP, tipo de contenido y forma
     del JSON. Si la interfaz gráfica o el celular esperan un campo y la
     API deja de mandarlo, la prueba lo detecta.
  b) Interfaz gráfica (azmuth.html y /reloj): que los elementos que el
     usuario toca existan y estén conectados a acciones reales del backend.

Ejecutar:  py -3.13 -m pytest -m interfaz -v
"""
import re
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import acciones_remotas
import idioma
import servidor
import tematicas

pytestmark = pytest.mark.interfaz


@pytest.fixture
def cliente():
    with mock.patch.object(servidor, "_hablar_en_segundo_plano"):
        yield TestClient(servidor.app)
    idioma.cambiar("es", guardar=False)


# Contrato: (método, ruta, cuerpo, código esperado, campos obligatorios y su tipo)
CONTRATOS = [
    ("get", "/estado", None, 200, {"estado": str, "detalle": str, "log": list, "log_total": int, "modo": str,
                                   "version_chat": int, "idioma": str, "tematica": str}),
    ("get", "/salud", None, 200, {"status": str, "activo_segundos": int, "errores_total": int,
                                  "ultimos_errores": list, "control_remoto_protegido": bool,
                                  "nodo": str, "sistema": str}),
    ("get", "/modo", None, 200, {"modo": str, "voz_chat": bool}),
    ("get", "/idioma", None, 200, {"idioma": str, "disponibles": list}),
    ("get", "/tematica", None, 200, {"tematica": str, "preferencia": str, "disponibles": list}),
    ("get", "/chats", None, 200, {"chats": list}),
    ("post", "/chats", None, 200, {"id": int}),
    ("post", "/voz_chat", {"activa": False}, 200, {"voz_chat": bool}),
    ("get", "/comando?accion=mute", None, 200, {"status": str, "mensaje": str}),
]


@pytest.mark.parametrize("metodo,ruta,cuerpo,codigo,campos", CONTRATOS, ids=[f"{c[0].upper()} {c[1]}" for c in CONTRATOS])
def test_ci_01_contrato_de_cada_endpoint(cliente, metodo, ruta, cuerpo, codigo, campos):
    """CI-01: código HTTP, JSON y tipo de cada campo del contrato."""
    r = getattr(cliente, metodo)(ruta, json=cuerpo) if cuerpo else getattr(cliente, metodo)(ruta)
    assert r.status_code == codigo
    assert r.headers["content-type"].startswith("application/json")
    datos = r.json()
    for campo, tipo in campos.items():
        assert isinstance(datos[campo], tipo), f"{ruta}: '{campo}' debería ser {tipo.__name__}"


def test_ci_02_errores_de_validacion_usan_422(cliente):
    """CI-02: un cuerpo mal formado recibe 422 (contrato de validación de FastAPI/Pydantic)."""
    assert cliente.post("/idioma", json={"lenguaje": "es"}).status_code == 422
    assert cliente.post("/chats/abc/mensajes", json={"texto": "hola"}).status_code == 422
    assert cliente.get("/comando").status_code == 422


def test_ci_03_listas_disponibles_coinciden_con_el_backend(cliente):
    """CI-03: lo que la interfaz ofrece en sus menús es lo que el backend soporta."""
    assert set(cliente.get("/idioma").json()["disponibles"]) == set(idioma.IDIOMAS)
    assert set(cliente.get("/tematica").json()["disponibles"]) == {"auto", *tematicas.TEMAS}


def test_ci_04_cada_boton_del_reloj_tiene_accion_real(cliente):
    """CI-04: todos los cmd: "..." del reloj existen en acciones_remotas.ACCIONES."""
    html = cliente.get("/reloj").text
    comandos = set(re.findall(r'cmd:\s*"(\w+)"', html))
    assert len(comandos) >= 20
    assert comandos - set(acciones_remotas.ACCIONES) == set()


def test_ci_05_la_ventana_llama_endpoints_que_existen(cliente):
    """CI-05: cada fetch('/ruta') o api('/ruta') de azmuth.html apunta a una ruta de FastAPI."""
    html = cliente.get("/").text
    usadas = set(re.findall(r"(?:fetch|api)\(\s*['`](/[\w/]*)", html))
    registradas = {r.path for r in servidor.app.routes}

    def existe(ruta):   # "/chats/" + id  ->  "/chats/{chat_id}"
        return ruta in registradas or any(p.startswith(ruta) and "{" in p for p in registradas)

    assert len(usadas) >= 5
    assert {u for u in usadas if not existe(u)} == set()


def test_ci_06_elementos_clave_de_la_interfaz(cliente):
    """CI-06: existen los elementos con los que el usuario interactúa."""
    html = cliente.get("/").text
    for elemento in ('id="textoEntrada"', 'id="btnEnviar"', 'id="listaChats"', 'id="consoleLog"',
                     "cambiarModo('escritorio')", "cambiarModo('voz')", "alternarIdioma()"):
        assert elemento in html, elemento
