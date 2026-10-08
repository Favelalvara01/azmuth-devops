"""Monitoreo: registro de errores en ejecución y endpoint /salud."""
import sys
import threading

from fastapi.testclient import TestClient

import monitoreo
import servidor


def test_registrar_error_escribe_traza(log_temporal):
    try:
        1 / 0
    except ZeroDivisionError as e:
        monitoreo.registrar_error("prueba", e)
    texto = log_temporal.read_text(encoding="utf-8")
    assert "prueba: division by zero" in texto and "Traceback" in texto
    ultimo = monitoreo.resumen()["ultimos_errores"][-1]
    assert ultimo["tipo"] == "ZeroDivisionError" and ultimo["origen"] == "prueba"


def test_resumen_cuenta_errores():
    antes = monitoreo.resumen()["errores_total"]
    monitoreo.registrar_error("x", ValueError("y"))
    assert monitoreo.resumen()["errores_total"] == antes + 1


def test_instalar_captura_errores_de_hilos(monkeypatch, log_temporal):
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    monitoreo.instalar()
    hilo = threading.Thread(target=lambda: 1 / 0, name="hilo-prueba")
    hilo.start()
    hilo.join()
    assert "hilo hilo-prueba" in log_temporal.read_text(encoding="utf-8")


def test_endpoint_salud():
    monitoreo.registrar_error("servidor", RuntimeError("caída simulada"))
    datos = TestClient(servidor.app).get("/salud").json()
    assert datos["status"] == "ok" and datos["errores_total"] >= 1
    assert datos["ultimos_errores"][-1]["mensaje"] == "caída simulada"


def test_error_en_endpoint_queda_registrado(monkeypatch):
    def explota():
        raise RuntimeError("bd corrupta")
    monkeypatch.setattr(servidor.estado, "obtener_estado", explota)
    r = TestClient(servidor.app, raise_server_exceptions=False).get("/estado")
    assert r.status_code == 500
    assert monitoreo.resumen()["ultimos_errores"][-1]["origen"] == "GET /estado"
