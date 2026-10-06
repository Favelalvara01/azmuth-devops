@echo off
REM Ejecuta en tu compu el mismo pipeline que corre GitHub Actions.
REM Uso: doble clic o "pipeline_local.bat" desde la terminal en esta carpeta.
cd /d "%~dp0"
if not exist reports mkdir reports
echo === 1/6 Instalando dependencias de desarrollo ===
py -3.13 -m pip install -q -r requirements-dev.txt
echo === 2/6 Validacion estatica (ruff) ===
py -3.13 -m ruff check . --select E9,F63,F7,F82 || goto error
py -3.13 -m ruff check . --exit-zero --output-format=concise > reports\ruff.txt
echo === 3/6 Pruebas automatizadas + cobertura ===
py -3.13 -m pytest --cov --cov-report=term --cov-report=json:reports/coverage.json --cov-report=html:reports/htmlcov --junitxml=reports/pruebas.xml || goto error
echo === 4/6 Complejidad ciclomatica (radon) ===
py -3.13 -m radon cc . -s -a -e "tests/*,metricas/*" > reports\complejidad.txt
py -3.13 -m radon mi . -s -e "tests/*,metricas/*" > reports\mantenibilidad.txt
echo === 5/6 Metricas y estimacion ===
py -3.13 metricas\calcular_metricas.py --reportes reports --historial metricas\resultados\historial.csv
py -3.13 metricas\estimacion.py --reportes reports
echo === 6/6 Analisis con IA (Claude) ===
py -3.13 metricas\analisis_ia.py --reportes reports
if not exist metricas\resultados mkdir metricas\resultados
for %%f in (metricas.md metricas.json estimacion.md estimacion.json analisis_ia.md complejidad.txt mantenibilidad.txt ruff.txt) do copy /y reports\%%f metricas\resultados\ >nul
echo.
echo Listo. Resultados guardados en metricas\resultados\
pause
exit /b 0
:error
echo El pipeline fallo. Revisa el mensaje de arriba.
pause
exit /b 1
