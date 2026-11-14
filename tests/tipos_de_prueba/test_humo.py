"""
TÉCNICA: PRUEBAS DE HUMO (smoke testing)
========================================
Es la primera prueba que se corre después de cada cambio o despliegue:
pocas verificaciones, muy rápidas (< 5 s), que confirman que lo ESENCIAL
"enciende" sin echar humo. Si una falla, no tiene caso correr el resto
de las pruebas: la versión se rechaza. En el pipeline (ci.yml) también se
hace una prueba de humo con GET /estado dentro del contenedor Docker.

Ejecutar:  py -3.13 -m pytest -m humo -v
"""
import importlib

import pytest
from fastapi.testclient import TestClient

import servidor
import skills
from basedatos import conectar

pytestmark = pytest.mark.humo
cliente = TestClient(servidor.app)


@pytest.mark.parametrize("modulo", ["config", "estado", "basedatos", "chats", "cerebro", "nucleo", "servidor", "skills"])
def test_ch_01_los_modulos_principales_importan(modulo):
    """CH-01: cada módulo principal se importa sin errores."""
    assert importlib.import_module(modulo)


def test_ch_02_la_api_responde():
    """CH-02: /estado y /salud contestan 200."""
    assert cliente.get("/estado").status_code == 200
    assert cliente.get("/salud").json()["status"] == "ok"


def test_ch_03_la_interfaz_carga():
    """CH-03: la ventana principal (/) y el reloj (/reloj) se sirven."""
    assert "<html" in cliente.get("/").text.lower()
    assert cliente.get("/reloj").status_code == 200


def test_ch_04_la_base_de_datos_crea_sus_tablas():
    """CH-04: SQLite crea todas las tablas que usa Azmuth."""
    with conectar() as con:
        tablas = {f[0] for f in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"notas", "recordatorios", "memoria", "chats", "mensajes", "ajustes"} <= tablas


def test_ch_05_las_skills_estan_cargadas_y_responden():
    """CH-05: hay 17+ skills registradas y un comando básico funciona."""
    assert len(skills.SKILLS) >= 17
    assert skills.procesar("ayuda")[1] == "ayuda"
