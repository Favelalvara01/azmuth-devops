"""
Skill: abrir y cerrar aplicaciones, y sitios web.
Esta es la gran diferencia frente a la versión de navegador: como este
programa corre directo en Windows, sí puede abrir programas de verdad.

¿No encuentra una app que quieres? Agrégala tú mismo abajo, en el
diccionario APPS — es solo una línea nueva. Instrucciones en AGENTE.md.
"""
import re
import os
import subprocess
import webbrowser
import unicodedata
from urllib.parse import quote

# nombre por el que le hablas -> objetivo real que se le pasa a Windows
APPS = {
    "bloc de notas": "notepad",
    "notepad": "notepad",
    "calculadora": "calc",
    "explorador de archivos": "explorer",
    "explorador": "explorer",
    "paint": "mspaint",
    "edge": "msedge",
    "microsoft edge": "msedge",
    "navegador": "msedge",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "spotify": "spotify",
    "configuración": "ms-settings:",
    "xbox": "powershell -Command Start-Process 'XboxPcAppCE.exe'",
    "fortnite": r'shell:AppsFolder\436609B6.FortniteClient_9ncxwbgmmv7m8!AppFortniteShipping',
    "rocket league": "com.epicgames.launcher://apps/rl?action=launch&silent=true",
    "roblox": r"shell:AppsFolder\ROBLOXCorporation.RobloxGDK_55nm5eh3cm0pr!Game",
    "whatsapp": "whatsapp:",
    "teams": "msteams:",
    "microsoft teams": "msteams:",
    "visual studio code": "code",
    "vs code": "code",
    "vscode": "code",
    "android studio": r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
    "localito": "https://local-tunes.netlify.app",
    "local betta": "https://lerma-dev.github.io/local-tunes",
    "local beta": "https://lerma-dev.github.io/local-tunes",
}

# Procesos reales de Windows para cerrar
PROCESOS_CIERRE = {
    "bloc de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "ApplicationFrameHost.exe",
    "explorador de archivos": "powershell -Command \"$wshell = New-Object -ComObject Shell.Application; foreach ($w in $wshell.Windows()) { if ($w.Name -eq 'File Explorer' -or $w.Name -eq 'Explorador de archivos') { $w.Quit() } }\"",
    "explorador": "powershell -Command \"$wshell = New-Object -ComObject Shell.Application; foreach ($w in $wshell.Windows()) { if ($w.Name -eq 'File Explorer' -or $w.Name -eq 'Explorador de archivos') { $w.Quit() } }\"",
    "paint": "mspaint.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "navegador": "msedge.exe",
    "spotify": "Spotify.exe",
    "visual studio code": "Code.exe",
    "vs code": "Code.exe",
    "vscode": "Code.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "xbox": "Xbox.exe",
    "teams": "ms-teams.exe",
    "microsoft teams": "ms-teams.exe",
    "configuración": "SystemSettings.exe",
    "fortnite": "FortniteClient-Win64-Shipping.exe",
    "whatsapp": "powershell -Command \"Get-Process | Where-Object { $_.Name -like '*whatsapp*' } | Stop-Process -Force\"",
}

_ARTICULOS_RE = re.compile(r"^(?:el|la|los|las|un|una|unos|unas)\s+")

_PALABRAS_YOUTUBE_RE = re.compile(
    r"\b(?:abre|ábreme|abrir|busca|búscame|en|y|youtube|por favor)\b", re.IGNORECASE
)


