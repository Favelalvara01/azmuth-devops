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
import idioma
import tematicas
import monitoreo
import notificaciones
import nucleo

# Si al comando le antepone el nombre del asistente ("Azmuth, recuerda que...",
# "oye Azmuth, toma nota..."), se lo quitamos ANTES de mandarlo a las skills.
# Sin esto, un patrón anclado al inicio de la frase (como el de "recuerda
# que..." en skills/memoria.py) nunca haría match porque la frase no
# empezaría en "recuerda" sino en "azmuth,".
_VOCATIVO_RE = re.compile(r"^(?:oye\s+|hey\s+)?azmuth[,]?\s+", re.IGNORECASE)

PALABRA_CLAVE = config.PALABRA_CLAVE.lower().strip()
PALABRA_CLAVE_EN = config.PALABRA_CLAVE_EN.lower().strip()


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


def revisar_recordatorios_una_vez() -> int:
    """Avisa los recordatorios vencidos. Devuelve cuántos avisó."""
    try:
        avisos = skills.recordatorios.revisar_pendientes()
        for texto in avisos:
            titulo = idioma.t("Recordatorio", "Reminder")
            notificaciones.notificar(idioma.t("⏰ Recordatorio de Azmuth", "⏰ Azmuth reminder"), texto)
            estado.set_estado("ejecutando", f"{titulo}: {texto}")
            voice.hablar(f"{titulo}: {texto}")
            estado.set_estado("reposo")
        return len(avisos)
    except Exception as e:
        monitoreo.registrar_error("vigilante de recordatorios", e)
        return 0


def _vigilar_recordatorios():
    while True:
        revisar_recordatorios_una_vez()
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


class DetectorVoz:
    """Decide, cuadro por cuadro, cuándo empieza y cuándo termina una frase.

    Se separó del micrófono para poder probarlo sin hardware.
    Antes esperaba ~1.9s de silencio (lento) y luego lo bajé a ~0.9s
    (muy agresivo: cortaba la frase si hacías una pausa corta al hablar).
    ~1.3s (20 cuadros) es el punto medio.
    """

    def __init__(self, umbral, max_silencio=20, max_espera=200, max_frames=None,
                 sample_rate=16000, chunk_size=1024):
        self.umbral = umbral
        self.max_silencio = max_silencio
        self.max_espera = max_espera
        self.max_frames = max_frames or (sample_rate / chunk_size) * 15
        self.frames = []
        self.hablando = False
        self._silencio = 0
        self._espera = 0

    def procesar(self, chunk, volumen) -> bool:
        """Agrega el cuadro. Devuelve True cuando ya hay que dejar de grabar."""
        if not self.hablando:
            return self._esperando_voz(chunk, volumen)
        self.frames.append(chunk)
        self._silencio = self._silencio + 1 if volumen < self.umbral else 0
        return self._silencio > self.max_silencio or len(self.frames) > self.max_frames

    def _esperando_voz(self, chunk, volumen) -> bool:
        self._espera += 1
        if volumen > self.umbral:
            self.hablando = True
            self.frames.append(chunk)
            estado.log("🎤 Voz detectada...")
            return False
        return self._espera > self.max_espera


def frames_a_wav(frames, sample_rate=16000) -> io.BytesIO:
    audio_data = np.concatenate(frames, axis=0)
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data.tobytes())
    wav_buffer.seek(0)
    return wav_buffer


def _grabar_frase(sample_rate=16000, chunk_size=1024):
    detector = DetectorVoz(_UMBRAL_VOZ, sample_rate=sample_rate, chunk_size=chunk_size)
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
        while True:
            audio_chunk, _ = stream.read(chunk_size)
            if detector.procesar(audio_chunk, np.max(np.abs(audio_chunk))):
                break
    return detector.frames


def transcribir(reconocedor, wav_buffer):
    """Convierte el WAV en texto con Google. None si no se entendió."""
    with sr.AudioFile(wav_buffer) as fuente:
        audio = reconocedor.record(fuente)
    try:
        texto = reconocedor.recognize_google(audio, language=idioma.codigo_voz())
        estado.log(f"🎤 Escuché: {texto}")
        return texto
    except (sr.UnknownValueError, sr.RequestError):
        return None


def escuchar(reconocedor, microfono, marcar_escuchando=False, grabar=None):
    if marcar_escuchando:
        estado.set_estado("escuchando", "Capturando su orden...")
    try:
        frames = (grabar or _grabar_frase)()
        if not frames:
            return None
        return transcribir(reconocedor, frames_a_wav(frames))
    except Exception as e:
        estado.log(f"[Audio Error]: {e}")
        monitoreo.registrar_error("audio", e)
        return None


_PALABRAS_APAGADO = ("apagate", "apagar", "apagar sistema", "apagar azmuth", "desactivar", "apaga el sistema",
                     "shut down", "shutdown", "power off", "turn yourself off")
_APPS_DIRECTAS = ("roblox", "fortnite", "rocket league", "spotify", "xbox", "edge", "word", "excel",
                  "paint", "bloc de notas")


def es_apagado(texto: str) -> bool:
    t = texto.lower().strip()
    return any(p in t for p in _PALABRAS_APAGADO)


def normalizar_comando(texto: str) -> str:
    """Quita el vocativo ("Azmuth, ...") y convierte "paint" en "abre paint"."""
    texto = _VOCATIVO_RE.sub("", texto, count=1).strip()
    t_limpio = texto.lower().strip()
    if t_limpio in _APPS_DIRECTAS:
        return f"abre {t_limpio}"
    return texto


