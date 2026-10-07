"""
estado.py — Estado global del "núcleo" visual de AZMUTH.

Guarda en qué está el asistente en cada momento (reposo, escuchando,
procesando, ejecutando) para que la interfaz gráfica (azmuth.html) pueda
animar el núcleo de forma distinta según corresponda, en vez de la
terminal negra tradicional.

Este módulo vive en la memoria compartida de un solo proceso de Python
(app_desktop.py): tanto el hilo de voz (main.py) como el hilo del
servidor web (servidor.py, incluyendo comandos remotos por Ngrok)
escriben y leen del mismo estado, sin necesidad de red ni archivos.

Estados válidos:
  - "reposo"      → esperando la palabra clave, animación ambiental.
  - "escuchando"  → capturando la orden por el micrófono.
  - "procesando"  → interpretando el comando (skill local o Claude).
  - "ejecutando"  → realizando la acción y/o hablando la respuesta.
"""
import threading
import time

_lock = threading.Lock()

_ESTADOS_VALIDOS = {"reposo", "escuchando", "procesando", "ejecutando"}

_estado_actual = "reposo"
_detalle_actual = ""
_ultima_actualizacion = time.time()

# Si un estado "activo" (no-reposo) se queda pegado más de este tiempo sin
# que nadie lo actualice —por ejemplo porque algo truena a medio camino—
# el vigilante de abajo lo regresa solo a "reposo". Así el núcleo nunca se
# queda animando algo que en realidad ya terminó.
_TIMEOUT_AUTO_RESET = 8  # segundos

# --- Modo de Azmuth: "voz" (ventana pequeña con el núcleo) o "escritorio"
# (ventana grande con chat escrito). En ambos modos el micrófono sigue
# escuchando; el modo solo cambia la interfaz y dónde se guardan las
# respuestas. _version_chat sube cada vez que entra un mensaje nuevo al
# chat activo, para que la interfaz sepa cuándo recargar los mensajes.
_MODOS_VALIDOS = {"voz", "escritorio"}
_modo_actual = "voz"
_version_chat = 0
_escuchas_modo = []  # funciones a llamar cuando cambia el modo (ej. redimensionar la ventana)

_historial = []  # últimas líneas para la consola visual (reemplaza la terminal)
_MAX_HISTORIAL = 200
_total_historial = 0  # contador que SOLO crece, nunca se resetea ni se recorta


def set_estado(nombre: str, detalle: str = ""):
    """Cambia el estado actual del núcleo. Cualquier hilo puede llamarlo."""
    global _estado_actual, _detalle_actual, _ultima_actualizacion
    if nombre not in _ESTADOS_VALIDOS:
        nombre = "reposo"
    with _lock:
        _estado_actual = nombre
        _detalle_actual = (detalle or "")[:120]
        _ultima_actualizacion = time.time()


def obtener_estado():
    """Regresa el estado actual + el historial reciente, listo para /estado."""
    with _lock:
        return {
            "estado": _estado_actual,
            "detalle": _detalle_actual,
            "log": list(_historial),
            "log_total": _total_historial,
            "modo": _modo_actual,
            "version_chat": _version_chat,
        }


def obtener_modo() -> str:
    return _modo_actual


def set_modo(nombre: str) -> str:
    """Cambia entre "voz" y "escritorio" y avisa a quien esté escuchando
    (app_desktop.py redimensiona la ventana). Regresa el modo final."""
    global _modo_actual
    if nombre not in _MODOS_VALIDOS:
        return _modo_actual
    with _lock:
        cambio = nombre != _modo_actual
        _modo_actual = nombre
    if cambio:
        for funcion in list(_escuchas_modo):
            try:
                funcion(nombre)
            except Exception:
                pass
    return _modo_actual


def al_cambiar_modo(funcion):
    """Registra una función que recibe el nuevo modo cada vez que cambia."""
    _escuchas_modo.append(funcion)


def aviso_chat_nuevo():
    """Llamado cada vez que se guarda un mensaje en el chat activo."""
    global _version_chat
    with _lock:
        _version_chat += 1


def log(texto: str):
    """Agrega una línea a la consola visual de la interfaz (sustituye a la
    terminal negra). También la imprime, por si se corre en modo
    desarrollador con la consola visible (lanzar.bat).

    _historial se recorta a _MAX_HISTORIAL para no crecer sin límite, pero
    _total_historial NUNCA se recorta: es un contador que solo sube. La
    interfaz (azmuth.html) lo usa para saber cuántas líneas nuevas hay,
    en vez de comparar contra el tamaño de la lista recortada (eso era
    el bug: una vez que _historial llegaba a su tope, su tamaño se
    quedaba fijo y la interfaz creía que ya no había nada nuevo que
    mostrar, aunque AZMUTH siguiera hablando)."""
    global _total_historial
    with _lock:
        _historial.append(texto)
        _total_historial += 1
        if len(_historial) > _MAX_HISTORIAL:
            del _historial[0]
    try:
        print(texto)
    except Exception:
        pass


def _vigilante():
    global _estado_actual, _detalle_actual
    while True:
        time.sleep(1)
        with _lock:
            if _estado_actual != "reposo" and (time.time() - _ultima_actualizacion) > _TIMEOUT_AUTO_RESET:
                _estado_actual = "reposo"
                _detalle_actual = ""


threading.Thread(target=_vigilante, daemon=True).start()


def asegurar_instancia_unica():
    """Evita que dos copias de Azmuth corran a la vez (dos micrófonos
    escuchando el mismo comando = comandos y voz duplicados, como pasaba
    con la tarea programada + el inicio automático corriendo por separado).

    Comparten este mismo mutex tanto app_desktop.py como el arranque
    standalone de main.py: no importa por cuál de los dos se abra Azmuth,
    si ya hay una instancia corriendo, la nueva se cierra sola.

    Windows libera el mutex solo cuando el proceso dueño termina (incluso
    si truena), así que no puede quedar un candado atorado por un cierre
    feo. Esto es específico de Windows (ctypes.windll) a propósito, porque
    todo este proyecto ya depende de Windows (PowerShell, WScript.Shell).
    """
    import ctypes
    import sys
    ERROR_ALREADY_EXISTS = 183
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, "Global\\AzmuthOS_JARVIS_InstanciaUnica")
    if ctypes.GetLastError() == ERROR_ALREADY_EXISTS:
        log("Ya había una instancia de Azmuth corriendo — cierro esta copia extra.")
        sys.exit(0)
    return mutex  # hay que guardar la referencia viva mientras corre el proceso
