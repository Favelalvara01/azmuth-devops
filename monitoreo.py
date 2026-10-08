"""Monitoreo en ejecución: registro central de errores de Azmuth.

Antes muchos hilos hacían `except Exception: pass` y un fallo en producción
solo se notaba cuando el usuario se quejaba (MTTD alto). Ahora todo error
queda en datos/errores.log (rotativo, máx. 3 × 512 KB) con fecha, origen y
traza, y el endpoint /salud del servidor muestra los últimos.
"""
import logging
import os
import sys
import threading
import time
from collections import deque
from logging.handlers import RotatingFileHandler

_RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "errores.log")
_INICIO = time.time()
_ultimos = deque(maxlen=20)
_total = 0
_candado = threading.Lock()
_logger = None


def _obtener_logger():
    global _logger
    if _logger is None:
        os.makedirs(os.path.dirname(_RUTA_LOG), exist_ok=True)
        _logger = logging.getLogger("azmuth.monitoreo")
        _logger.setLevel(logging.INFO)
        _logger.propagate = False
        for viejo in list(_logger.handlers):
            _logger.removeHandler(viejo)
            viejo.close()
        manejador = RotatingFileHandler(_RUTA_LOG, maxBytes=512_000, backupCount=3, encoding="utf-8")
        manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        _logger.addHandler(manejador)
    return _logger


def registrar_error(origen: str, error: BaseException):
    """Guarda el error con su traza. Nunca lanza excepciones."""
    global _total
    fecha = time.strftime("%Y-%m-%d %H:%M:%S")
    with _candado:
        _total += 1
        _ultimos.append({"fecha": fecha, "origen": origen,
                         "tipo": type(error).__name__, "mensaje": str(error)[:300]})
    try:
        _obtener_logger().error("%s: %s", origen, error,
                                exc_info=(type(error), error, error.__traceback__))
    except Exception:  # el monitoreo jamás debe tumbar la app
        pass


def registrar_evento(texto: str):
    try:
        _obtener_logger().info(texto)
    except Exception:
        pass


def resumen() -> dict:
    with _candado:
        return {
            "activo_segundos": int(time.time() - _INICIO),
            "errores_total": _total,
            "ultimos_errores": list(_ultimos),
        }


def instalar():
    """Captura también las excepciones que nadie atrapó (hilo principal e hilos)."""
    previo = sys.excepthook

    def _hook(tipo, valor, traza):
        registrar_error("excepcion no atrapada", valor)
        previo(tipo, valor, traza)

    def _hook_hilo(args):
        registrar_error(f"hilo {args.thread.name if args.thread else '?'}", args.exc_value)

    sys.excepthook = _hook
    threading.excepthook = _hook_hilo
    registrar_evento("Azmuth iniciado")
