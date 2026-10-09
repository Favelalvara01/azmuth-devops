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


def _clave(nombre: str) -> str:
    """Lee una clave del .env. Los textos de ejemplo de .env.example ("tu_clave_de_..._aqui",
    "tu-dominio-fijo...") cuentan como vacíos: así una clave sin llenar no se usa por error
    (antes daba "invalid x-api-key" en vez de pasar a la IA gratuita)."""
    valor = os.getenv(nombre, "").strip()
    bajo = valor.lower()
    if bajo.startswith(("tu_", "tu-", "your_", "your-")) or bajo.endswith(("_aqui", "_aquí")):
        return ""
    return valor


ANTHROPIC_API_KEY = _clave("ANTHROPIC_API_KEY")
# Alternativa gratuita: si no hay clave de Anthropic, Azmuth usa Google Gemini.
GEMINI_API_KEY = _clave("GEMINI_API_KEY")
# Por defecto el Flash Lite: es el más rápido para un asistente de voz y el menos saturado.
GEMINI_MODELO = os.getenv("GEMINI_MODELO", "gemini-flash-lite-latest").strip() or "gemini-flash-lite-latest"
# Otra alternativa gratuita y muy rápida para conversar (no ve imágenes).
GROQ_API_KEY = _clave("GROQ_API_KEY")
GROQ_MODELO = os.getenv("GROQ_MODELO", "openai/gpt-oss-120b").strip() or "openai/gpt-oss-120b"
# DeepSeek (de pago, muy económica): va antes que las gratuitas si hay clave.
DEEPSEEK_API_KEY = _clave("DEEPSEEK_API_KEY")
DEEPSEEK_MODELO = os.getenv("DEEPSEEK_MODELO", "deepseek-flash").strip() or "deepseek-flash"
ELEVENLABS_API_KEY = _clave("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb").strip()
PALABRA_CLAVE = os.getenv("PALABRA_CLAVE", "hora de ser heroe").strip().lower()
# Palabra clave extra para cuando Azmuth está en inglés. Si no la defines se usa la
# misma de siempre (ej. "omnitrix", que se entiende igual en los dos idiomas).
PALABRA_CLAVE_EN = (os.getenv("PALABRA_CLAVE_EN", "").strip() or PALABRA_CLAVE).lower()
# Cómo te llama Azmuth ("Bienvenido, Favela"). Vacío = te dice "señor".
NOMBRE_USUARIO = os.getenv("NOMBRE_USUARIO", "").strip()
IDIOMA_VOZ = "es-MX"
MODELO_CLAUDE = "claude-sonnet-4-6"

# --- Servidor único (interfaz + comandos remotos) y túnel de Ngrok ---
# Un solo puerto para todo: la ventana de escritorio (PyWebView) y el
# túnel de Ngrok apuntan aquí. Así nunca hay dos servidores compitiendo.
PUERTO_SERVIDOR = int(os.getenv("PUERTO_SERVIDOR", "8080").strip() or "8080")
NGROK_AUTHTOKEN = _clave("NGROK_AUTHTOKEN")
# Dominio fijo reservado en tu cuenta de Ngrok (ej. algo.ngrok-free.dev).
# Déjalo vacío si quieres que Ngrok te asigne uno aleatorio cada vez.
NGROK_DOMINIO = _clave("NGROK_DOMINIO")
# Seguridad del control remoto: si defines TOKEN_REMOTO en .env, todo lo que
# llegue por Ngrok (celular / reloj) debe traer ese token. Abre una vez
# https://<tu-dominio>/reloj?token=TU_TOKEN y el celular lo recuerda.
TOKEN_REMOTO = os.getenv("TOKEN_REMOTO", "").strip()

if not ANTHROPIC_API_KEY and (DEEPSEEK_API_KEY or GROQ_API_KEY or GEMINI_API_KEY):
    print("ℹ️  Sin ANTHROPIC_API_KEY: se usará "
          + " + ".join(n for n, k in (("DeepSeek", DEEPSEEK_API_KEY), ("Groq", GROQ_API_KEY), ("Gemini", GEMINI_API_KEY)) if k) + ".")
elif not ANTHROPIC_API_KEY:
    print("⚠️  Falta una clave de IA (ANTHROPIC, DEEPSEEK, GROQ o GEMINI) en tu .env — la IA no va a funcionar todavía.")
if not ELEVENLABS_API_KEY:
    print("⚠️  Falta ELEVENLABS_API_KEY en tu archivo .env — usaré la voz de reserva de Windows mientras tanto.")
