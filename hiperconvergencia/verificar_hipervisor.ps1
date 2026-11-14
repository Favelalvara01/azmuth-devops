# =====================================================================
#  verificar_hipervisor.ps1 — se ejecuta en WINDOWS (anfitrión)
#  Verifica la comunicación HIPERVISOR (VirtualBox) <-> NODO HIPERCONVERGENTE
#  (VM Ubuntu Server con la API de Azmuth en Docker) y corre las pruebas de API.
#
#  Uso (PowerShell, desde la carpeta jarvis-agent):
#     powershell -ExecutionPolicy Bypass -File hiperconvergencia\verificar_hipervisor.ps1 -VM "UbuntuServer" -Token "azmuth-xxxx"
#  El token es el que imprimió preparar_nodo.sh (archivo hiperconvergencia/.env de la VM).
# =====================================================================
param(
    [string]$VM = "UbuntuServer",
    [Parameter(Mandatory = $true)][string]$Token,
    [int]$PuertoApi = 8081,
    [int]$PuertoSsh = 2222
)
$ErrorActionPreference = "Continue"
function Paso($texto) { Write-Host ""; Write-Host "==================== $texto ====================" -ForegroundColor Green }

$vbox = "$env:ProgramFiles\Oracle\VirtualBox\VBoxManage.exe"
if (-not (Test-Path $vbox)) { Write-Host "No encontré VBoxManage.exe en $vbox" -ForegroundColor Red; exit 1 }

Paso "1. Hipervisor: versión de VirtualBox y máquinas registradas"
& $vbox --version
& $vbox list vms

Paso "2. Estado del nodo (VM '$VM')"
$corriendo = (& $vbox list runningvms) -match "`"$VM`""
if (-not $corriendo) {
    Write-Host "La VM está apagada: el hipervisor la enciende en modo headless..." -ForegroundColor Yellow
    & $vbox startvm $VM --type headless
    Start-Sleep -Seconds 45
}
& $vbox list runningvms

Paso "3. Recursos que el hipervisor asigna al nodo (cómputo, almacenamiento, red)"
$info = & $vbox showvminfo $VM --machinereadable
$info | Select-String -Pattern '^(name|ostype|cpus|memory|VMState|nic1|natnet1|Forwarding|"SATA)' | ForEach-Object { $_.Line }

Paso "4. Red virtual: reglas de reenvío de puertos NAT (Windows -> VM)"
& $vbox controlvm $VM natpf1 delete "azmuth-api" 2>$null
& $vbox controlvm $VM natpf1 delete "ssh" 2>$null
& $vbox controlvm $VM natpf1 "azmuth-api,tcp,127.0.0.1,$PuertoApi,,8080"
& $vbox controlvm $VM natpf1 "ssh,tcp,127.0.0.1,$PuertoSsh,,22"
(& $vbox showvminfo $VM --machinereadable) | Select-String "Forwarding" | ForEach-Object { $_.Line }

Paso "5. El hipervisor consulta al invitado (Guest Additions): IP y sistema de la VM"
& $vbox guestproperty get $VM "/VirtualBox/GuestInfo/Net/0/V4/IP"
& $vbox guestproperty get $VM "/VirtualBox/GuestInfo/OS/Product"

Paso "6. Conectividad TCP del anfitrión al puerto de la API"
Test-NetConnection -ComputerName 127.0.0.1 -Port $PuertoApi | Select-Object ComputerName, RemotePort, TcpTestSucceeded

Paso "7. Llamadas a la API a través del hipervisor"
$base = "http://127.0.0.1:$PuertoApi"
try {
    Invoke-RestMethod "$base/estado" -TimeoutSec 5 | Out-Null
    Write-Host "Sin token: respondió 200 (¡NO debería!)" -ForegroundColor Red
} catch { Write-Host "Sin token  -> $($_.Exception.Response.StatusCode.value__) (rechazado, correcto)" -ForegroundColor Cyan }
$salud = Invoke-RestMethod "$base/salud" -Headers @{ "X-Azmuth-Token" = $Token } -TimeoutSec 5
Write-Host "Con token  -> nodo=$($salud.nodo)  sistema=$($salud.sistema)  activo=$($salud.activo_segundos)s  protegido=$($salud.control_remoto_protegido)" -ForegroundColor Cyan

Paso "8. Métricas del nodo vistas desde el hipervisor"
& $vbox metrics setup --period 2 --samples 3 $VM "CPU/Load,RAM/Usage" | Out-Null
Start-Sleep -Seconds 7
& $vbox metrics query $VM "CPU/Load/User,CPU/Load/Kernel,RAM/Usage/Used"

Paso "9. Pruebas automatizadas de API contra el nodo (pytest)"
$env:AZMUTH_URL = $base
$env:AZMUTH_TOKEN = $Token
py -3.13 -m pytest tests/api_remota -v -s -p no:cacheprovider
