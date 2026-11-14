"""
PRUEBAS UNITARIAS (automatizadas)
=================================
Una prueba unitaria revisa UNA sola función, aislada del resto del programa
(sin micrófono, sin internet, sin IA). Si falla, sabemos exactamente qué
función está mal. Se usan entradas conocidas y se compara la salida con la
esperada (patrón AAA: Arrange - Act - Assert).

Ejecutar:  py -3.13 -m pytest -m unitaria -v
"""
from datetime import date, datetime

import pytest

import basedatos
import chats
import cerebro
import config
import skills
from skills import recordatorios, tiempo

pytestmark = pytest.mark.unitaria


def test_cp_uni_01_variantes_quita_signos_y_agrega_acentos():
    """CP-UNI-01: skills.variantes() genera las versiones del texto a probar."""
    # Arrange
    texto = "¿que hora es?"
    # Act
    versiones = skills.variantes(texto)
    # Assert
    assert versiones == ["¿que hora es?", "que hora es", "qué hora es"]


def test_cp_uni_02_titulo_de_chat_se_corta_en_48_caracteres():
    """CP-UNI-02: chats._titulo_desde() recorta títulos largos sin partir palabras."""
    largo = "Explícame paso a paso cómo se configuran las pruebas unitarias en pytest"
    titulo = chats._titulo_desde(largo)
    assert len(titulo) <= 49 and titulo.endswith("…")
    assert chats._titulo_desde("   ") == "Nuevo chat"


@pytest.mark.parametrize("valor,esperado", [
    ("sk-ant-123", "sk-ant-123"),            # clave real
    ("tu_clave_de_anthropic_aqui", ""),     # texto de ejemplo de .env.example
    ("your-key", ""),
    ("   ", ""),
])
def test_cp_uni_03_clave_de_ejemplo_cuenta_como_vacia(monkeypatch, valor, esperado):
    """CP-UNI-03: config._clave() ignora los textos de ejemplo del .env."""
    monkeypatch.setenv("CLAVE_PRUEBA", valor)
    assert config._clave("CLAVE_PRUEBA") == esperado


def test_cp_uni_04_hora_objetivo_pm_es_en_formato_24h():
    """CP-UNI-04: recordatorios._calcular_hora_objetivo() convierte 5 pm a 17:00."""
    objetivo = recordatorios._calcular_hora_objetivo(5, 30, "pm")
    assert (objetivo.hour, objetivo.minute) == (17, 30)
    assert objetivo > datetime.now()          # siempre en el futuro


def test_cp_uni_05_extraer_dias_de_un_recordatorio_recurrente():
    """CP-UNI-05: recordatorios._extraer_dias() detecta los días de la semana."""
    texto, dias = recordatorios._extraer_dias("entregar el reporte los martes y jueves")
    assert dias == [1, 3]
    assert texto == "entregar el reporte"


def test_cp_uni_06_fecha_siempre_en_espanol():
    """CP-UNI-06 (regresión DEF-021): la fecha no depende del idioma de Windows."""
    assert tiempo.fecha_en_espanol(date(2026, 11, 12)) == "jueves 12 de noviembre de 2026"


@pytest.mark.parametrize("texto,patron", [
    ("pan", "%pan%"),
    ("%", "%\\%%"),          # el comodín se escapa (DEF-019)
    ("a_b", "%a\\_b%"),
])
def test_cp_uni_07_patron_like_escapa_comodines(texto, patron):
    """CP-UNI-07: basedatos.patron_like() escapa % y _ de SQL LIKE."""
    assert basedatos.patron_like(texto) == patron


def test_cp_uni_08_orden_de_proveedores_de_ia(monkeypatch):
    """CP-UNI-08: cerebro.proveedores() respeta el orden Claude > DeepSeek > Groq > Gemini."""
    for clave in ("ANTHROPIC_API_KEY", "DEEPSEEK_API_KEY", "GROQ_API_KEY", "GEMINI_API_KEY"):
        monkeypatch.setattr(config, clave, "")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "g")
    monkeypatch.setattr(config, "GROQ_API_KEY", "q")
    assert cerebro.proveedores() == ["groq", "gemini"]
    assert cerebro.proveedores(con_imagen=True) == ["gemini"]   # Groq no ve imágenes
