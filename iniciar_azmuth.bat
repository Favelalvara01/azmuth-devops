@echo off
cd /d "C:\Users\osiel\OneDrive\Escritorio\asistente\jarvis-agent"

:: Levantamos Ngrok
start /B ngrok http --domain=epiphany-bottling-dilation.ngrok-free.dev 8080 >nul 2>&1
timeout /t 2 /nobreak > nul

:: Usamos python con consola para ver el error exacto si se cierra
python app_desktop.py

pause