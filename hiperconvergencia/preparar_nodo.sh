#!/usr/bin/env bash
# =====================================================================
#  preparar_nodo.sh — se ejecuta DENTRO de la VM Ubuntu Server (VirtualBox)
#  Convierte la VM en un nodo hiperconvergente para la API de Azmuth.
#
#  Uso:
#     git clone https://github.com/Favelalvara01/azmuth-devops.git
#     cd azmuth-devops/hiperconvergencia
#     bash preparar_nodo.sh            # instala, levanta y prueba
#     bash preparar_nodo.sh pruebas    # solo vuelve a correr las pruebas
#     bash preparar_nodo.sh zap        # escaneo de seguridad OWASP ZAP (opcional)
# =====================================================================
set -euo pipefail
cd "$(dirname "$0")"
paso() { echo; echo "==================== $* ===================="; }

instalar() {
  paso "1. Instalando Docker, Compose y utilidades del invitado de VirtualBox"
  sudo apt-get update -y
  sudo apt-get install -y docker.io docker-compose-v2 git curl openssl virtualbox-guest-utils || \
  sudo apt-get install -y docker.io docker-compose-v2 git curl openssl
  sudo systemctl enable --now docker
  sudo usermod -aG docker "$USER" || true
}

token() {
  paso "2. Generando el token de la API (hiperconvergencia/.env)"
  if [ ! -f .env ]; then
    echo "TOKEN_REMOTO=azmuth-$(openssl rand -hex 12)" > .env
  fi
  cat .env
}

levantar() {
  paso "3. Levantando el nodo: cómputo + almacenamiento + red definidos por software"
  sudo docker compose up -d --build
  echo "Esperando a que el healthcheck marque 'healthy'..."
  for _ in $(seq 1 40); do
    estado=$(sudo docker inspect -f '{{.State.Health.Status}}' azmuth-api 2>/dev/null || echo "?")
    [ "$estado" = "healthy" ] && break
    sleep 3
  done
  sudo docker compose ps
}

recursos() {
  paso "4. Recursos virtualizados del nodo"
  echo "--- CÓMPUTO (límites del contenedor) ---"
  sudo docker inspect -f 'CPU: {{.HostConfig.NanoCpus}} nanoCPU | RAM: {{.HostConfig.Memory}} bytes' azmuth-api
  sudo docker stats --no-stream azmuth-api
  echo "--- ALMACENAMIENTO (volumen) ---"
  sudo docker volume inspect azmuth-hci_azmuth-datos --format 'Volumen: {{.Name}}  ->  {{.Mountpoint}}'
  echo "--- RED (red definida por software) ---"
  sudo docker network inspect azmuth-hci_red-hci --format 'Red: {{.Name}}  Subred: {{range .IPAM.Config}}{{.Subnet}}{{end}}'
  sudo docker inspect -f 'IP del contenedor: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' azmuth-api
  echo "--- IP de la VM ---"
  hostname -I
}

pruebas() {
  # shellcheck disable=SC1091
  source .env
  paso "5. Prueba local con curl (dentro de la VM)"
  echo -n "Sin token  -> "; curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/estado
  echo -n "Con token  -> "; curl -s -H "X-Azmuth-Token: $TOKEN_REMOTO" http://localhost:8080/salud; echo

  paso "6. Pruebas de API servicio-a-servicio (contenedor probador en la red red-hci)"
  sudo docker compose --profile pruebas run --rm probador

  paso "7. Persistencia del almacenamiento: crear chat, reiniciar el contenedor y verificar"
  id=$(curl -s -X POST -H "X-Azmuth-Token: $TOKEN_REMOTO" http://localhost:8080/chats | sed 's/[^0-9]//g')
  curl -s -X POST -H "X-Azmuth-Token: $TOKEN_REMOTO" -H "Content-Type: application/json" \
       -d '{"texto":"toma nota: dato que sobrevive al reinicio"}' "http://localhost:8080/chats/$id/mensajes" > /dev/null
  sudo docker compose restart azmuth-api
  sleep 6
  echo "Mensajes del chat $id después de reiniciar:"
  curl -s -H "X-Azmuth-Token: $TOKEN_REMOTO" "http://localhost:8080/chats/$id/mensajes"; echo
}

zap() {
  # shellcheck disable=SC1091
  source .env
  paso "Escaneo dinámico de seguridad (OWASP ZAP baseline) contra la API del nodo"
  sudo docker run --rm --network azmuth-hci_red-hci -v "$(pwd)":/zap/wrk:rw ghcr.io/zaproxy/zaproxy:stable \
    zap-baseline.py -t http://azmuth-api:8080/salud -r reporte_zap.html -I \
    -z "-config replacer.full_list(0).description=token -config replacer.full_list(0).enabled=true \
        -config replacer.full_list(0).matchtype=REQ_HEADER -config replacer.full_list(0).matchstr=X-Azmuth-Token \
        -config replacer.full_list(0).regex=false -config replacer.full_list(0).replacement=$TOKEN_REMOTO"
  echo "Reporte: hiperconvergencia/reporte_zap.html"
}

case "${1:-todo}" in
  pruebas) pruebas ;;
  zap) zap ;;
  recursos) recursos ;;
  *) instalar; token; levantar; recursos; pruebas
     paso "LISTO. Ahora en Windows ejecuta: hiperconvergencia\\verificar_hipervisor.ps1" ;;
esac
