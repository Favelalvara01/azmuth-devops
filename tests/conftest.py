"""
conftest.py — configuración compartida de las pruebas de Azmuth.

Azmuth es un asistente de escritorio para Windows (micrófono, teclado
virtual, ventanas). En el pipeline de CI (GitHub Actions, Linux, sin
pantalla) esas librerías no existen, así que aquí se SIMULAN (mocks):
así se valida la lógica de cada skill sin abrir programas reales.

Además, cada prueba usa su propia base de datos SQLite temporal: nunca
se tocan las notas, recordatorios ni la memoria reales del usuario.
"""
import os
import sys
import types
from unittest import mock

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

# --- Librerías exclusivas de Windows / hardware: se reemplazan por dobles ---
for nombre in ("pyautogui", "pygetwindow", "speech_recognition", "sounddevice", "webview", "pyttsx3"):
    if nombre not in sys.modules:
        sys.modules[nombre] = mock.MagicMock(name=nombre)

# Sin claves reales durante las pruebas (nunca se llama a la API de verdad)
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("ELEVENLABS_API_KEY", "")

if "anthropic" not in sys.modules:
    try:
        import anthropic  # noqa: F401
    except ImportError:  # pragma: no cover
        sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=mock.MagicMock())


@pytest.fixture(autouse=True)
def bd_temporal(tmp_path, monkeypatch):
    """Cada prueba arranca con una base de datos SQLite vacía y aislada."""
    import basedatos
    monkeypatch.setattr(basedatos, "_RUTA_DB", str(tmp_path / "azmuth_test.db"))
    yield tmp_path / "azmuth_test.db"


@pytest.fixture(autouse=True)
def log_temporal(tmp_path, monkeypatch):
    """El registro de errores de las pruebas va a una carpeta temporal."""
    import monitoreo
    monkeypatch.setattr(monitoreo, "_RUTA_LOG", str(tmp_path / "errores.log"))
    monkeypatch.setattr(monitoreo, "_logger", None)
    yield tmp_path / "errores.log"


@pytest.fixture(autouse=True)
def sin_efectos_externos(monkeypatch):
    """Evita que una prueba abra el navegador, programas o comandos reales."""
    import webbrowser
    import subprocess
    abiertos = []
    monkeypatch.setattr(webbrowser, "open", lambda url, *a, **k: abiertos.append(url) or True)
    monkeypatch.setattr(subprocess, "run", mock.MagicMock(name="subprocess.run"))
    if hasattr(os, "startfile"):
        monkeypatch.setattr(os, "startfile", mock.MagicMock(side_effect=OSError("bloqueado en pruebas")))
    yield abiertos


@pytest.fixture(autouse=True)
def tematica_normal(monkeypatch):
    """Las pruebas no dependen de la fecha real (en octubre sería Halloween) ni hacen ruido."""
    import datetime
    import tematicas
    monkeypatch.setattr(tematicas, "_preferencia", None)
    monkeypatch.setattr(tematicas, "_hoy", lambda: datetime.date(2026, 6, 15))
    monkeypatch.setattr(tematicas, "_reproducir", mock.MagicMock(name="winsound"))
    yield
