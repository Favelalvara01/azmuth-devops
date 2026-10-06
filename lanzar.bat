@echo off visible,
REM para ver los logs de depuracion (DEBUG - Escuche, errores, etc).
REM Para el uso normal del dia a dia usa iniciar_azmuth.bat en su lugar.
cd /d "%~dp0jarvis-agent"
python main.py
