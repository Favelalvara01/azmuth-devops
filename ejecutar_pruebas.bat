@echo off
REM ==================================================================
REM  Ejecuta cada TIPO de prueba de software por separado (reporte de
REM  Pruebas de Software). Entre cada tipo hace una pausa para que
REM  puedas tomar la captura de pantalla de la terminal.
REM  Uso: doble clic, o "ejecutar_pruebas.bat" desde esta carpeta.
REM       "ejecutar_pruebas.bat humo" corre solo un tipo.
REM ==================================================================
chcp 65001 > nul
cd /d "%~dp0"
if not exist reports mkdir reports
set PY=py -3.13 -m

if not "%1"=="" (
    %PY% pytest -m %1 -v -s -p no:cacheprovider
    goto fin
)

echo === Instalando dependencias de desarrollo (una sola vez) ===
%PY% pip install -q -r requirements-dev.txt

for %%T in (humo unitaria componente integracion sistema aceptacion exploratoria usabilidad funcional no_funcional interfaz seguridad) do (
    cls
    echo.
    echo ##################################################################
    echo    PRUEBAS: %%T
    echo ##################################################################
    %PY% pytest -m %%T -v -s -p no:cacheprovider --junitxml=reports\pruebas_%%T.xml
    echo.
    echo  ^>^>^> Toma la captura de "%%T" y presiona una tecla para continuar...
    pause > nul
)

cls
echo ##################################################################
echo    SEGURIDAD: analisis estatico del codigo (bandit)
echo ##################################################################
%PY% bandit -r . -x ./tests,./metricas -ll
echo  ^>^>^> Toma la captura de bandit y presiona una tecla...
pause > nul

cls
echo ##################################################################
echo    SEGURIDAD: vulnerabilidades en dependencias (pip-audit)
echo ##################################################################
%PY% pip_audit -r requirements-dev.txt
echo  ^>^>^> Toma la captura de pip-audit y presiona una tecla...
pause > nul

cls
echo ##################################################################
echo    RESUMEN: toda la bateria + cobertura
echo ##################################################################
%PY% pytest --cov --cov-report=term -q -p no:cacheprovider

:fin
echo.
pause
