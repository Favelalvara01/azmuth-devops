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


# ---------- Seguridad del control remoto (TOKEN_REMOTO) ----------
NGROK = {"X-Forwarded-For": "201.1.2.3"}


def test_sin_token_configurado_todo_funciona_igual(monkeypatch):
    monkeypatch.setattr(servidor.config, "TOKEN_REMOTO", "")
    r = TestClient(servidor.app).get("/comando", params={"accion": "mute"}, headers=NGROK)
    assert r.status_code == 200


def test_desde_internet_sin_token_se_rechaza(monkeypatch):
    monkeypatch.setattr(servidor.config, "TOKEN_REMOTO", "s3creto")
    r = TestClient(servidor.app).get("/comando", params={"accion": "bloquear"}, headers=NGROK)
    assert r.status_code == 401


def test_desde_internet_con_token_pasa(monkeypatch):
    monkeypatch.setattr(servidor.config, "TOKEN_REMOTO", "s3creto")
    cliente = TestClient(servidor.app)
    por_cabecera = cliente.get("/comando", params={"accion": "mute"},
                               headers={**NGROK, "X-Azmuth-Token": "s3creto"})
    por_url = cliente.get("/reloj", params={"token": "s3creto"}, headers=NGROK)
    assert por_cabecera.status_code == 200 and por_url.status_code == 200
    assert "X-Azmuth-Token" in por_url.text  # la página reenvía el token en cada fetch


def test_ventana_local_no_necesita_token(monkeypatch):
    monkeypatch.setattr(servidor.config, "TOKEN_REMOTO", "s3creto")
    assert TestClient(servidor.app).get("/estado").status_code == 200


def test_salud_indica_si_esta_protegido(monkeypatch):
    monkeypatch.setattr(servidor.config, "TOKEN_REMOTO", "s3creto")
    assert TestClient(servidor.app).get("/salud").json()["control_remoto_protegido"] is True
