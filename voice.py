"""
Módulo de voz de AZMUTH.
Intenta hablar con una voz de ElevenLabs (natural). Si algo falla
(sin internet, sin API key, se acabaron los créditos), cae automáticamente
a la voz nativa de Windows para que AZMUTH nunca se quede mudo.

IMPORTANTE: Hay dos partes del programa que pueden querer hablar al mismo
tiempo (el bucle principal, y el hilo que vigila recordatorios). La voz
de Windows (pyttsx3) NO es segura para usarse desde dos hilos a la vez —
si eso pasa, se puede quedar trabada para siempre y congelar todo el
programa. Por eso todo pasa por un candado (_lock): solo una parte puede
estar hablando en un momento dado, la otra espera su turno.
"""
import threading
import re
import config
import estado

_lock = threading.Lock()

_MAX_CARACTERES_VOZ = 320


def texto_para_voz(texto: str) -> str:
    """Prepara una respuesta del chat (que puede venir en Markdown y ser
    larga) para decirla en voz alta: quita símbolos de formato, no lee
    bloques de código y, si es muy larga, dice solo el principio."""
    t = texto or ""
    t = re.sub(r"```.*?```", " (le dejé el código en pantalla) ", t, flags=re.DOTALL)
    t = re.sub(r"`([^`]*)`", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)          # [texto](url) -> texto
    t = re.sub(r"^\s*(#{1,6}|>|[-*+]|\d+\.)\s+", "", t, flags=re.MULTILINE)
    t = re.sub(r"^\s*\|.*\|\s*$", "", t, flags=re.MULTILINE)   # tablas
    t = t.replace("**", "").replace("__", "").replace("*", "")
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) <= _MAX_CARACTERES_VOZ:
        return t
    corte = t[:_MAX_CARACTERES_VOZ]
    fin = max(corte.rfind(". "), corte.rfind("? "), corte.rfind("! "))
    corte = corte[:fin + 1] if fin > 80 else corte.rsplit(" ", 1)[0] + "…"
    return corte + " El resto se lo dejé en pantalla."


def _hablar_con_windows(texto: str):
    """Voz de reserva usando pyttsx3 (siempre disponible, sin internet)."""
    try:
        import pyttsx3
        motor = pyttsx3.init()
        motor.say(texto)
        motor.runAndWait()
        motor.stop()
    except Exception as e:
        print(f"[voz] Tampoco pude usar la voz de reserva de Windows: {e}")


def hablar(texto: str):
    """Punto de entrada único: siempre lo manda a la consola visual (y a la
    terminal si está visible) y, si puede, lo dice en voz alta."""
    estado.log(f"AZMUTH: {texto}")

    with _lock:
        if not config.ELEVENLABS_API_KEY:
            _hablar_con_windows(texto)
            return

        try:
            from elevenlabs.client import ElevenLabs
            from elevenlabs.play import play

            cliente = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
            audio = cliente.text_to_speech.convert(
                text=texto,
                voice_id=config.ELEVENLABS_VOICE_ID,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            play(audio)
        except Exception as e:
            print(f"[voz] ElevenLabs falló ({e}), uso la voz de reserva.")
            _hablar_con_windows(texto)
