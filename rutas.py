"""Rutas de la app, funcionando igual con `python app_desktop.py` que con Azmuth.exe.

Con PyInstaller los recursos de solo lectura (azmuth.html, imagenes/) se
desempacan en una carpeta interna, pero los datos del usuario (.env, la base
de datos y los logs) deben vivir junto al .exe para no perderse.
"""
import os
import sys

CONGELADO = bool(getattr(sys, "frozen", False))
_AQUI = os.path.dirname(os.path.abspath(__file__))

CARPETA_RECURSOS = getattr(sys, "_MEIPASS", _AQUI)
CARPETA_APP = os.path.dirname(sys.executable) if CONGELADO else _AQUI
CARPETA_DATOS = os.path.join(CARPETA_APP, "datos")
