"""
TÉCNICA: PRUEBAS FUNCIONALES (caja negra)
=========================================
Validan QUÉ hace el sistema contra sus requisitos funcionales, sin mirar
el código por dentro: se da una entrada y se compara la salida con la
esperada. Técnicas de diseño de casos usadas:

  1. Partición de equivalencia  -> clases válidas / inválidas de una entrada
  2. Análisis de valores límite -> justo en el borde (48, 49 caracteres...)
  3. Tabla de decisión           -> combinaciones de condiciones (token remoto)
  4. Casos de uso                -> frase del usuario -> respuesta esperada

Ejecutar:  py -3.13 -m pytest -m funcional -v
"""
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import chats
import config
import idioma
import servidor
import skills

pytestmark = pytest.mark.funcional


@pytest.fixture
def cliente():
    with mock.patch.object(servidor, "_hablar_en_segundo_plano"):
        yield TestClient(servidor.app)
    idioma.cambiar("es", guardar=False)


# ---------------- 1. Partición de equivalencia ----------------
@pytest.mark.parametrize("valor,codigo", [
    ("es", 200), ("en", 200),                     # clase válida
    ("fr", 400), ("", 400), ("ES", 400),          # clase inválida: no soportado / vacío / mayúsculas
])
def test_cf_01_particion_equivalencia_idioma(cliente, valor, codigo):
    """CF-01: POST /idioma acepta solo los idiomas soportados."""
    assert cliente.post("/idioma", json={"idioma": valor}).status_code == codigo


@pytest.mark.parametrize("modo,codigo", [("voz", 200), ("escritorio", 200), ("chat", 400), ("VOZ", 400)])
def test_cf_02_particion_equivalencia_modo(cliente, modo, codigo):
    """CF-02: POST /modo acepta 'voz' y 'escritorio'."""
    assert cliente.post("/modo", json={"modo": modo}).status_code == codigo
    cliente.post("/modo", json={"modo": "voz"})


# ---------------- 2. Valores límite ----------------
@pytest.mark.parametrize("largo,recortado", [(47, False), (48, False), (49, True), (200, True)])
def test_cf_03_valor_limite_titulo_del_chat(largo, recortado):
    """CF-03: el título se recorta solo a partir de 49 caracteres (límite = 48)."""
    texto = ("palabra " * 40)[:largo].strip() or "x"
    texto = texto.ljust(largo, "x")
    titulo = chats._titulo_desde(texto)
    assert titulo.endswith("…") is recortado


@pytest.mark.parametrize("texto,codigo", [("", 400), ("   ", 400), ("a", 200), ("x" * 4000, 200)])
def test_cf_04_valor_limite_mensaje(cliente, texto, codigo):
    """CF-04: mensaje vacío -> 400; 1 carácter o muy largo -> 200."""
    chat_id = cliente.post("/chats").json()["id"]
    assert cliente.post(f"/chats/{chat_id}/mensajes", json={"texto": texto}).status_code == codigo


# ---------------- 3. Tabla de decisión (control remoto) ----------------
#  Regla | Token configurado | Viene de internet | Token correcto | Resultado
#   R1   |        No         |        Sí         |       -        | Permitido
#   R2   |        Sí         |        No         |       -        | Permitido (ventana local)
#   R3   |        Sí         |        Sí         |       No       | 401
#   R4   |        Sí         |        Sí         |       Sí       | Permitido
@pytest.mark.parametrize("regla,token_conf,internet,token_ok,codigo", [
    ("R1", "", True, False, 200),
    ("R2", "clave", False, False, 200),
    ("R3", "clave", True, False, 401),
    ("R4", "clave", True, True, 200),
])
def test_cf_05_tabla_de_decision_token(monkeypatch, cliente, regla, token_conf, internet, token_ok, codigo):
    """CF-05: cada regla de la tabla de decisión del middleware de seguridad."""
    monkeypatch.setattr(config, "TOKEN_REMOTO", token_conf)
    cabeceras = {"X-Forwarded-For": "8.8.8.8"} if internet else {}
    if token_ok:
        cabeceras["X-Azmuth-Token"] = token_conf
    assert cliente.get("/comando", params={"accion": "mute"}, headers=cabeceras).status_code == codigo, regla


# ---------------- 4. Casos de uso: entrada -> salida esperada ----------------
@pytest.mark.parametrize("frase,esperado", [
    ("toma nota: revisar CI", 'Nota guardada: "revisar CI".'),
    ("volumen a 40", "Volumen ajustado al 40 por ciento."),
    ("guarda el contacto de Jesús como 6561234567", "Listo, guardé a Jesús con el número 5216561234567."),
    ("recuerda que mi color favorito es verde", "Guardado. Ya sé que mi color favorito es verde."),
    ("mis hábitos", "Todavía no tengo suficientes datos sobre sus hábitos."),
])
def test_cf_06_frase_produce_la_respuesta_esperada(frase, esperado):
    """CF-06: requisitos funcionales de las skills (caja negra)."""
    assert skills.procesar(frase)[0] == esperado
