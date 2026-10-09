"""
servidor.py — El ÚNICO servidor web de A.Z.M.U.T.H.
"""
import os
import threading

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import acciones_remotas
import chats
import config
import estado
import idioma
import monitoreo
import rutas
import tematicas

app = FastAPI()

# Script que se inyecta en las páginas: guarda el token que venga en la URL
# (?token=...) y lo manda en cada fetch como cabecera X-Azmuth-Token.
_JS_TOKEN = """<script>
(function () {
  const q = new URLSearchParams(location.search).get('token');
  try { if (q) localStorage.setItem('azmuthToken', q); } catch (e) {}
  let t = q; try { t = t || localStorage.getItem('azmuthToken'); } catch (e) {}
  if (!t) return;
  const original = window.fetch;
  window.fetch = (url, op = {}) => {
    op.headers = Object.assign({}, op.headers, { 'X-Azmuth-Token': t });
    return original(url, op);
  };
})();
</script>"""


def _viene_de_internet(request) -> bool:
    """Ngrok reenvía a 127.0.0.1 pero agrega X-Forwarded-For; la ventana local no."""
    return "x-forwarded-for" in request.headers or "ngrok-trace-id" in request.headers


def _token_valido(request) -> bool:
    import hmac
    dado = (request.headers.get("x-azmuth-token") or request.query_params.get("token")
            or request.cookies.get(_COOKIE) or "")
    return hmac.compare_digest(dado, config.TOKEN_REMOTO)


_COOKIE = "azmuth_token"
# Las imágenes del Omnitrix son públicas: un <img> no puede mandar la cabecera
# del token (DEF-017: salían rotas las que no estaban en caché).
_RUTAS_PUBLICAS = ("/imagenes/",)


@app.middleware("http")
async def _proteger_acceso_remoto(request, call_next):
    if not config.TOKEN_REMOTO or not _viene_de_internet(request):
        return await call_next(request)
    if request.url.path.startswith(_RUTAS_PUBLICAS):
        return await call_next(request)
    if not _token_valido(request):
        monitoreo.registrar_evento(f"Acceso remoto rechazado: {request.method} {request.url.path}")
        return JSONResponse(status_code=401, content={"status": "error", "mensaje": "Token inválido"})
    respuesta = await call_next(request)
    if request.query_params.get("token"):
        # Recordar el token en el celular/reloj: así las imágenes y recargas también pasan
        respuesta.set_cookie(_COOKIE, config.TOKEN_REMOTO, max_age=31_536_000,
                             httponly=True, secure=True, samesite="lax")
    return respuesta

# Montamos la carpeta de imágenes para que estén accesibles por URL (ej: /imagenes/Fuego.png)
_RUTA_IMAGENES = os.path.join(rutas.CARPETA_RECURSOS, "imagenes")
if os.path.exists(_RUTA_IMAGENES):
    app.mount("/imagenes", StaticFiles(directory=_RUTA_IMAGENES), name="imagenes")

_RUTA_HTML = os.path.join(rutas.CARPETA_RECURSOS, "azmuth.html")


@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open(_RUTA_HTML, "r", encoding="utf-8") as f:
            return f.read().replace("<script>", _JS_TOKEN + "\n    <script>", 1)
    except FileNotFoundError:
        return "<h1>Error: No se encontró el archivo 'azmuth.html' en la raíz del proyecto.</h1>"


@app.get("/estado")
def obtener_estado():
    return estado.obtener_estado()


@app.exception_handler(Exception)
async def _error_no_controlado(request: Request, error: Exception):
    """Cualquier fallo de un endpoint queda en datos/errores.log (monitoreo)."""
    monitoreo.registrar_error(f"{request.method} {request.url.path}", error)
    return JSONResponse(status_code=500, content={"status": "error", "mensaje": "Error interno"})


class CambioIdioma(BaseModel):
    idioma: str


@app.get("/idioma")
def ver_idioma():
    return {"idioma": idioma.obtener(), "disponibles": list(idioma.IDIOMAS)}


@app.post("/idioma")
def cambiar_idioma(datos: CambioIdioma):
    if datos.idioma not in idioma.IDIOMAS:
        raise HTTPException(status_code=400, detail="Idioma no soportado")
    return {"idioma": idioma.cambiar(datos.idioma)}


class CambioTematica(BaseModel):
    tematica: str


@app.get("/tematica")
def ver_tematica():
    return {"tematica": tematicas.obtener(), "preferencia": tematicas.preferencia(),
            "disponibles": ["auto", *tematicas.TEMAS]}


@app.post("/tematica")
def cambiar_tematica(datos: CambioTematica):
    if datos.tematica != "auto" and datos.tematica not in tematicas.TEMAS:
        raise HTTPException(status_code=400, detail="Temática no soportada")
    activa = tematicas.cambiar(datos.tematica)
    threading.Thread(target=tematicas.reproducir_sonido, daemon=True).start()
    return {"tematica": activa, "preferencia": tematicas.preferencia()}


