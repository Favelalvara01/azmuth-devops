import os
import sys
import threading
import time

# --- Redirigir stdout/stderr si no hay consola (se ejecuta con pythonw) ---
# Bajo pythonw.exe, sys.stdout y sys.stderr son None (no hay consola). Como
# config.py y otros módulos usan print() para avisos (ej. si falta una API
# key en .env), sin esto la app truena en silencio al arrancar, antes de
# que aparezca cualquier ventana. Los mandamos a un archivo de log en vez
# de reescribir cada print() del proyecto uno por uno.
if sys.stdout is None or sys.stderr is None:
    _carpeta_datos = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
    os.makedirs(_carpeta_datos, exist_ok=True)
    _log_salida = open(os.path.join(_carpeta_datos, "salida.log"), "a", encoding="utf-8", buffering=1)
    sys.stdout = _log_salida
    sys.stderr = _log_salida

import uvicorn
import webview

import chats
import config
import estado
import main
import monitoreo
from servidor import app as servidor_app

# Tamaño de la ventana en cada modo (ancho, alto)
TAMANOS = {"voz": (380, 560), "escritorio": (1100, 720)}

_CARPETA = os.path.dirname(os.path.abspath(__file__))
_RUTA_LOG = os.path.join(_CARPETA, "datos", "azmuth.log")


def _log_arranque(texto: str):
    try:
        os.makedirs(os.path.dirname(_RUTA_LOG), exist_ok=True)
        with open(_RUTA_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {texto}\n")
    except Exception:
        pass


def iniciar_servidor():
    try:
        uvicorn.run(servidor_app, host="127.0.0.1", port=config.PUERTO_SERVIDOR, log_level="critical")
    except Exception as e:
        _log_arranque(f"Error arrancando el servidor: {e}")
        monitoreo.registrar_error("arranque del servidor", e)


def iniciar_escucha_voz():
    """Da un pequeño respiro al sistema y arranca el bucle de voz en segundo plano"""
    time.sleep(2)
    try:
        main.iniciar()
    except Exception as e:
        _log_arranque(f"Error en el motor de voz: {e}")
        monitoreo.registrar_error("motor de voz", e)
        estado.log(f"Error en voz: {e}")


def _al_cerrar_ventana():
    os._exit(0)


if __name__ == '__main__':
    _mutex_instancia = estado.asegurar_instancia_unica()
    monitoreo.instalar()

    # 1. Servidor FastAPI en segundo plano
    threading.Thread(target=iniciar_servidor, daemon=True).start()
    
    # 1b. Índice de aplicaciones instaladas (para "abre cualquier app"), sin frenar el arranque
    from skills import apps_instaladas
    threading.Thread(target=apps_instaladas.precargar, daemon=True).start()

    # 2. Motor de voz en hilo secundario independiente
    threading.Thread(target=iniciar_escucha_voz, daemon=True).start()

    # 3. Modo con el que se cerró la última vez (voz o escritorio)
    estado.set_modo(chats.obtener_ajuste("modo", "voz"))
    ancho, alto = TAMANOS[estado.obtener_modo()]

    # 4. Creación y ejecución de la ventana gráfica (DEBE estar en el hilo principal)
    ventana = webview.create_window(
        'Azmuth OS - JARVIS',
        f'http://127.0.0.1:{config.PUERTO_SERVIDOR}',
        width=ancho,
        height=alto,
        min_size=(380, 520),
        background_color='#050b05',
        resizable=True,
    )
    ventana.events.closed += _al_cerrar_ventana

    def _al_cambiar_modo(modo):
        """Por voz, por el botón o escrito: la ventana se agranda para el chat
        o regresa a la ventana compacta del núcleo, y se recuerda el modo."""
        chats.guardar_ajuste("modo", modo)
        try:
            ventana.resize(*TAMANOS[modo])
        except Exception as e:
            _log_arranque(f"No pude redimensionar la ventana: {e}")

    estado.al_cambiar_modo(_al_cambiar_modo)

    webview.start()
