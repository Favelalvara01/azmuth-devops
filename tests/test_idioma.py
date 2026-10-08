"""Idioma: español / inglés en voz, chat, comandos e interfaz."""
from unittest import mock

import pytest
from fastapi.testclient import TestClient

import cerebro
import chats
import idioma
import main
import servidor
import skills
import voice
from skills import ingles


@pytest.fixture(autouse=True)
def espanol_al_terminar():
    yield
    idioma.cambiar("es", guardar=False)


@pytest.fixture
def en_ingles(monkeypatch):
    idioma.cambiar("en", guardar=False)
    # La traducción real llama a Claude: en pruebas se marca con [EN]
    monkeypatch.setattr(cerebro, "traducir", lambda texto, a="en": f"[EN] {texto}")


# ---------- cambiar de idioma ----------
@pytest.mark.parametrize("frase", ["cambia a inglés", "Habla en inglés", "pon el idioma en inglés",
                                   "switch to English", "English mode", "Azmuth, speak English"])
def test_frases_para_pasar_a_ingles(frase):
    respuesta, skill = skills.procesar(frase)
    assert skill == "idiomas" and idioma.obtener() == "en" and "English" in respuesta


@pytest.mark.parametrize("frase", ["switch to Spanish", "speak spanish", "cambia a español"])
def test_frases_para_regresar_a_espanol(frase, en_ingles):
    respuesta, skill = skills.procesar(frase)
    assert skill == "idiomas" and idioma.obtener() == "es"


def test_el_idioma_se_guarda_y_se_restaura():
    idioma.cambiar("en")
    assert chats.obtener_ajuste("idioma") == "en"
    idioma.cambiar("es", guardar=False)
    assert idioma.cargar() == "en"


def test_idioma_invalido_no_cambia():
    assert idioma.cambiar("fr") == "es"


# ---------- comandos en inglés ----------
@pytest.mark.parametrize("ingles_,espanol", [
    ("open Discord", "abre discord"), ("Can you please close Spotify?", "cierra spotify"),
    ("new tab", "nueva pestaña"), ("close this tab", "cierra pestaña"), ("tab 3", "pestaña 3"),
    ("volume to 40%", "volumen a 40"), ("volume up", "sube el volumen"), ("next song", "siguiente"),
    ("play my playlist", "pon mi playlist"), ("pause", "pausa"), ("mute", "silencia"),
    ("take a note: buy coffee", "toma nota: buy coffee"), ("my notes", "mis notas"),
    ("remind me to study at 7 pm", "recuérdame study a las 7 pm"),
    ("remind me to drink water every day at 9", "recuérdame drink water todos los días a las 9"),
    ("what time is it?", "qué hora es"), ("what's the date today", "qué fecha es"),
    ("what's the weather like", "qué clima hace"), ("what can you do", "ayuda"),
    ("search for cats", "busca cats"), ("desktop mode", "modo escritorio"),
])
def test_traduce_comandos(ingles_, espanol):
    assert ingles.a_espanol(ingles_).lower() == espanol


def test_frase_libre_no_es_comando():
    assert ingles.a_espanol("explain what DevOps is") is None


def test_comando_en_ingles_usa_la_skill_y_contesta_en_ingles(en_ingles):
    respuesta, skill = skills.procesar("take a note: buy coffee")
    assert skill == "notas" and respuesta.startswith("[EN] Nota guardada")


def test_en_ingles_next_friday_no_cambia_la_cancion(en_ingles):
    # sin la restricción, la skill multimedia tomaba "next" como "siguiente canción"
    assert skills.procesar("next friday I have an exam, help me plan") == (None, None)


def test_ayuda_en_ingles_no_se_traduce_con_ia(en_ingles):
    respuesta, skill = skills.procesar("help")
    assert skill == "ayuda" and respuesta.startswith("I can help you") and "[EN]" not in respuesta


def test_pantalla_en_ingles(en_ingles, monkeypatch):
    from skills import pantalla
    monkeypatch.setattr(pantalla, "capturar", lambda: b"JPEG")
    analizar = mock.MagicMock(return_value="I see VS Code.")
    monkeypatch.setattr(cerebro, "analizar_imagen", analizar)
    respuesta, skill = skills.procesar("what's on my screen?")
    assert respuesta == "I see VS Code." and analizar.call_args.args[1] == pantalla._PREGUNTA_GENERICA_EN


