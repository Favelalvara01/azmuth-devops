# Hiperconvergencia: API de Azmuth en VirtualBox + Ubuntu Server

```
 Windows (anfitrión)                          VirtualBox (hipervisor tipo 2)
 ┌──────────────────────────┐   NAT 8081→8080  ┌──────────────────────────────────────────┐
 │ verificar_hipervisor.ps1 │ ───────────────▶ │ VM Ubuntu Server = nodo hiperconvergente │
 │ pytest tests/api_remota  │   VBoxManage     │  ┌────────── Docker (red-hci) ─────────┐ │
 └──────────────────────────┘ ◀─ métricas ──── │  │ azmuth-api  (cómputo: 1 CPU/512 MB) │ │
                                               │  │ volumen azmuth-datos (SQLite)       │ │
                                               │  │ probador    (pruebas internas)      │ │
                                               │  │ portainer   (gestión, opcional)     │ │
                                               │  └─────────────────────────────────────┘ │
                                               └──────────────────────────────────────────┘
```

1. **En la VM** (Ubuntu Server, adaptador 1 en NAT):
   ```bash
   git clone https://github.com/Favelalvara01/azmuth-devops.git
   cd azmuth-devops/hiperconvergencia
   bash preparar_nodo.sh          # instala Docker, levanta el nodo y corre las pruebas internas
   ```
2. **En Windows** (carpeta `jarvis-agent`, PowerShell):
   ```powershell
   powershell -ExecutionPolicy Bypass -File hiperconvergencia\verificar_hipervisor.ps1 -VM "UbuntuServer" -Token "<token del .env de la VM>"
   ```
3. Opcional: `bash preparar_nodo.sh zap` (OWASP ZAP) y `docker compose --profile gestion up -d` (Portainer en `https://<ip-vm>:9443`).
