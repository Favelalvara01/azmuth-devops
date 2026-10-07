"""
A.Z.M.U.T.H. — motor de voz optimizado y sincronizado con el núcleo.
"""
import re
import threading
import time
import io
import wave
import os
import numpy as np
import sounddevice as sd

import speech_recognition as sr

import config
import voice
import cerebro
import skills
import estado
import nucleo

# Si al comando le antepone el nombre del asistente ("Azmuth, recuerda que...",
# "oye Azmuth, toma nota..."), se lo quitamos ANTES de mandarlo a las skills.
# Sin esto, un patrón anclado al inicio de la frase (como el de "recuerda
# que..." en skills/memoria.py) nunca haría match porque la frase no
# empezaría en "recuerda" sino en "azmuth,".
_VOCATIVO_RE = re.compile(r"^(?:oye\s+|hey\s+)?azmuth[,]?\s+", re.IGNORECASE)

PALABRA_CLAVE = config.PALABRA_CLAVE.lower().strip()


class SoundDeviceMicrophone:
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self, size):
        audio_chunk = sd.rec(int(size), samplerate=self.sample_rate, channels=1, dtype='int16', blocking=True)
        return audio_chunk.tobytes()

    @property
    def CHUNK(self):
        return self.chunk_size

    @property
    def SAMPLE_RATE(self):
        return self.sample_rate

    @property
    def SAMPLE_WIDTH(self):
        return 2


def _vigilar_recordatorios():
    while True:
        try:
            avisos = skills.recordatorios.revisar_pendientes()
            for texto in avisos:
                estado.set_estado("ejecutando", f"Recordatorio: {texto}")
                voice.hablar(f"Recordatorio: {texto}")
                estado.set_estado("reposo")
        except Exception:
            pass
        time.sleep(20)


# Umbral de voz "dinámico": se recalcula en iniciar() según el ruido de
# fondo real del cuarto/micrófono en vez de usar un número fijo. Este
# valor es solo el respaldo mientras arranca la calibración.
_UMBRAL_VOZ = 150


def calibrar_umbral(sample_rate=16000, chunk_size=1024, duracion_seg=1.0):
    """Escucha un instante de silencio ambiente y calcula un umbral de voz
    ajustado a las condiciones reales (ruido de fondo, ganancia del
    micrófono, etc.), en vez del número fijo que se usaba antes."""
    try:
        n_frames = max(1, int((sample_rate / chunk_size) * duracion_seg))
        niveles = []
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            for _ in range(n_frames):
                audio_chunk, _ = stream.read(chunk_size)
                niveles.append(float(np.max(np.abs(audio_chunk))))
        ruido_base = sum(niveles) / len(niveles) if niveles else 60.0
    except Exception as e:
        estado.log(f"[Calibración de mic falló, uso valor de reserva]: {e}")
        ruido_base = 60.0

    # Un poco por encima del piso de ruido real, con topes para no quedar
    # ni demasiado sordo ni demasiado sensible a cualquier soplido.
    umbral = int(max(80, min(1200, ruido_base * 2.5 + 40)))
    estado.log(f"🎚️ Ruido ambiente: {ruido_base:.0f} — umbral de voz fijado en {umbral}")
    return umbral


