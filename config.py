"""
Configuración central de JARVIS.
Lee las claves y ajustes desde el archivo .env (que tú creas a partir
de .env.example) y los deja disponibles para el resto del programa.
"""
import os
from dotenv import load_dotenv

import rutas

# El .env vive junto al programa (o junto a Azmuth.exe en la versión empaquetada)
load_dotenv(os.path.join(rutas.CARPETA_APP, ".env"))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "").strip()
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb").strip()
PALABRA_CLAVE = os.getenv("PALABRA_CLAVE", "hora de ser heroe").strip().lower()
# Palabra clave cuando Azmuth está en inglés (el reconocedor en-US no entiende la de español)
PALABRA_CLAVE_EN = os.getenv("PALABRA_CLAVE_EN", "it's hero time").strip().lower()
IDIOMA_VOZ = "es-MX"
MODELO_CLAUDE = "claude-sonnet-4-6"

# --- Servidor único (interfaz + comandos remotos) y túnel de Ngrok ---
# Un solo puerto para todo: la ventana de escritorio (PyWebView) y el
# túnel de Ngrok apuntan aquí. Así nunca hay dos servidores compitiendo.
PUERTO_SERVIDOR = int(os.getenv("PUERTO_SERVIDOR", "8080").strip() or "8080")
NGROK_AUTHTOKEN = os.getenv("NGROK_AUTHTOKEN", "").strip()
# Dominio fijo reservado en tu cuenta de Ngrok (ej. algo.ngrok-free.dev).
# Déjalo vacío si quieres que Ngrok te asigne uno aleatorio cada vez.
NGROK_DOMINIO = os.getenv("NGROK_DOMINIO", "").strip()
# Seguridad del control remoto: si defines TOKEN_REMOTO en .env, todo lo que
# llegue por Ngrok (celular / reloj) debe traer ese token. Abre una vez
# https://<tu-dominio>/reloj?token=TU_TOKEN y el celular lo recuerda.
TOKEN_REMOTO = os.getenv("TOKEN_REMOTO", "").strip()

if not ANTHROPIC_API_KEY:
    print("⚠️  Falta ANTHROPIC_API_KEY en tu archivo .env — la conversación con la IA no va a funcionar todavía.")
if not ELEVENLABS_API_KEY:
    print("⚠️  Falta ELEVENLABS_API_KEY en tu archivo .env — usaré la voz de reserva de Windows mientras tanto.")