def limpiar_texto_voz(texto: str) -> str:
    """Quita acentos, pasa a minúsculas y elimina signos de puntuación extra."""
    if not texto:
        return ""
    t = texto.lower()
    t = ''.join(
        c for c in unicodedata.normalize('NFD', t)
        if unicodedata.category(c) != 'Mn'
    )
    t = re.sub(r'[^\w\s]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _limpiar_nombre(nombre: str) -> str:
    return _ARTICULOS_RE.sub("", nombre).strip()


def _abrir_simple(objetivo: str):
    try:
        if objetivo.startswith("http://") or objetivo.startswith("https://"):
            webbrowser.open(objetivo)
            return None
        if "powershell" in objetivo.lower():
            subprocess.run(objetivo, shell=True, check=True)
            return None
        os.startfile(objetivo)
        return None
    except Exception as e1:
        try:
            subprocess.run(
                ["cmd", "/c", "start", "", objetivo],
                check=True, capture_output=True, text=True,
            )
            return None
        except Exception as e2:
            return f"{e1} / {e2}"


def intentar(texto: str):
    if not texto:
        return None

    # Limpiamos el texto de voz aquí: adiós acentos, mayúsculas y comas
    t = limpiar_texto_voz(texto)

    # --- MODO RICKROLL ---
    if any(k in t for k in ("rick roll", "rickroll", "rick astley")):
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        return "Activando modo Rickroll."

    # --- MODO MENEA TU CHAPA ---
    if "menea tu chapa" in t:
        url_chapa = "https://www.youtube.com/watch?v=qD9uZp9TyR8&list=RDqD9uZp9TyR8&start_radio=1"
        webbrowser.open(url_chapa)
        return "Activando modo Menea tu chapa. ¡A bailar!"

    # --- MODO AZMUTH MIX (Tu playlist oficial de YouTube) ---
    if any(k in t for k in ("azmuth mix", "mi musica", "mix personal", "pon mi musica", "aleatorio")):
        url_playlist = "https://www.youtube.com/watch?v=pMNhe03RKZE&list=PLTEsV4ouHz8U&index=2"
        webbrowser.open(url_playlist)
        return "Activando tu playlist"

    # --- CERRAR APLICACIONES ---
    m_cerrar = re.match(r"^(?:cierra|cierrame|cerrar)\s+(.+)", t)
    if m_cerrar:
        app_pedida = _limpiar_nombre(m_cerrar.group(1).strip())
        proceso = PROCESOS_CIERRE.get(app_pedida)
        if proceso:
            try:
                if "powershell" in proceso.lower():
                    subprocess.run(proceso, shell=True, check=False, capture_output=True, text=True)
                else:
                    subprocess.run(["taskkill", "/f", "/im", proceso], check=False, capture_output=True, text=True)
                return f"Cerrando {app_pedida}."
            except Exception as e:
                print(f"[aplicaciones] Error al cerrar {app_pedida}: {e}")
                return f"No pude cerrar {app_pedida}. Es probable que no esté abierta."
        return f'No tengo registrado el proceso para cerrar "{app_pedida}".'

    # --- BUSCAR DIRECTAMENTE EN YOUTUBE ---
    if "youtube" in t and any(v in t for v in ("abre", "abreme", "abrir", "busca", "buscame")):
        consulta_limpia = _PALABRAS_YOUTUBE_RE.sub("", t).strip()
        consulta_limpia = re.sub(r"\s+", " ", consulta_limpia)

        if len(consulta_limpia) > 1:
            url = f"https://www.youtube.com/results?search_query={quote(consulta_limpia)}"
        else:
            url = f"https://www.youtube.com"

        webbrowser.open(url)
        if len(consulta_limpia) > 1:
            return f'Abriendo YouTube y buscando "{consulta_limpia}".'
        return "Le abro YouTube."

    # --- MESSENGER ---
    if "messenger" in t and any(v in t for v in ("abre", "abreme", "abrir")):
        webbrowser.open("https://www.messenger.com")
        return "Le abro Messenger. Ahí busca al contacto y manda el mensaje usted mismo — no tengo acceso a sus contactos."

    # --- APERTURA POR NOMBRE ---
    if any(v in t for v in ("abre", "abreme", "abrir")):
        for nombre_app in APPS.keys():
            if nombre_app in t:
                comando = APPS[nombre_app]
                error = _abrir_simple(comando)
                if error is None:
                    return f"Abriendo {nombre_app}."
                print(f"[aplicaciones] Error al abrir {nombre_app!r} ({comando!r}): {error}")
                return f"Intenté abrir {nombre_app} pero Windows no pudo."

    return None