def escuchar(reconocedor, microfono, marcar_escuchando=False):
    sample_rate = 16000
    chunk_size = 1024

    umbral_silencio = _UMBRAL_VOZ
    # Antes esperaba ~1.9s de silencio (lento) y luego lo bajé a ~0.9s
    # (muy agresivo: cortaba la frase si hacías una pausa corta al hablar,
    # y el audio truncado salía como "no escuché ningún comando"). ~1.3s
    # es el punto medio: sigue siendo más rápido que el original pero deja
    # margen para pausas naturales al hablar.
    max_frames_silencio = 20
    max_frames_espera_voz = 200

    if marcar_escuchando:
        estado.set_estado("escuchando", "Capturando su orden...")

    audio_frames = []
    hablando = False
    silencio_frames = 0
    espera_voz_frames = 0

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
            while True:
                audio_chunk, _ = stream.read(chunk_size)
                volumen = np.max(np.abs(audio_chunk))

                if not hablando:
                    espera_voz_frames += 1
                    if volumen > umbral_silencio:
                        hablando = True
                        audio_frames.append(audio_chunk)
                        estado.log("🎤 Voz detectada...")
                    elif espera_voz_frames > max_frames_espera_voz:
                        break
                else:
                    audio_frames.append(audio_chunk)
                    if volumen < umbral_silencio:
                        silencio_frames += 1
                        if silencio_frames > max_frames_silencio:
                            break
                    else:
                        silencio_frames = 0

                if len(audio_frames) > (sample_rate / chunk_size) * 15:
                    break

        if not audio_frames:
            return None

        audio_data = np.concatenate(audio_frames, axis=0)

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio_data.tobytes())
        wav_buffer.seek(0)

        with sr.AudioFile(wav_buffer) as fuente:
            audio = reconocedor.record(fuente)

    except Exception as e:
        estado.log(f"[Audio Error]: {e}")
        return None

    try:
        texto = reconocedor.recognize_google(audio, language=config.IDIOMA_VOZ)
        estado.log(f"🎤 Escuché: {texto}")
        return texto
    except (sr.UnknownValueError, sr.RequestError):
        return None


def procesar_comando(texto: str):
    estado.log(f"USTED: {texto}")
    estado.set_estado("procesando", texto)

    texto = _VOCATIVO_RE.sub("", texto, count=1).strip()
    t_limpio = texto.lower().strip()

    palabras_apagado = ["apagate", "apagar", "apagar sistema", "apagar azmuth", "desactivar", "apaga el sistema"]
    if any(p in t_limpio for p in palabras_apagado):
        estado.set_estado("ejecutando", "Apagando sistema")
        voice.hablar("Apagando sistema. Hasta luego, señor.")
        time.sleep(1.5)
        # main.iniciar() corre en un hilo secundario cuando lo lanza app_desktop.py
        # (el hilo principal está ocupado con la ventana de webview). sys.exit(0)
        # solo mata ESE hilo y la ventana se queda abierta. os._exit(0) sí termina
        # el proceso completo -incluida la ventana- sin importar en qué hilo esté.
        os._exit(0)

    apps_directas = ["roblox", "fortnite", "rocket league", "spotify", "xbox", "edge", "word", "excel", "paint", "bloc de notas"]
    if t_limpio in apps_directas:
        texto = f"abre {t_limpio}"

    # En modo escritorio lo que se dice por voz también queda escrito en el
    # chat activo (y Claude usa el historial de ese chat como contexto).
    if estado.obtener_modo() == "escritorio":
        respuesta, _, _ = nucleo.responder_en_chat(texto, origen="voz")
        respuesta_hablada = voice.texto_para_voz(respuesta)
    else:
        respuesta, _ = nucleo.responder(texto)
        respuesta_hablada = respuesta
    estado.set_estado("ejecutando", respuesta)
    voice.hablar(respuesta_hablada)
    time.sleep(1.5)
    estado.set_estado("reposo")


def _vigilar_perfil():
    """Cada cierto tiempo revisa si toca regenerar el perfil de
    personalidad (ver skills/perfil.py y cerebro.actualizar_perfil_si_toca).
    Esto SÍ puede vivir en un hilo aparte porque no toca el micrófono —
    solo hace una llamada a Claude de vez en cuando."""
    while True:
        time.sleep(300)
        try:
            cerebro.actualizar_perfil_si_toca()
        except Exception:
            pass


_RE_RESPUESTA_SI = re.compile(r"\b(s[ií]|claro|va|dale|dele|s[ií]mon|por favor|ok[aá]y?)\b", re.IGNORECASE)
_RE_RESPUESTA_NO = re.compile(r"\bno\b|ahorita no|después no|luego no|para nada", re.IGNORECASE)


