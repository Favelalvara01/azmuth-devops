"""Acciones del control remoto (/comando) como tabla de despacho.

HU-11 / DEF-015: antes vivían en un if/elif gigante dentro de servidor.py
(complejidad ciclomática 27, rango D) con líneas de PowerShell de más de
200 caracteres. Ahora cada acción es una entrada de ACCIONES y los scripts
de PowerShell se arman con plantillas cortas.
"""
import subprocess
import webbrowser

# Plantilla para declarar keybd_event de user32.dll (teclas virtuales).
_DECLARAR_TECLADO = (
    "$code = '[DllImport(\"user32.dll\")] public static extern void "
    "keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; "
    "Add-Type -MemberDefinition $code -Name '{nombre}' -Namespace '{ns}'; "
)
_SHELL = "(New-Object -ComObject WScript.Shell)"
_BRILLO = (
    "$b = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods); "
    "if ($b) {{ $curr = (Get-WmiObject -Namespace root/WMI "
    "-Class WmiMonitorBrightness).CurrentBrightness; "
    "$b.WmiSetBrightness(1, [Math]::{fn}({lim}, $curr {op} 15)) }}"
)
_URL_MUSICA = "https://www.youtube.com/watch?v=pMNhe03RKZE&list=PLTEsV4ouHz8U&index=2"
_URL_CHAPA = "https://www.youtube.com/watch?v=qD9uZp9TyR8&list=RDqD9uZp9TyR8&start_radio=1"


def _ps(script: str):
    subprocess.run(["powershell", "-command", script], shell=True)


def _ps_corto(script: str):
    subprocess.run(f'powershell -command "{script}"', shell=True)


def _cmd(linea: str):
    subprocess.run(linea, shell=True)


def _teclas(nombre: str, ns: str, teclas: list[int], previo: str = "", repetir: int = 1):
    """Pulsa (down) y suelta (up) las teclas virtuales en orden tipo atajo."""
    llamada = f"[{ns}.{nombre}]::keybd_event"
    sep = ", " if len(teclas) > 1 else ","  # combinaciones llevan espacios (formato original)
    abajo = "; ".join(f"{llamada}(0x{t:02X}{sep}0{sep}0{sep}0)" for t in teclas)
    arriba = "; ".join(f"{llamada}(0x{t:02X}{sep}0{sep}2{sep}0)" for t in reversed(teclas))
    cuerpo = f"{abajo}; {arriba};"
    if repetir > 1:
        cuerpo = f"1..{repetir} | ForEach-Object {{ {cuerpo} Start-Sleep -Milliseconds 20 }}"
    _ps(previo + _DECLARAR_TECLADO.format(nombre=nombre, ns=ns) + cuerpo)


def _enviar(teclas: str):
    _ps_corto(f"{_SHELL}.SendKeys('{teclas}')")


def _activar(ventana: str):
    _ps_corto(f"{_SHELL}.AppActivate('{ventana}')")


def _abrir_web(url: str):
    webbrowser.open(url)
    _activar("Microsoft Edge")


def _brillo(subir: bool):
    if subir:
        _ps(_BRILLO.format(fn="Min", lim=100, op="+"))
    else:
        _ps(_BRILLO.format(fn="Max", lim=0, op="-"))


def _vscode():
    _cmd("code")
    _activar("Visual Studio Code")


_NUEVO_SHELL = "New-Object -ComObject WScript.Shell"
_SHIFT_N = f"$ws = {_NUEVO_SHELL}; $ws.SendKeys('+n'); "
_SHIFT_P = f"$ws = {_NUEVO_SHELL}; $ws.SendKeys('+p'); "

# accion -> (función sin argumentos, mensaje de respuesta)
ACCIONES = {
    "musica": (lambda: _abrir_web(_URL_MUSICA), "Playlist activada al frente"),
    "chapa": (lambda: _abrir_web(_URL_CHAPA), "Chapa activada al frente"),
    "local_tunes": (lambda: _abrir_web("https://local-tunes.netlify.app"),
                    "Local Tunes abierto al frente"),
    "play_pause": (lambda: _ps(f"$wscript = {_NUEVO_SHELL}; $wscript.SendKeys([char]179)"),
                   "Play / Pausa"),
    "next": (lambda: _teclas("W1", "U1", [0xB0], previo=_SHIFT_N), "Siguiente video / pista"),
    "prev": (lambda: _teclas("W2", "U2", [0xB1], previo=_SHIFT_P), "Video / pista anterior"),
    "vol_up": (lambda: _teclas("W3", "U3", [0xAF], repetir=5), "Volumen +10"),
    "vol_down": (lambda: _teclas("W4", "U4", [0xAE], repetir=5), "Volumen -10"),
    "mute": (lambda: _teclas("W5", "U5", [0xAD]), "Volumen Silenciado"),
    "alt_tab": (lambda: _teclas("WTab", "WT", [0x12, 0x09]), "Cambiando de App"),
    "cerrar_app": (lambda: _teclas("WClose", "WC", [0x12, 0x73]), "Ventana cerrada"),
    "escritorio": (lambda: _teclas("WDesk", "WD", [0x5B, 0x44]), "Escritorio mostrado"),
    "nueva_pestana": (lambda: _enviar("^t"), "Nueva pestaña abierta"),
    "next_tab": (lambda: _enviar("^{TAB}"), "Siguiente pestaña"),
    "prev_tab": (lambda: _enviar("^+{TAB}"), "Pestaña anterior"),
    "cerrar_pestana": (lambda: _enviar("^w"), "Pestaña cerrada"),
    "task_manager": (lambda: _enviar("^+{ESC}"), "Administrador de Tareas abierto"),
    "fortnite": (lambda: _cmd(r"start shell:AppsFolder\436609B6.FortniteClient_9ncxwbgmmv7m8"
                              r"!AppFortniteShipping"), "Abriendo Fortnite"),
    "roblox": (lambda: _cmd(r"start shell:AppsFolder\ROBLOXCorporation.RobloxGDK_55nm5eh3cm0pr"
                            r"!Game"), "Abriendo Roblox"),
    "edge": (lambda: _cmd("start msedge"), "Edge abierto"),
    "vscode": (_vscode, "VS Code abierto al frente"),
    "teams": (lambda: _cmd("start msteams:"), "Teams abierto"),
    "bloquear": (lambda: _cmd("rundll32.exe user32.dll,LockWorkStation"), "PC bloqueada"),
    "terminal": (lambda: _cmd("wt"), "Terminal abierta"),
    "brillo_up": (lambda: _brillo(True), "Brillo aumentado"),
    "brillo_down": (lambda: _brillo(False), "Brillo reducido"),
}


def ejecutar(accion: str):
    """Ejecuta la acción. Devuelve el mensaje, o None si no existe."""
    entrada = ACCIONES.get(accion)
    if entrada is None:
        return None
    funcion, mensaje = entrada
    funcion()
    return mensaje
