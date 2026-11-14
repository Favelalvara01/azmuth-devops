"""
PRUEBAS DE SEGURIDAD
====================
Buscan debilidades que un atacante podría aprovechar, tomando como guía el
OWASP Top 10 (2021) y OWASP API Security Top 10 (2023):

  A01 Control de acceso roto      -> token del control remoto (incluye DEF-020)
  A03 Inyección                   -> SQL, comodines LIKE (DEF-019), comandos del SO
  A05 Configuración insegura      -> rutas fuera de /imagenes, cookies, errores con traza
  A02 Exposición de datos         -> claves de la API que nunca deben salir en respuestas
  A07 XSS                         -> la interfaz escapa el HTML de los mensajes

Se complementan con análisis estático (bandit), de dependencias (pip-audit)
y un escaneo dinámico con OWASP ZAP contra la API en la VM (ver reporte).

Ejecutar:  py -3.13 -m pytest -m seguridad -v
"""
import inspect
import os
import subprocess
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import chats
import config
import servidor
from basedatos import conectar
from skills import notas

pytestmark = pytest.mark.seguridad
INTERNET = {"X-Forwarded-For": "201.1.2.3"}
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def con_token(monkeypatch):
    monkeypatch.setattr(config, "TOKEN_REMOTO", "Omnitrix-2026-largo")
    return "Omnitrix-2026-largo"


# ---------------- A01: control de acceso ----------------
@pytest.mark.parametrize("token", [None, "", "omnitrix-2026-largo", "Omnitrix-2026-larg", "' OR '1'='1"])
def test_cs_01_token_ausente_o_incorrecto_se_rechaza(con_token, token):
    """CS-01: sin token, con mayúsculas distintas o con inyección -> 401."""
    cabeceras = {**INTERNET, **({"X-Azmuth-Token": token} if token is not None else {})}
    r = TestClient(servidor.app).get("/comando", params={"accion": "bloquear"}, headers=cabeceras)
    assert r.status_code == 401 and r.json()["mensaje"] == "Token inválido"


def test_cs_02_comparacion_de_token_resistente_a_ataques_de_tiempo():
    """CS-02: el token se compara con hmac.compare_digest (tiempo constante)."""
    assert "hmac.compare_digest" in inspect.getsource(servidor._token_valido)


def test_cs_03_red_local_sin_token_se_rechaza(monkeypatch, con_token):
    """CS-03 (DEF-020): en la VM/contenedor, un equipo de la red sin token ya no entra."""
    monkeypatch.setattr(config, "EXIGIR_TOKEN_EN_RED", True)
    vecino = TestClient(servidor.app, client=("192.168.1.50", 51000))
    assert vecino.get("/comando", params={"accion": "bloquear"}).status_code == 401
    assert vecino.get("/estado", headers={"X-Azmuth-Token": con_token}).status_code == 200
    local = TestClient(servidor.app, client=("127.0.0.1", 51000))
    assert local.get("/estado").status_code == 200            # la ventana local sigue sin token


def test_cs_04_cookie_del_token_es_segura(con_token):
    """CS-04: la cookie que recuerda el token es HttpOnly, Secure y SameSite."""
    r = TestClient(servidor.app, base_url="https://testserver").get("/reloj", params={"token": con_token}, headers=INTERNET)
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" in cookie and "samesite=lax" in cookie


# ---------------- A03: inyección ----------------
def test_cs_05_inyeccion_sql_se_guarda_como_texto():
    """CS-05: un título o nota con SQL malicioso no ejecuta nada (consultas parametrizadas)."""
    ataque = "x'); DROP TABLE notas; --"
    notas.intentar(f"toma nota: {ataque}")
    chat_id = chats.crear_chat()
    chats.renombrar_chat(chat_id, ataque)
    with conectar() as con:
        assert con.execute("SELECT texto FROM notas").fetchone()["texto"] == ataque
        assert con.execute("SELECT titulo FROM chats WHERE id = ?", (chat_id,)).fetchone()["titulo"] == ataque


@pytest.mark.parametrize("comodin", ["%", "_", "%%"])
def test_cs_06_comodines_like_no_borran_todo(comodin):
    """CS-06 (DEF-019): "borra la nota de %" borraba TODAS las notas."""
    notas.intentar("toma nota: tarea de métricas")
    notas.intentar("toma nota: comprar pan")
    assert "No encontré" in notas.intentar(f"borra la nota de {comodin}")
    with conectar() as con:
        assert con.execute("SELECT COUNT(*) FROM notas").fetchone()[0] == 2


