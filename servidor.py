"""
servidor.py — El ÚNICO servidor web de A.Z.M.U.T.H.
"""
import os
import subprocess
import webbrowser

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

import estado

app = FastAPI()

# Montamos la carpeta de imágenes para que estén accesibles por URL (ej: /imagenes/Fuego.png)
_RUTA_IMAGENES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagenes")
if os.path.exists(_RUTA_IMAGENES):
    app.mount("/imagenes", StaticFiles(directory=_RUTA_IMAGENES), name="imagenes")

_RUTA_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "azmuth.html")


@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open(_RUTA_HTML, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: No se encontró el archivo 'azmuth.html' en la raíz del proyecto.</h1>"


@app.get("/estado")
def obtener_estado():
    return estado.obtener_estado()


def _terminar(mensaje: str, status: str = "ok"):
    estado.log(f"[remoto] {mensaje}")
    return {"status": status, "mensaje": mensaje}


@app.get("/comando")
def ejecutar_accion(accion: str):
    accion = accion.lower().strip()
    estado.set_estado("ejecutando", f"Comando remoto: {accion}")

    if accion == "musica":
        webbrowser.open("https://www.youtube.com/watch?v=pMNhe03RKZE&list=PLTEsV4ouHz8U&index=2")
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).AppActivate('Microsoft Edge')\"", shell=True)
        return _terminar("Playlist activada al frente")
    elif accion == "chapa":
        webbrowser.open("https://www.youtube.com/watch?v=qD9uZp9TyR8&list=RDqD9uZp9TyR8&start_radio=1")
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).AppActivate('Microsoft Edge')\"", shell=True)
        return _terminar("Chapa activada al frente")
    elif accion == "play_pause":
        subprocess.run(["powershell", "-command", "$wscript = New-Object -ComObject WScript.Shell; $wscript.SendKeys([char]179)"], shell=True)
        return _terminar("Play / Pausa")
    elif accion == "next":
        ps = "$ws = New-Object -ComObject WScript.Shell; $ws.SendKeys('+n'); $code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'W1' -Namespace 'U1'; [U1.W1]::keybd_event(0xB0,0,0,0); [U1.W1]::keybd_event(0xB0,0,2,0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Siguiente video / pista")
    elif accion == "prev":
        ps = "$ws = New-Object -ComObject WScript.Shell; $ws.SendKeys('+p'); $code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'W2' -Namespace 'U2'; [U2.W2]::keybd_event(0xB1,0,0,0); [U2.W2]::keybd_event(0xB1,0,2,0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Video / pista anterior")
    elif accion == "vol_up":
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'W3' -Namespace 'U3'; 1..5 | ForEach-Object { [U3.W3]::keybd_event(0xAF,0,0,0); [U3.W3]::keybd_event(0xAF,0,2,0); Start-Sleep -Milliseconds 20 }"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Volumen +10")
    elif accion == "vol_down":
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'W4' -Namespace 'U4'; 1..5 | ForEach-Object { [U4.W4]::keybd_event(0xAE,0,0,0); [U4.W4]::keybd_event(0xAE,0,2,0); Start-Sleep -Milliseconds 20 }"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Volumen -10")
    elif accion == "mute":
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'W5' -Namespace 'U5'; [U5.W5]::keybd_event(0xAD,0,0,0); [U5.W5]::keybd_event(0xAD,0,2,0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Volumen Silenciado")
    elif accion == "alt_tab":
        # Simulación robusta de Alt + Tab para ciclar entre aplicaciones sin trabarse
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'WTab' -Namespace 'WT'; [WT.WTab]::keybd_event(0x12, 0, 0, 0); [WT.WTab]::keybd_event(0x09, 0, 0, 0); [WT.WTab]::keybd_event(0x09, 0, 2, 0); [WT.WTab]::keybd_event(0x12, 0, 2, 0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Cambiando de App")
    elif accion == "nueva_pestana":
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).SendKeys('^t')\"", shell=True)
        return _terminar("Nueva pestaña abierta")
    elif accion == "next_tab":
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).SendKeys('^{TAB}')\"", shell=True)
        return _terminar("Siguiente pestaña")
    elif accion == "prev_tab":
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).SendKeys('^+{TAB}')\"", shell=True)
        return _terminar("Pestaña anterior")
    elif accion == "fortnite":
        subprocess.run(r"start shell:AppsFolder\436609B6.FortniteClient_9ncxwbgmmv7m8!AppFortniteShipping", shell=True)
        return _terminar("Abriendo Fortnite")
    elif accion == "roblox":
        subprocess.run(r"start shell:AppsFolder\ROBLOXCorporation.RobloxGDK_55nm5eh3cm0pr!Game", shell=True)
        return _terminar("Abriendo Roblox")
    elif accion == "edge":
        subprocess.run("start msedge", shell=True)
        return _terminar("Edge abierto")
    elif accion == "vscode":
        subprocess.run("code", shell=True)
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).AppActivate('Visual Studio Code')\"", shell=True)
        return _terminar("VS Code abierto al frente")
    elif accion == "teams":
        subprocess.run("start msteams:", shell=True)
        return _terminar("Teams abierto")
    elif accion == "cerrar_pestana":
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).SendKeys('^w')\"", shell=True)
        return _terminar("Pestaña cerrada")
    elif accion == "cerrar_app":
        # Simulación nativa exacta de Alt + F4 para cerrar cualquier ventana activa de forma universal
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'WClose' -Namespace 'WC'; [WC.WClose]::keybd_event(0x12, 0, 0, 0); [WC.WClose]::keybd_event(0x73, 0, 0, 0); [WC.WClose]::keybd_event(0x73, 0, 2, 0); [WC.WClose]::keybd_event(0x12, 0, 2, 0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Ventana cerrada")
    elif accion == "bloquear":
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return _terminar("PC bloqueada")
    elif accion == "task_manager":
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).SendKeys('^+{ESC}')\"", shell=True)
        return _terminar("Administrador de Tareas abierto")
    elif accion == "terminal":
        subprocess.run("wt", shell=True)
        return _terminar("Terminal abierta")
    elif accion == "escritorio":
        # Atajo exacto Win + D mediante PowerShell para mostrar/ocultar el escritorio de forma infalible
        ps = "$code = '[DllImport(\"user32.dll\")] public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);'; Add-Type -MemberDefinition $code -Name 'WDesk' -Namespace 'WD'; [WD.WDesk]::keybd_event(0x5B, 0, 0, 0); [WD.WDesk]::keybd_event(0x44, 0, 0, 0); [WD.WDesk]::keybd_event(0x44, 0, 2, 0); [WD.WDesk]::keybd_event(0x5B, 0, 2, 0);"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Escritorio mostrado")
    elif accion == "brillo_up":
        ps = "$b = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods); if ($b) { $curr = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness; $b.WmiSetBrightness(1, [Math]::Min(100, $curr + 15)) }"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Brillo aumentado")
    elif accion == "brillo_down":
        ps = "$b = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods); if ($b) { $curr = (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness; $b.WmiSetBrightness(1, [Math]::Max(0, $curr - 15)) }"
        subprocess.run(["powershell", "-command", ps], shell=True)
        return _terminar("Brillo reducido")
    elif accion == "local_tunes":
        webbrowser.open("https://local-tunes.netlify.app")
        subprocess.run("powershell -command \"(New-Object -ComObject WScript.Shell).AppActivate('Microsoft Edge')\"", shell=True)
        return _terminar("Local Tunes abierto al frente")

    estado.set_estado("reposo")
    return _terminar(f"Comando '{accion}' no reconocido", status="error")


