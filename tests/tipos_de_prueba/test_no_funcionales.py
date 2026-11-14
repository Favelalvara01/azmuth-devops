"""
TÉCNICA: PRUEBAS NO FUNCIONALES
===============================
No revisan QUÉ hace Azmuth sino CÓMO lo hace: atributos de calidad de
ISO/IEC 25010. Se miden con números y un umbral de aceptación:

  Eficiencia de desempeño -> latencia (p95) y prueba de carga concurrente
  Fiabilidad              -> tolerancia a fallos y persistencia de datos
  Portabilidad            -> arranca sin las librerías de Windows (Docker / Linux)
  Mantenibilidad          -> todas las skills cumplen el mismo contrato

Ejecutar:  py -3.13 -m pytest -m no_funcional -v -s
"""
import sqlite3
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

import monitoreo
import servidor
import skills
from skills import notas

pytestmark = pytest.mark.no_funcional
cliente = TestClient(servidor.app, raise_server_exceptions=False)


def test_cnf_01_rendimiento_latencia_estado():
    """CNF-01: 200 peticiones a /estado con p95 < 50 ms (la interfaz lo consulta cada 300 ms)."""
    tiempos = []
    for _ in range(200):
        inicio = time.perf_counter()
        assert cliente.get("/estado").status_code == 200
        tiempos.append((time.perf_counter() - inicio) * 1000)
    p95 = statistics.quantiles(tiempos, n=20)[18]
    print(f"\n/estado -> promedio {statistics.mean(tiempos):.2f} ms | p95 {p95:.2f} ms | máx {max(tiempos):.2f} ms")
    assert p95 < 50


def test_cnf_02_carga_concurrente_20_usuarios():
    """CNF-02: 20 clientes a la vez x 10 peticiones = 200 sin errores (prueba de carga)."""
    def usuario(_):
        c = TestClient(servidor.app)
        return [c.get(ruta).status_code for ruta in ("/estado", "/salud", "/modo", "/idioma", "/chats") * 2]

    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=20) as hilos:
        codigos = [c for lista in hilos.map(usuario, range(20)) for c in lista]
    duracion = time.perf_counter() - inicio
    print(f"\n{len(codigos)} peticiones concurrentes en {duracion:.2f} s ({len(codigos) / duracion:.0f} pet/s)")
    assert codigos.count(200) == 200


def test_cnf_03_fiabilidad_un_error_no_tumba_el_servidor(monkeypatch):
    """CNF-03: si un endpoint truena, responde 500 controlado, se registra y el resto sigue."""
    import estado
    monkeypatch.setattr(estado, "obtener_estado", lambda: 1 / 0)
    assert cliente.get("/estado").status_code == 500
    monkeypatch.undo()
    assert cliente.get("/salud").json()["errores_total"] >= 1
    assert cliente.get("/estado").status_code == 200          # se recupera solo
    assert monitoreo.resumen()["ultimos_errores"][-1]["tipo"] == "ZeroDivisionError"


def test_cnf_04_fiabilidad_los_datos_persisten(bd_temporal):
    """CNF-04: lo guardado sigue ahí al abrir una conexión nueva (como al reiniciar Azmuth)."""
    notas.intentar("toma nota: no perder esto")
    con = sqlite3.connect(bd_temporal)           # conexión nueva e independiente (como tras reiniciar)
    try:
        assert con.execute("SELECT texto FROM notas").fetchone()[0] == "no perder esto"
        assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    finally:
        con.close()


def test_cnf_05_portabilidad_api_sin_librerias_de_windows():
    """CNF-05: servidor.py arranca sin pyautogui/micrófono (así corre en Docker y en la VM)."""
    # nucleo y voice (que cargan pyautogui y el micrófono) se importan DENTRO de las funciones
    assert "nucleo" not in servidor.__dict__ and "voice" not in servidor.__dict__


def test_cnf_06_mantenibilidad_contrato_de_skills():
    """CNF-06: cada skill expone intentar(texto) y regresa None si no le toca."""
    for skill in skills.SKILLS:
        assert callable(getattr(skill, "intentar", None)), skill.__name__
        assert skill.intentar("zzz frase que nadie entiende 123") is None, skill.__name__