@pytest.mark.parametrize("accion", ["bloquear; shutdown /s", "bloquear && del C:\\*", "$(whoami)", "mute|calc"])
def test_cs_07_no_hay_inyeccion_de_comandos_remotos(accion):
    """CS-07: /comando solo acepta acciones de una lista blanca; lo demás no ejecuta nada."""
    subprocess.run.reset_mock()
    r = TestClient(servidor.app).get("/comando", params={"accion": accion})
    assert r.json()["status"] == "error"
    assert not subprocess.run.called


# ---------------- A05: configuración ----------------
@pytest.mark.parametrize("ruta", ["/imagenes/../.env", "/imagenes/..%2f.env", "/imagenes/%2e%2e/config.py",
                                  "/imagenes/..%5c.env"])
def test_cs_08_no_se_puede_salir_de_la_carpeta_de_imagenes(ruta):
    """CS-08: recorrido de directorios (path traversal) bloqueado."""
    r = TestClient(servidor.app).get(ruta)
    assert r.status_code in (400, 404) or "API_KEY" not in r.text


def test_cs_09_errores_internos_no_muestran_la_traza(monkeypatch):
    """CS-09: un 500 responde 'Error interno' sin rutas ni código del servidor."""
    import estado
    monkeypatch.setattr(estado, "obtener_estado", mock.MagicMock(side_effect=RuntimeError("C:\\Users\\osiel secreto")))
    r = TestClient(servidor.app, raise_server_exceptions=False).get("/estado")
    assert r.status_code == 500 and r.json() == {"status": "error", "mensaje": "Error interno"}


# ---------------- A02: exposición de datos sensibles ----------------
def test_cs_10_las_claves_nunca_salen_en_las_respuestas(monkeypatch):
    """CS-10: ningún endpoint devuelve las claves de IA ni el token."""
    secretos = {"ANTHROPIC_API_KEY": "sk-ant-SECRETO-123", "ELEVENLABS_API_KEY": "el-SECRETO-456",
                "TOKEN_REMOTO": ""}
    for nombre, valor in secretos.items():
        monkeypatch.setattr(config, nombre, valor)
    cliente = TestClient(servidor.app)
    for ruta in ("/estado", "/salud", "/modo", "/idioma", "/tematica", "/chats", "/", "/reloj"):
        texto = cliente.get(ruta).text
        assert "SECRETO" not in texto, ruta


def test_cs_11_el_env_no_se_sube_a_git_ni_a_docker():
    """CS-11: .env (claves) está en .gitignore y .dockerignore."""
    for archivo in (".gitignore", ".dockerignore"):
        with open(os.path.join(RAIZ, archivo), encoding="utf-8") as f:
            assert ".env" in [linea.strip() for linea in f], archivo


# ---------------- A07: XSS ----------------
def test_cs_12_la_interfaz_escapa_el_html_de_los_mensajes():
    """CS-12: los mensajes se pintan con textContent o pasan por escaparHTML()."""
    html = TestClient(servidor.app).get("/").text
    assert "let t = escaparHTML(texto || '')" in html                     # respuestas de Azmuth (Markdown)
    assert "caja.querySelector('.burbuja').textContent = m.texto" in html  # mensajes del usuario
    assert "item.querySelector('.titulo').textContent = c.titulo" in html  # títulos de chats


@pytest.mark.parametrize("frase", ["abre calculadora; powershell -c whoami", "abre powershell & whoami",
                                   "cierra chrome && whoami"])
def test_cs_13_texto_del_usuario_nunca_llega_a_la_shell(monkeypatch, frase):
    """CS-13: bandit marca shell=True (B602); se comprueba que esos comandos salen de un
    catálogo fijo y que lo que dice el usuario nunca se pasa a la shell."""
    from skills import aplicaciones  # noqa: F401  (la skill que usa shell=True)
    import skills
    monkeypatch.setattr(subprocess, "Popen", mock.MagicMock(name="Popen"))
    subprocess.run.reset_mock()
    skills.procesar(frase)
    llamadas = [str(c) for c in subprocess.run.call_args_list + subprocess.Popen.call_args_list]
    assert not any("whoami" in c for c in llamadas)
