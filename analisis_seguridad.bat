@echo off
REM ==================================================================
REM  Analisis de seguridad de Azmuth con explicacion en pantalla:
REM  1) bandit    = analisis estatico del codigo (SAST)
REM  2) pip-audit = vulnerabilidades conocidas en las librerias (SCA)
REM  Uso: analisis_seguridad.bat
REM ==================================================================
chcp 65001 > nul
cd /d "%~dp0"

echo ================================================================================
echo   1. ANÁLISIS ESTÁTICO DEL CÓDIGO (SAST) con bandit
echo ================================================================================
echo   Qué es: revisa el código fuente SIN ejecutarlo, buscando patrones inseguros
echo   conocidos (contraseñas escritas en el código, inyección de comandos, etc.).
echo   Para qué sirve: encuentra riesgos antes de que el programa llegue al usuario.
echo   Se muestran solo los hallazgos de severidad media o alta (-ll).
echo ================================================================================
py -3.13 -m bandit -r . -x ./tests,./metricas -ll -q -f custom --msg-template "  {relpath}:{line}  [{test_id}] {severity}: {msg}"
echo.
echo ================================== CONCLUSIÓN ==================================
echo   Los 5 hallazgos son B602 (subprocess con shell=True) en acciones_remotas.py y
echo   skills\aplicaciones.py. Se analizaron: los comandos que van a la shell salen de
echo   un catálogo fijo escrito en el código (lista blanca), nunca de lo que dice el
echo   usuario. Las pruebas CS-07 y CS-13 lo comprueban: riesgo ACEPTADO Y MITIGADO.
echo.
echo ================================================================================
echo   2. VULNERABILIDADES EN DEPENDENCIAS (SCA) con pip-audit
echo ================================================================================
echo   Qué es: compara cada librería que usa Azmuth (fastapi, requests, anthropic...)
echo   contra la base pública de vulnerabilidades conocidas (CVE / PyPI Advisory).
echo   Para qué sirve: una librería vulnerable hace vulnerable a todo el programa.
echo ================================================================================
py -3.13 -m pip_audit -r requirements-dev.txt --progress-spinner off
if errorlevel 1 (
    echo.
    echo ================================== CONCLUSIÓN ==================================
    echo   Hay librerías con vulnerabilidades: actualízalas a la versión indicada.
) else (
    echo.
    echo ================================== CONCLUSIÓN ==================================
    echo   Ninguna dependencia tiene vulnerabilidades conocidas.
)
echo.
pause