def _revisar_sugerencia_pendiente(reconocedor, microfono):
    """Si hay una sugerencia de hábito lista (ver skills/habitos.py), la
    dice y espera un sí/no corto — SIEMPRE desde el hilo principal, para
    no competir por el micrófono con el bucle normal de escucha. Si
    acepta y esa categoría tiene una acción concreta asociada, la
    ejecuta de una vez."""
    resultado = skills.habitos.sugerir_por_hora()
    if not resultado:
        return
    texto_sugerencia, categoria = resultado

    estado.set_estado("ejecutando", texto_sugerencia)
    voice.hablar(texto_sugerencia)
    estado.set_estado("escuchando", "Esperando su respuesta...")
    respuesta = escuchar(reconocedor, microfono, marcar_escuchando=True)
    estado.set_estado("reposo")

    if not respuesta:
        return  # no dijo nada claro -> no cuenta como aceptar ni rechazar

    if _RE_RESPUESTA_SI.search(respuesta.lower()):
        skills.habitos.registrar_respuesta_sugerencia(categoria, aceptada=True)
        accion = skills.habitos.ACCION_SUGERIDA.get(categoria)
        if accion:
            procesar_comando(accion)
        else:
            voice.hablar("Listo.")
    elif _RE_RESPUESTA_NO.search(respuesta.lower()):
        skills.habitos.registrar_respuesta_sugerencia(categoria, aceptada=False)
        voice.hablar("Entendido.")
    # cualquier otra cosa (cambió de tema, dijo otro comando) se ignora
    # aquí sin contar como rechazo -no es justo penalizar una sugerencia
    # solo porque el usuario tenía otra cosa en mente.


def iniciar():
    global _UMBRAL_VOZ
    reconocedor = sr.Recognizer()
    reconocedor.dynamic_energy_threshold = True
    microfono = SoundDeviceMicrophone()

    estado.log("=" * 40)
    estado.log("A.Z.M.U.T.H. — sistema iniciado")
    estado.set_estado("ejecutando", "Calibrando micrófono")
    _UMBRAL_VOZ = calibrar_umbral()
    estado.log(f'Diga "{config.PALABRA_CLAVE}" seguido de su comando')
    estado.log("=" * 40)

    estado.set_estado("ejecutando", "Iniciando sistema")
    voice.hablar("Sistema iniciado. A sus órdenes.")
    estado.set_estado("reposo")

    threading.Thread(target=_vigilar_recordatorios, daemon=True).start()
    threading.Thread(target=_vigilar_perfil, daemon=True).start()

    while True:
        try:
            texto = escuchar(reconocedor, microfono)
            if not texto:
                _revisar_sugerencia_pendiente(reconocedor, microfono)
                continue

            t_norm = texto.lower().strip()

            if PALABRA_CLAVE in t_norm:
                partes = t_norm.split(PALABRA_CLAVE, 1)
                resto = partes[1].strip() if len(partes) > 1 else ""

                if len(resto) > 2:
                    procesar_comando(resto)
                else:
                    estado.set_estado("escuchando", "Dígame...")
                    voice.hablar("Dígame.")
                    time.sleep(0.3)
                    comando = escuchar(reconocedor, microfono, marcar_escuchando=True)
                    if comando:
                        procesar_comando(comando)
                    else:
                        voice.hablar("No escuché ningún comando.")
                        time.sleep(1.0)
                    estado.set_estado("reposo")
                continue

        except SystemExit:
            raise
        except Exception as e:
            estado.log(f"[ERROR]: {e}")
            estado.set_estado("reposo")
            time.sleep(1)
            continue


def main():
    iniciar()


if __name__ == "__main__":
    _mutex_instancia = estado.asegurar_instancia_unica()
    try:
        iniciar()
    except KeyboardInterrupt:
        print("\nAzmuth apagado.")
