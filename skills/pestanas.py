"""
Skill: control de pestañas y ventanas abiertas en el navegador o Windows.
Permite cambiar de pestaña, cerrar pestañas o alternar entre ventanas.

Los atajos de teclado (Ctrl+Tab, Ctrl+W, etc.) le llegan a la ventana que
tenga el foco en ese momento — normalmente esta consola, no Edge. Por eso
antes de mandar el atajo, buscamos la ventana de Edge y la traemos al
frente. Si usas otro navegador, cambia "edge" por el nombre del tuyo en
_enfocar_navegador().
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
        print(f"[pestanas] No pude enfocar el navegador: {e}")


def intentar(texto: str):
    t = texto.lower().strip()

    if re.match(r"^(?:siguiente\s+pestaña|cambia\s+de\s+pestaña|otra\s+pestaña)", t):
        _enfocar_navegador()
        pyautogui.hotkey("ctrl", "tab")
        return "Cambiando a la siguiente pestaña."

    if re.match(r"^(?:pestaña\s+anterior|regresa\s+de\s+pestaña)", t):
        _enfocar_navegador()
        pyautogui.hotkey("ctrl", "shift", "tab")
        return "Cambiando a la pestaña anterior."

    # Mapeo por si Google transcribe los números como texto (ej. "uno" en lugar de "1")
    numeros_texto = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9}

    m = re.match(r"^(?:ve\s+a\s+(?:la\s+)?pestaña|pestaña)\s+(?:(\d+)|([a-záéíóú]+))", t)
    if m:
        num_str_digito = m.group(1)
        num_str_palabra = m.group(2)
        
        num = None
        if num_str_digito:
            num = int(num_str_digito)
        elif num_str_palabra and num_str_palabra in numeros_texto:
            num = numeros_texto[num_str_palabra]

        if num:
            if 1 <= num <= 8:
                _enfocar_navegador()
                pyautogui.hotkey("ctrl", str(num))
                return f"Cambiando a la pestaña {num}."
            elif num == 9:
                _enfocar_navegador()
                pyautogui.hotkey("ctrl", "9")
                return "Cambiando a la última pestaña."

    if re.match(r"^(?:cierra\s+(?:esta\s+)?pestaña|cerrar\s+pestaña)", t):
        _enfocar_navegador()
        pyautogui.hotkey("ctrl", "w")
        return "Pestaña cerrada."

    if re.match(r"^(?:nueva\s+pestaña|abre\s+(?:una\s+)?pestaña)", t):
        _enfocar_navegador()
        pyautogui.hotkey("ctrl", "t")
        return "Abriendo nueva pestaña."

    if re.match(r"^(?:cambia\s+de\s+ventana|otra\s+ventana|alternar\s+ventana)", t):
        pyautogui.hotkey("alt", "tab")
        return "Alternando ventana."

    return None