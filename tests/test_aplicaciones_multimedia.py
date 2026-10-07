import subprocess
import sys

from skills import aplicaciones, multimedia, ayuda, sistema


def test_limpiar_texto_voz():
    assert aplicaciones.limpiar_texto_voz("¡Ábreme la CALCULADORA, por favor!") == "abreme la calculadora por favor"
    assert aplicaciones.limpiar_texto_voz("") == ""


def test_youtube_con_busqueda(sin_efectos_externos):
    assert aplicaciones.intentar("abre youtube y busca lofi") == 'Abriendo YouTube y buscando "lofi".'
    assert sin_efectos_externos[-1].endswith("search_query=lofi")


def test_youtube_sin_busqueda():
    assert aplicaciones.intentar("abre youtube") == "Le abro YouTube."


def test_cerrar_app_registrada_y_no_registrada():
    assert aplicaciones.intentar("cierra el bloc de notas") == "Cerrando bloc de notas."
    subprocess.run.assert_called()
    assert aplicaciones.intentar("cierra minecraft") is None  # lo resuelve skills/apps_instaladas


def test_abrir_url_y_modos(sin_efectos_externos):
    assert aplicaciones.intentar("abre localito") == "Abriendo localito."
    assert aplicaciones.intentar("rickroll") == "Activando modo Rickroll."
    assert "Messenger" in aplicaciones.intentar("abre messenger")


def test_frase_sin_verbo_no_abre_nada():
    assert aplicaciones.intentar("me gusta la calculadora") is None


def test_volumen_se_limita_entre_0_y_100():
    pyautogui = sys.modules["pyautogui"]
    pyautogui.press.reset_mock()
    assert multimedia.intentar("volumen a 150") == "Volumen ajustado al 100 por ciento."
    assert pyautogui.press.call_count == 50 + 50


def test_controles_multimedia():
    assert multimedia.intentar("pausa") == "Reproducción pausada o reanudada."
    assert multimedia.intentar("siguiente") == "Reproduciendo siguiente pista."
    assert multimedia.intentar("silencia") == "Estado de silencio alternado."
    assert multimedia.intentar("sube el volumen") == "Subiendo volumen."


def test_ayuda_y_sistema():
    assert "comandos exactos" in ayuda.intentar("qué puedes hacer")
    assert sistema.intentar("borra el historial") == "Historial de conversación reiniciado."
    assert sistema.intentar("hola") is None