# ---------- Claude, voz y palabra clave ----------
def test_prompt_de_claude_pide_ingles(en_ingles):
    assert "ENGLISH" in cerebro._construir_system_prompt()


def test_prompt_en_espanol_no_lo_pide():
    assert "ENGLISH" not in cerebro._construir_system_prompt()


def test_traducir_sin_clave_regresa_el_original(monkeypatch):
    monkeypatch.setattr(cerebro.config, "ANTHROPIC_API_KEY", "")
    assert cerebro.traducir("Abriendo paint.") == "Abriendo paint."


def test_traducir_usa_cache(monkeypatch):
    monkeypatch.setattr(cerebro.config, "ANTHROPIC_API_KEY", "x")
    cliente = mock.MagicMock()
    cliente.messages.create.return_value.content = [mock.MagicMock(type="text", text="Opening paint.")]
    monkeypatch.setattr(cerebro, "_obtener_cliente", lambda: cliente)
    cerebro._cache_traducciones.clear()
    assert cerebro.traducir("Abriendo paint.") == "Opening paint."
    assert cerebro.traducir("Abriendo paint.") == "Opening paint."
    assert cliente.messages.create.call_count == 1


def test_reconocimiento_de_voz_cambia_de_idioma(en_ingles):
    assert idioma.codigo_voz() == "en-US"


def test_palabra_clave_en_ingles(monkeypatch):
    monkeypatch.setattr(main, "PALABRA_CLAVE", "omnitrix")
    monkeypatch.setattr(main, "PALABRA_CLAVE_EN", "omnitrix")
    assert main.extraer_comando("omnitrix open discord") == "open discord"
    # el dictado en inglés a veces separa la palabra inventada
    assert main.extraer_comando("Omni trix, what time is it") == "what time is it"
    assert main.extraer_comando("omni-trix") == ""
    assert main.extraer_comando("open discord") is None


def test_palabra_clave_extra_en_ingles(monkeypatch):
    monkeypatch.setattr(main, "PALABRA_CLAVE", "omnitrix")
    monkeypatch.setattr(main, "PALABRA_CLAVE_EN", "it's hero time")
    assert main.extraer_comando("It’s hero time what time is it") == "what time is it"
    assert main.extraer_comando("omnitrix qué hora es") == "qué hora es"


def test_apagado_en_ingles():
    assert main.es_apagado("shut down")


def test_texto_para_voz_en_ingles(en_ingles):
    assert voice.texto_para_voz("x " * 300).endswith("The rest is on screen.")


def test_voz_de_windows_en_ingles(en_ingles):
    motor = mock.MagicMock()
    motor.getProperty.return_value = [mock.MagicMock(id="ES_SABINA", name="Microsoft Sabina"),
                                      mock.MagicMock(id="EN-US_ZIRA", name="Microsoft Zira")]
    assert voice._elegir_voz_windows(motor) == "EN-US_ZIRA"


# ---------- servidor e interfaz ----------
def test_endpoint_idioma():
    c = TestClient(servidor.app)
    assert c.post("/idioma", json={"idioma": "en"}).json() == {"idioma": "en"}
    assert c.get("/estado").json()["idioma"] == "en"
    assert c.post("/idioma", json={"idioma": "xx"}).status_code == 400


def test_la_interfaz_tiene_boton_y_textos_en_ingles():
    html = TestClient(servidor.app).get("/").text
    assert "alternarIdioma()" in html and "DESKTOP MODE" in html and "HOW CAN I HELP, SIR?" in html



def test_recordatorio_en_ingles_se_guarda_con_hora(en_ingles):
    import basedatos
    respuesta, skill = skills.procesar("remind me to study at 7 pm")
    assert skill == "recordatorios" and respuesta.startswith("[EN]")
    with basedatos.conectar() as con:
        fila = con.execute("SELECT texto, hora, hora_objetivo FROM recordatorios").fetchone()
    assert fila["texto"] == "study" and "19:00" in (fila["hora"] or fila["hora_objetivo"] or "")
