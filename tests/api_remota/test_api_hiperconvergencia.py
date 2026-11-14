"""
PRUEBAS DE API Y DE SERVICIOS EN LA INFRAESTRUCTURA HIPERCONVERGENTE
====================================================================
Estas pruebas NO usan TestClient: hablan por la RED con la API de Azmuth que
corre DENTRO de la máquina virtual Ubuntu Server (hipervisor VirtualBox),
en el nodo hiperconvergente armado con Docker (cómputo + almacenamiento +
red definidos por software, ver hiperconvergencia/docker-compose.yml).

  Windows (anfitrión)  --VirtualBox NAT 127.0.0.1:8081-->  VM Ubuntu :8080  -->  contenedor azmuth-api

Se ejecutan de dos formas:
  1) Desde Windows, a través del hipervisor:
       $env:AZMUTH_URL="http://127.0.0.1:8081"; $env:AZMUTH_TOKEN="<token>"
       py -3.13 -m pytest tests/api_remota -v
  2) Desde dentro del nodo, servicio a servicio (contenedor "probador"):
       docker compose --profile pruebas run --rm probador

Si AZMUTH_URL no está definida, se omiten (así no fallan en el CI normal).
"""
import os
import statistics
import time

import pytest
import requests

URL = os.getenv("AZMUTH_URL", "").rstrip("/")
TOKEN = os.getenv("AZMUTH_TOKEN", "")

pytestmark = [
    pytest.mark.api_remota,
    pytest.mark.skipif(not URL, reason="Define AZMUTH_URL con la dirección de la API en la VM"),
]


def _get(ruta, token=True, headers=None, **kw):
    cabeceras = headers if headers is not None else ({"X-Azmuth-Token": TOKEN} if token else {})
    return requests.get(f"{URL}{ruta}", headers=cabeceras, timeout=10, **kw)


def _send(metodo, ruta, json=None):
    return requests.request(metodo, f"{URL}{ruta}", json=json, headers={"X-Azmuth-Token": TOKEN}, timeout=10)


def test_api_01_el_nodo_responde_por_la_red():
    """API-01: la API del contenedor contesta a través del hipervisor (conectividad)."""
    r = _get("/salud")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_api_02_responde_el_contenedor_linux_de_la_vm():
    """API-02: quien contesta es el contenedor Linux de la VM, no el Windows anfitrión."""
    datos = _get("/salud").json()
    print(f"\nnodo que respondió: {datos['nodo']} | sistema: {datos['sistema']} | activo: {datos['activo_segundos']} s")
    assert datos["sistema"] == "Linux"
    assert datos["control_remoto_protegido"] is True


def test_api_03_sin_token_la_red_es_rechazada():
    """API-03: desde la red (anfitrión u otro contenedor) sin token -> 401 (DEF-020)."""
    assert _get("/estado", token=False).status_code == 401
    assert _get("/estado", headers={"X-Azmuth-Token": "token-falso"}).status_code == 401


def test_api_04_contrato_del_estado():
    """API-04: /estado devuelve el JSON que espera la interfaz."""
    r = _get("/estado")
    assert r.status_code == 200 and r.headers["content-type"].startswith("application/json")
    assert {"estado", "modo", "idioma", "log_total"} <= set(r.json())


def test_api_05_crud_de_chats_y_almacenamiento_del_nodo():
    """API-05: crear chat, mandar comando, leer, renombrar y borrar (se guarda en el volumen)."""
    chat_id = _send("POST", "/chats").json()["id"]
    r = _send("POST", f"/chats/{chat_id}/mensajes", {"texto": "toma nota: prueba en la VM"})
    assert r.status_code == 200 and r.json()["categoria"] == "notas"
    assert len(_get(f"/chats/{chat_id}/mensajes").json()["mensajes"]) == 2
    assert _send("PATCH", f"/chats/{chat_id}", {"titulo": "Chat de la VM"}).json()["titulo"] == "Chat de la VM"
    assert _send("DELETE", f"/chats/{chat_id}").status_code == 200
    assert _get(f"/chats/{chat_id}/mensajes").status_code == 404


def test_api_06_validacion_de_entradas():
    """API-06: la API rechaza datos inválidos con 400/422 y nunca con 500."""
    assert _send("POST", "/idioma", {"idioma": "klingon"}).status_code == 400
    assert _send("POST", "/modo", {"modo": 5}).status_code == 422
    assert _get("/comando").status_code == 422


def test_api_07_latencia_a_traves_del_hipervisor():
    """API-07: 30 peticiones por la red virtual con promedio < 300 ms."""
    tiempos = []
    for _ in range(30):
        inicio = time.perf_counter()
        assert _get("/estado").status_code == 200
        tiempos.append((time.perf_counter() - inicio) * 1000)
    print(f"\nlatencia por el hipervisor: promedio {statistics.mean(tiempos):.1f} ms | máx {max(tiempos):.1f} ms")
    assert statistics.mean(tiempos) < 300


def test_api_08_skill_sin_pantalla_no_tumba_el_chat():
    """API-08 (DEF-022): en la VM no hay teclado; "volumen a 40" avisa en vez de dar 500."""
    chat_id = _send("POST", "/chats").json()["id"]
    r = _send("POST", f"/chats/{chat_id}/mensajes", {"texto": "volumen a 40"})
    assert r.status_code == 200 and r.json()["categoria"] == "multimedia"
    _send("DELETE", f"/chats/{chat_id}")


def test_api_09_servicio_de_comandos_en_el_nodo():
    """API-09: el servicio de control remoto responde dentro del nodo (lista blanca)."""
    assert _get("/comando", params={"accion": "mute"}).json()["status"] == "ok"
    assert _get("/comando", params={"accion": "rm -rf /"}).json()["status"] == "error"
