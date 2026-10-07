"""
Skill: control de volumen y reproducción multimedia.
El volumen (subir/bajar/mute) es una tecla verdaderamente global de
Windows, funciona sin importar qué ventana tenga el foco. Pero
pausa/siguiente/anterior dependen de qué app tenga la sesión de
reproducción "activa" para Windows, que en la práctica casi siempre
es la ventana que está al frente — por eso ahí sí enfocamos Edge primero.
"""
import re
import time
import pyautogui

try:
    import pygetwindow as gw
except ImportError:
    gw = None


def _enfocar_navegador():
    if gw is None:
        return
    try:
        candidatas = [w for w in gw.getAllWindows() if w.title.strip() and "edge" in w.title.lower()]
        if candidatas:
            candidatas[0].activate()
            time.sleep(0.15)
    except Exception as e:
        print(f"[multimedia] No pude enfocar el navegador: {e}")


def intentar(texto: str):
    if not texto:
        return None

    t = texto.lower().strip()

    m = re.match(r"^(?:sube|subir|baja|bajar|pon)?\s*(?:el\s+)?volumen\s+(?:a\s+|al\s+)?(\d+)(?:\s*(?:%|por ciento))?", t)
    if m:
        nivel = max(0, min(100, int(m.group(1))))
        for _ in range(50):
            pyautogui.press("volumedown")
        pasos = int(nivel / 2)
        for _ in range(pasos):
            pyautogui.press("volumeup")
        return f"Volumen ajustado al {nivel} por ciento."

    if re.match(r"^(?:pausa|pausar|reproducir|play|reanudar)", t):
        _enfocar_navegador()
        pyautogui.press("playpause")
        return "Reproducción pausada o reanudada."

    if re.match(r"^(?:silencia|silenciar|mute|callarse|quitar silencio|activar sonido)", t):
        pyautogui.press("volumemute")
        return "Estado de silencio alternado."

    if re.match(r"^(?:siguiente|cancion siguiente|next|pasar)", t):
        _enfocar_navegador()
        pyautogui.press("nexttrack")
        return "Reproduciendo siguiente pista."

    if re.match(r"^(?:anterior|cancion anterior|previous|regresar pista)", t):
        _enfocar_navegador()
        pyautogui.press("prevtrack")
        return "Reproduciendo pista anterior."

    if re.match(r"^(?:sube|subir)(?:\s+el)?\s+volumen", t):
        for _ in range(5):
            pyautogui.press("volumeup")
        return "Subiendo volumen."

    if re.match(r"^(?:baja|bajar)(?:\s+el)?\s+volumen", t):
        for _ in range(5):
            pyautogui.press("volumedown")
        return "Bajando volumen."

    return None