def responder_segun_modo(texto: str):
    """Devuelve (respuesta completa, lo que se dice en voz alta)."""
    # En modo escritorio lo que se dice por voz también queda escrito en el
    # chat activo (y Claude usa el historial de ese chat como contexto).
    if estado.obtener_modo() == "escritorio":
        respuesta, _, _ = nucleo.responder_en_chat(texto, origen="voz")
        return respuesta, voice.texto_para_voz(respuesta)
    respuesta, _ = nucleo.responder(texto)
    return respuesta, respuesta


def procesar_comando(texto: str):
    estado.log(f"USTED: {texto}")
    estado.set_estado("procesando", texto)

    texto = normalizar_comando(texto)

    if es_apagado(texto):
        estado.set_estado("ejecutando", "Apagando sistema")
        voice.hablar(idioma.t("Apagando sistema. Hasta luego, señor.", "Shutting down. Goodbye, sir."))
        time.sleep(1.5)
        # main.iniciar() corre en un hilo secundario cuando lo lanza app_desktop.py
        # (el hilo principal está ocupado con la ventana de webview). sys.exit(0)
        # solo mata ESE hilo y la ventana se queda abierta. os._exit(0) sí termina
        # el proceso completo -incluida la ventana- sin importar en qué hilo esté.
        os._exit(0)

    respuesta, respuesta_hablada = responder_segun_modo(texto)
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
        except Exception as e:
            monitoreo.registrar_error("vigilante de perfil", e)


_RE_RESPUESTA_SI = re.compile(r"\b(s[ií]|claro|va|dale|dele|s[ií]mon|por favor|ok[aá]y?|yes|yeah|yep|sure|please)\b",
                              re.IGNORECASE)
_RE_RESPUESTA_NO = re.compile(r"\bno\b|ahorita no|después no|luego no|para nada|\bnope\b|not now", re.IGNORECASE)


def clasificar_respuesta(respuesta: str):
    """'si', 'no' o None (cambió de tema)."""
    t = respuesta.lower()
    if _RE_RESPUESTA_SI.search(t):
        return "si"
    if _RE_RESPUESTA_NO.search(t):
        return "no"
    return None


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

    decision = clasificar_respuesta(respuesta)
    if decision == "si":
        skills.habitos.registrar_respuesta_sugerencia(categoria, aceptada=True)
        accion = skills.habitos.ACCION_SUGERIDA.get(categoria)
        if accion:
            procesar_comando(accion)
        else:
            voice.hablar(idioma.t("Listo.", "Done."))
    elif decision == "no":
        skills.habitos.registrar_respuesta_sugerencia(categoria, aceptada=False)
        voice.hablar(idioma.t("Entendido.", "Understood."))
    # cualquier otra cosa (cambió de tema, dijo otro comando) se ignora
    # aquí sin contar como rechazo -no es justo penalizar una sugerencia
    # solo porque el usuario tenía otra cosa en mente.


def extraer_comando(texto: str):
    """Si la frase trae la palabra clave devuelve lo que sigue ('' si no dijo
    nada más); si no la trae devuelve None (no era para Azmuth)."""
    t_norm = texto.lower().strip().replace("’", "'")
    for clave in dict.fromkeys((PALABRA_CLAVE, PALABRA_CLAVE_EN)):
        m = _patron_clave(clave).search(t_norm) if clave else None
        if m:
            return t_norm[m.end():].strip(" ,.")
    return None


def _patron_clave(clave: str):
    """La palabra clave tolera espacios o guiones entre letras: el dictado a veces
    escribe "omni trix" u "omni-trix" en vez de "omnitrix"."""
    letras = [re.escape(c) for c in clave if not c.isspace()]
    return re.compile(r"[\s-]*".join(letras))


def atender(texto: str, reconocedor, microfono) -> bool:
    """Una vuelta del bucle principal. Devuelve True si la frase era para Azmuth."""
    resto = extraer_comando(texto)
    if resto is None:
        return False
    if len(resto) > 2:
        procesar_comando(resto)
        return True
    estado.set_estado("escuchando", "Dígame...")
    voice.hablar(idioma.t("Dígame.", "Go ahead."))
    time.sleep(0.3)
    comando = escuchar(reconocedor, microfono, marcar_escuchando=True)
    if comando:
        procesar_comando(comando)
    else:
        voice.hablar(idioma.t("No escuché ningún comando.", "I didn't hear a command."))
        time.sleep(1.0)
    estado.set_estado("reposo")
    return True


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
    tematicas.reproducir_sonido()  # sonido de temporada (Halloween, Muertos, Navidad); nada en la normal
    voice.hablar(tematicas.saludo())
    estado.set_estado("reposo")

    threading.Thread(target=_vigilar_recordatorios, daemon=True).start()
    threading.Thread(target=_vigilar_perfil, daemon=True).start()

    while True:
        try:
            texto = escuchar(reconocedor, microfono)
            if not texto:
                _revisar_sugerencia_pendiente(reconocedor, microfono)
                continue

            atender(texto, reconocedor, microfono)

        except SystemExit:
            raise
        except Exception as e:
            estado.log(f"[ERROR]: {e}")
            monitoreo.registrar_error("bucle principal", e)
            estado.set_estado("reposo")
            time.sleep(1)
            continue


def main():
    iniciar()


if __name__ == "__main__":
    _mutex_instancia = estado.asegurar_instancia_unica()
    monitoreo.instalar()
    try:
        iniciar()
    except KeyboardInterrupt:
        print("\nAzmuth apagado.")
