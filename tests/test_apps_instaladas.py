"""Pruebas de la skill que abre CUALQUIER app instalada y aprende sola."""
from types import SimpleNamespace
from unittest import mock

import pytest

import cerebro
import config
import skills
from skills import apps_instaladas as ai

INDICE = [
    {"nombre": "Discord", "tipo": "appid", "destino": "com.squirrel.Discord.Discord"},
    {"nombre": "Steam", "tipo": "appid", "destino": "Valve.Steam"},
    {"nombre": "Minecraft Launcher", "tipo": "appid", "destino": "Microsoft.4297127D64EC6_8wekyb3d8bbwe!Minecraft"},
    {"nombre": "Google Chrome", "tipo": "appid", "destino": "Chrome"},
    {"nombre": "OBS Studio", "tipo": "appid", "destino": "OBS"},
    {"nombre": "Fortnite", "tipo": "ruta", "destino": r"C:\Users\osiel\Desktop\Fortnite.url"},
    {"nombre": "Microsoft Teams", "tipo": "appid", "destino": "MSTeams"},
    {"nombre": "Microsoft To Do", "tipo": "appid", "destino": "ToDo"},
]


@pytest.fixture
def pc(monkeypatch):
    escaneos = []
    monkeypatch.setattr(ai, "escanear_windows", lambda: escaneos.append(1) or INDICE)
    abiertas, cerradas = [], []
    monkeypatch.setattr(ai, "lanzar", lambda app: abiertas.append(app["nombre"]) or True)
    monkeypatch.setattr(ai, "cerrar", lambda app: cerradas.append(app["nombre"]) or True)
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    return SimpleNamespace(abiertas=abiertas, cerradas=cerradas, escaneos=escaneos)


def test_normalizar():
    assert ai.normalizar("¡Ábreme el Minecraft!") == "abreme minecraft"


@pytest.mark.parametrize("frase,app", [
    ("abre discord", "Discord"), ("ábreme el steam", "Steam"), ("abre minecraft", "Minecraft Launcher"),
    ("inicia obs", "OBS Studio"), ("abre chrome", "Google Chrome"), ("ejecuta fortnite", "Fortnite"),
    ("abre discor", "Discord"),  # error de dictado: lo encuentra por parecido
])
def test_abre_apps_que_no_estan_en_la_lista_fija(pc, frase, app):
    respuesta = ai.intentar(frase)
    assert respuesta.startswith(f"Abriendo {app}") and pc.abiertas == [app]


def test_aprende_y_la_segunda_vez_usa_la_memoria(pc):
    assert "La agregué" in ai.intentar("abre discord")
    assert ai.intentar("abre discord") == "Abriendo Discord."
    assert ai.recordada("discord")["nombre"] == "Discord"
    assert "discord" in ai.intentar("qué aplicaciones aprendiste")


def test_ensenar_un_alias(pc):
    assert "Minecraft Launcher" in ai.intentar("cuando diga el juego de bloques abre minecraft")
    assert ai.intentar("abre el juego de bloques").startswith("Abriendo Minecraft Launcher")


def test_cerrar_cualquier_app(pc):
    assert ai.intentar("cierra steam") == "Cerrando Steam."
    assert pc.cerradas == ["Steam"]


def test_ambigua_sin_ia_pregunta_cual(pc):
    r = ai.intentar("abre microsoft")
    assert r.startswith("No estoy seguro") and "Microsoft Teams" in r and pc.abiertas == []


def test_ambigua_la_resuelve_la_ia(pc, monkeypatch):
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "clave-falsa")
    falso = mock.MagicMock()
    falso.messages.create.return_value = SimpleNamespace(content=[SimpleNamespace(type="text", text="Microsoft To Do")])
    monkeypatch.setattr(cerebro, "_cliente", falso)
    assert ai.intentar("abre la de pendientes de microsoft").startswith("Abriendo Microsoft To Do")


def test_si_no_es_una_app_deja_que_conteste_claude(pc):
    assert ai.intentar("abre tu corazón a la ciencia") is None
    assert ai.intentar("hola") is None


def test_reescanea_si_no_la_encuentra_y_por_comando(pc):
    ai.intentar("abre programa inexistente xyz")
    assert len(pc.escaneos) == 2  # índice inicial + re-escaneo por si se acaba de instalar
    assert ai.intentar("actualiza tus aplicaciones") == f"Listo, encontré {len(INDICE)} aplicaciones y accesos directos en su computadora."


def test_el_enrutador_manda_apps_desconocidas_a_esta_skill(pc):
    respuesta, skill = skills.procesar("abre discord")
    assert skill == "apps_instaladas" and respuesta.startswith("Abriendo Discord")
    _, skill = skills.procesar("abre calculadora")
    assert skill == "aplicaciones"  # las de la lista fija siguen igual


def test_escanear_sin_windows_no_truena():
    with mock.patch("skills.apps_instaladas.subprocess.run", side_effect=FileNotFoundError):
        assert ai.escanear_windows() == []