@app.get("/salud")
def salud():
    """Monitoreo: tiempo activo y últimos errores registrados."""
    return {"status": "ok", "control_remoto_protegido": bool(config.TOKEN_REMOTO), **monitoreo.resumen()}


# ====================== MODO ESCRITORIO (chat escrito) ======================
# nucleo y voice se importan dentro de las funciones a propósito: cargan las
# skills (pyautogui, etc.), que solo existen en Windows. Así este servidor
# sigue arrancando en el contenedor Docker del pipeline para la prueba de humo.

class CambioModo(BaseModel):
    modo: str


class NuevoMensaje(BaseModel):
    texto: str


class Renombrar(BaseModel):
    titulo: str


class VozChat(BaseModel):
    activa: bool


@app.get("/modo")
def ver_modo():
    return {"modo": estado.obtener_modo(), "voz_chat": chats.obtener_ajuste("voz_chat", "1") == "1"}


@app.post("/modo")
def cambiar_modo(datos: CambioModo):
    if datos.modo not in ("voz", "escritorio"):
        raise HTTPException(400, "Modo inválido: usa 'voz' o 'escritorio'")
    modo = estado.set_modo(datos.modo)
    estado.log(f"Modo {modo} activado")
    return {"modo": modo}


@app.post("/voz_chat")
def cambiar_voz_chat(datos: VozChat):
    chats.guardar_ajuste("voz_chat", "1" if datos.activa else "0")
    return {"voz_chat": datos.activa}


@app.get("/chats")
def ver_chats():
    return {"chats": chats.listar_chats(), "activo": chats.obtener_activo(crear_si_no_hay=False)}


@app.post("/chats")
def nuevo_chat():
    # Si ya hay un chat vacío, se reutiliza en vez de llenar la lista de "Nuevo chat"
    vacio = next((c for c in chats.listar_chats() if c["mensajes"] == 0), None)
    if vacio:
        chats.fijar_activo(vacio["id"])
        return {"id": vacio["id"]}
    return {"id": chats.crear_chat()}


def _chat_o_404(chat_id: int):
    if not chats.existe(chat_id):
        raise HTTPException(404, "Ese chat no existe")


@app.post("/chats/{chat_id}/activar")
def activar_chat(chat_id: int):
    _chat_o_404(chat_id)
    chats.fijar_activo(chat_id)
    return {"activo": chat_id}


@app.patch("/chats/{chat_id}")
def renombrar_chat(chat_id: int, datos: Renombrar):
    _chat_o_404(chat_id)
    return {"titulo": chats.renombrar_chat(chat_id, datos.titulo)}


@app.delete("/chats/{chat_id}")
def borrar_chat(chat_id: int):
    _chat_o_404(chat_id)
    chats.borrar_chat(chat_id)
    return {"borrado": chat_id}


@app.get("/chats/{chat_id}/mensajes")
def ver_mensajes(chat_id: int):
    _chat_o_404(chat_id)
    return {"mensajes": chats.obtener_mensajes(chat_id)}


@app.post("/chats/{chat_id}/mensajes")
def enviar_mensaje(chat_id: int, datos: NuevoMensaje):
    texto = (datos.texto or "").strip()
    if not texto:
        raise HTTPException(400, "El mensaje está vacío")
    _chat_o_404(chat_id)
    import nucleo
    estado.log(f"USTED (texto): {texto[:100]}")
    estado.set_estado("procesando", texto)
    try:
        respuesta, categoria, chat_id = nucleo.responder_en_chat(texto, chat_id, origen="texto")
    finally:
        estado.set_estado("reposo")
    estado.log(f"AZMUTH (texto): {respuesta[:100]}")
    if chats.obtener_ajuste("voz_chat", "1") == "1":
        threading.Thread(target=_hablar_en_segundo_plano, args=(respuesta,), daemon=True).start()
    return {"respuesta": respuesta, "categoria": categoria, "chat_id": chat_id, "modo": estado.obtener_modo()}


def _hablar_en_segundo_plano(respuesta: str):
    try:
        import voice
        voice.hablar(voice.texto_para_voz(respuesta))
    except Exception as e:
        estado.log(f"[voz] {e}")


def _terminar(mensaje: str, status: str = "ok"):
    estado.log(f"[remoto] {mensaje}")
    return {"status": status, "mensaje": mensaje}


@app.get("/comando")
def ejecutar_accion(accion: str):
    accion = accion.lower().strip()
    estado.set_estado("ejecutando", f"Comando remoto: {accion}")
    mensaje = acciones_remotas.ejecutar(accion)
    if mensaje is not None:
        return _terminar(mensaje)
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

        """ + _JS_TOKEN + """
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