@app.get("/reloj", response_class=HTMLResponse)
def vista_reloj():
    html_reloj = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>Omnitrix Watch</title>
        <style>
            body {
                background-color: #010d06;
                color: #4ade80;
                font-family: 'Courier New', Courier, monospace;
                margin: 0;
                padding: 6px 0 0 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: flex-start;
                height: 100vh;
                box-sizing: border-box;
                overflow-y: auto;
            }
            #status {
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
                margin-bottom: 4px;
                color: #facc15;
                text-shadow: 0 0 6px rgba(250, 204, 21, 0.9);
                text-align: center;
                width: 100%;
                letter-spacing: 1px;
            }
            #menu-view {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 5px;
                width: 175px;
                max-height: 195px;
                overflow-y: auto;
                padding: 2px;
                align-items: center;
                justify-items: center;
            }
            .menu-btn {
                background-color: #022c14;
                border: 1.5px solid #22c55e;
                color: #4ade80;
                font-size: 9.5px;
                font-weight: bold;
                padding: 8px 4px;
                width: 100%;
                height: 44px;
                border-radius: 7px;
                cursor: pointer;
                text-transform: uppercase;
                text-align: center;
                box-shadow: 0 0 5px rgba(34, 197, 94, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                box-sizing: border-box;
            }
            .menu-btn:active {
                background-color: #22c55e;
                color: #000;
            }

            #dial-view {
                display: none;
                flex-direction: column;
                align-items: center;
            }
            .back-btn {
                background: none;
                border: none;
                color: #facc15;
                font-size: 12px;
                font-weight: bold;
                cursor: pointer;
                margin-bottom: 4px;
                text-transform: uppercase;
                text-shadow: 0 0 6px rgba(250, 204, 21, 0.9);
            }
            .watch-wrapper {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 4px;
                width: 100%;
                max-width: 220px;
            }
            .nav-btn {
                background-color: rgba(2, 44, 20, 0.9);
                border: 1.5px solid #22c55e;
                color: #4ade80;
                font-size: 16px;
                font-weight: bold;
                width: 28px;
                height: 55px;
                border-radius: 6px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 0 6px rgba(34, 197, 94, 0.3);
                z-index: 5;
            }
            .nav-btn:active {
                background-color: #22c55e;
                color: #000;
            }
            .dial-container {
                position: relative;
                width: 155px;
                height: 155px;
                border: 3px solid #22c55e;
                border-radius: 50%;
                background: radial-gradient(circle, #032d14 0%, #011208 85%);
                box-shadow: 0 0 12px rgba(34, 197, 94, 0.6), inset 0 0 8px rgba(34, 197, 94, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: hidden;
            }
            .dial-track {
                display: flex;
                transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1);
                width: 100%;
                height: 100%;
                align-items: center;
            }
            .dial-item {
                min-width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                user-select: none;
                padding: 2px;
                box-sizing: border-box;
            }
            .dial-item img {
                width: 85px;
                height: 85px;
                object-fit: contain;
                margin-bottom: 2px;
                filter: drop-shadow(0 0 8px #22c55e);
            }
            .alien-name {
                font-size: 12px;
                font-weight: bold;
                color: #a7f3d0;
                text-transform: uppercase;
                margin-bottom: 1px;
                text-shadow: 0 0 5px rgba(167, 243, 208, 0.7);
            }
            .action-label {
                font-size: 10px;
                font-weight: bold;
                color: #facc15;
                background: rgba(0, 0, 0, 0.85);
                padding: 2px 7px;
                border-radius: 6px;
                border: 1px solid #15803d;
                text-transform: uppercase;
                white-space: nowrap;
                text-shadow: 0 0 3px rgba(250, 204, 21, 0.6);
            }
        </style>
    </head>
    <body>
        <div id="status">OMNITRIX READY</div>

        <!-- 1. MENÚ PRINCIPAL EN CUADRÍCULA (2 COLUMNAS) -->
        <div id="menu-view">
            <button class="menu-btn" onclick="openSection('multimedia')">Multimedia</button>
            <button class="menu-btn" onclick="openSection('volumen')">Volumen</button>
            <button class="menu-btn" onclick="openSection('videojuegos')">Videojuegos</button>
            <button class="menu-btn" onclick="openSection('sistema')">Sistema</button>
            <button class="menu-btn" onclick="openSection('herramientas')">Herramientas</button>
            <button class="menu-btn" onclick="openSection('navegador')">Pestañas</button>
        </div>

        <!-- 2. VISTA DEL DIAL FILTRADO POR SECCIÓN -->
        <div id="dial-view">
            <button class="back-btn" onclick="goBack()">◄ Volver</button>
            <div class="watch-wrapper">
                <button class="nav-btn" onclick="girarDial(-1)">‹</button>
                <div class="dial-container" id="dialContainer">
                    <div class="dial-track" id="dialTrack">
                        <!-- Las opciones se cargarán dinámicamente -->
                    </div>
                </div>
                <button class="nav-btn" onclick="girarDial(1)">›</button>
            </div>
        </div>

        <script>
            const sectionsData = {
                multimedia: [
                    {img: "Fuego.png", name: "Fuego", action: "Mix Playlist", cmd: "musica"},
                    {img: "Ditto.png", name: "Ditto", action: "Play / Pausa", cmd: "play_pause"},
                    {img: "Xrl8.png", name: "XLR8", action: "Siguiente", cmd: "next"},
                    {img: "clockwark.png", name: "clockwork", action: "Anterior", cmd: "prev"},
                    {img: "Ultra_T.png", name: "Ultra T", action: "Menea Chapa", cmd: "chapa"}
                ],
                volumen: [
                    {img: "eco-eco.png", name: "eco eco", action: "Volumen +", cmd: "vol_up"},
                    {img: "Materia_gris.png", name: "Materia Gris", action: "Volumen -", cmd: "vol_down"},
                    {img: "Fantasmatico.png", name: "Fantasmático", action: "Silenciar", cmd: "mute"}
                ],
                videojuegos: [
                    {img: "jury-rigg.png", name: "Jury Rigg", action: "Fortnite", cmd: "fortnite"},
                    {img: "Ditto.png", name: "Ditto", action: "Roblox", cmd: "roblox"}
                ],
                sistema: [
                    {img: "Muy_grande.png", name: "Muy Grande", action: "Bloquear PC", cmd: "bloquear"},
                    {img: "Xrl8.png", name: "XLR8", action: "Cerrar Ventana", cmd: "cerrar_app"},
                    {img: "Ultra_T.png", name: "Ultra T", action: "Cambiar App", cmd: "alt_tab"},
                    {img: "Materia_gris.png", name: "Intelec-T", action: "VS Code", cmd: "vscode"},
                    {img: "Fuego.png", name: "Fuego", action: "Edge", cmd: "edge"},
                    {img: "Fantasmatico.png", name: "Fantasmático", action: "Teams", cmd: "teams"}
                ],
                herramientas: [
                    {img: "nanomech.png", name: "Nanomech", action: "Task Manager", cmd: "task_manager"},
                    {img: "Ultra_T.png", name: "Eco Eco", action: "Abrir Terminal", cmd: "terminal"},
                    {img: "Muy_grande.png", name: "Cannonbolt", action: "Escritorio", cmd: "escritorio"},
                    {img: "Fuego.png", name: "Fuego", action: "Brillo +", cmd: "brillo_up"},
                    {img: "Fantasmatico.png", name: "Fantasmático", action: "Brillo -", cmd: "brillo_down"}
                ],
                navegador: [
                    {img: "Diamante.png", name: "Diamante", action: "Nueva Pestaña", cmd: "nueva_pestana"},
                    {img: "Xrl8.png", name: "XLR8", action: "Cerrar Pestaña", cmd: "cerrar_pestana"},
                    {img: "Ultra_T.png", name: "Ultra T", action: "Sig Pestaña", cmd: "next_tab"},
                    {img: "Fedback.png", name: "Feedback", action: "Ant Pestaña", cmd: "prev_tab"}
                ]
            };

            let currentIndex = 0;
            let currentItems = [];

            function openSection(sectionKey) {
                document.getElementById('menu-view').style.display = 'none';
                document.getElementById('dial-view').style.display = 'flex';
                
                currentItems = sectionsData[sectionKey];
                currentIndex = 0;
                renderDial();
            }

            function goBack() {
                document.getElementById('dial-view').style.display = 'none';
                document.getElementById('menu-view').style.display = 'grid';
            }

            function renderDial() {
                const track = document.getElementById('dialTrack');
                track.innerHTML = '';
                currentItems.forEach(item => {
                    track.innerHTML += `
                        <div class="dial-item" onclick="cmd('${item.cmd}')">
                            <img src="/imagenes/${item.img}" alt="${item.name}">
                            <div class="alien-name">${item.name}</div>
                            <div class="action-label">${item.action}</div>
                        </div>
                    `;
                });
                track.style.transform = `translateX(0px)`;
            }

            function girarDial(direction) {
                if (currentItems.length === 0) return;
                currentIndex = (currentIndex + direction + currentItems.length) % currentItems.length;
                const track = document.getElementById('dialTrack');
                track.style.transform = `translateX(-${currentIndex * 100}%)`;
            }

            let touchStartX = 0;
            const container = document.getElementById('dialContainer');

            container.addEventListener('touchstart', e => {
                touchStartX = e.touches[0].clientX;
            });

            container.addEventListener('touchend', e => {
                let touchEndX = e.changedTouches[0].clientX;
                if (touchStartX - touchEndX > 25) {
                    girarDial(1);
                } else if (touchEndX - touchStartX > 25) {
                    girarDial(-1);
                }
            });

            function cmd(accion) {
                const statusEl = document.getElementById('status');
                statusEl.innerText = "ACTIVANDO...";
                statusEl.style.color = "#22d3ee";
                
                fetch('/comando?accion=' + accion)
                    .then(r => r.json())
                    .then(data => {
                        statusEl.innerText = "¡TRANSFORMADO!";
                        statusEl.style.color = "#facc15";
                        setTimeout(() => { statusEl.innerText = "OMNITRIX READY"; }, 1500);
                    })
                    .catch(err => {
                        statusEl.innerText = "ERROR";
                        statusEl.style.color = "#ef4444";
                        setTimeout(() => { statusEl.innerText = "OMNITRIX READY"; statusEl.style.color = "#facc15"; }, 2000);
                    });
            }
        </script>
    </body>
    </html>
    """
    return html_reloj