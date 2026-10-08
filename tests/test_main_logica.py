"""Lógica de main.py separada del micrófono (sube la cobertura del motor de voz)."""
import io
import wave
from unittest import mock

import numpy as np
import pytest

import main
import monitoreo


@pytest.fixture
def m(monkeypatch):
    monkeypatch.setattr(main.voice, "hablar", mock.MagicMock())
    monkeypatch.setattr(main.time, "sleep", lambda *_: None)
    return main


def _cuadro(valor):
    return np.full((1024, 1), valor, dtype=np.int16)


# ---------- DetectorVoz ----------
def test_detector_corta_tras_silencio():
    d = main.DetectorVoz(umbral=100, max_silencio=3)
    assert d.procesar(_cuadro(500), 500) is False and d.hablando
    resultados = [d.procesar(_cuadro(10), 10) for _ in range(4)]
    assert resultados == [False, False, False, True]
    assert len(d.frames) == 5


def test_detector_pausa_corta_no_corta():
    d = main.DetectorVoz(umbral=100, max_silencio=3)
    d.procesar(_cuadro(500), 500)
    d.procesar(_cuadro(10), 10)
    d.procesar(_cuadro(10), 10)
    d.procesar(_cuadro(400), 400)  # vuelve a hablar: reinicia el conteo
    assert [d.procesar(_cuadro(10), 10) for _ in range(3)] == [False, False, False]


def test_detector_se_rinde_si_nadie_habla():
    d = main.DetectorVoz(umbral=100, max_espera=2)
    assert [d.procesar(_cuadro(5), 5) for _ in range(3)] == [False, False, True]
    assert d.frames == []


def test_detector_limite_de_frase_larga():
    d = main.DetectorVoz(umbral=100, max_frames=3)
    salidas = [d.procesar(_cuadro(500), 500) for _ in range(5)]
    assert salidas[-1] is True


def test_frames_a_wav():
    buf = main.frames_a_wav([_cuadro(1), _cuadro(2)])
    with wave.open(buf) as wf:
        assert wf.getframerate() == 16000 and wf.getnframes() == 2048


# ---------- escuchar / transcribir ----------
def test_escuchar_sin_frames(m):
    assert m.escuchar(None, None, grabar=lambda: []) is None


def test_escuchar_transcribe(m):
    rec = mock.MagicMock()
    rec.recognize_google.return_value = "azmuth hola"
    assert m.escuchar(rec, None, marcar_escuchando=True, grabar=lambda: [_cuadro(300)]) == "azmuth hola"


def test_escuchar_no_entendio(m, monkeypatch):
    class NoEntendi(Exception):
        pass
    monkeypatch.setattr(m.sr, "UnknownValueError", NoEntendi)
    monkeypatch.setattr(m.sr, "RequestError", NoEntendi)
    rec = mock.MagicMock()
    rec.recognize_google.side_effect = NoEntendi()
    assert m.transcribir(rec, io.BytesIO()) is None


def test_escuchar_error_de_audio_queda_registrado(m):
    def falla():
        raise OSError("micrófono desconectado")
    assert m.escuchar(None, None, grabar=falla) is None
    assert monitoreo.resumen()["ultimos_errores"][-1]["origen"] == "audio"


def test_calibrar_umbral(monkeypatch):
    stream = mock.MagicMock()
    stream.__enter__.return_value.read.return_value = (_cuadro(100), None)
    monkeypatch.setattr(main.sd, "InputStream", mock.MagicMock(return_value=stream))
    assert main.calibrar_umbral(duracion_seg=0.1) == int(100 * 2.5 + 40)


def test_calibrar_umbral_respaldo(monkeypatch):
    monkeypatch.setattr(main.sd, "InputStream", mock.MagicMock(side_effect=OSError("sin mic")))
    assert main.calibrar_umbral() == int(max(80, 60 * 2.5 + 40))


# ---------- texto ----------
@pytest.mark.parametrize("frase,esperado", [
    ("apágate", False), ("apagate ya", True), ("desactivar", True), ("abre paint", False)])
def test_es_apagado(frase, esperado):
    assert main.es_apagado(frase) is esperado


@pytest.mark.parametrize("frase,esperado", [
    ("Azmuth, paint", "abre paint"), ("oye azmuth toma nota: x", "toma nota: x"),
    ("Spotify", "abre spotify"), ("qué hora es", "qué hora es")])
def test_normalizar_comando(frase, esperado):
    assert main.normalizar_comando(frase) == esperado


CLAVE = main.PALABRA_CLAVE  # "hora de ser heroe" por defecto (config.py / .env)


@pytest.mark.parametrize("texto,esperado", [
    (f"{CLAVE} abre paint", "abre paint"), (CLAVE, ""), ("hola a todos", None)])
def test_extraer_comando(texto, esperado):
    assert main.extraer_comando(texto) == esperado


@pytest.mark.parametrize("resp,esperado", [
    ("sí, por favor", "si"), ("claro", "si"), ("no gracias", "no"), ("ponme música", None)])
def test_clasificar_respuesta(resp, esperado):
    assert main.clasificar_respuesta(resp) == esperado


# ---------- flujo ----------
def test_responder_en_modo_escritorio(m, monkeypatch):
    monkeypatch.setattr(m.estado, "obtener_modo", lambda: "escritorio")
    monkeypatch.setattr(m.nucleo, "responder_en_chat", lambda t, origen: ("**Hola** " + "x" * 400, "ia", 1))
    completa, hablada = m.responder_segun_modo("hola")
    assert completa.startswith("**Hola**") and "**" not in hablada and len(hablada) < len(completa)


def test_apagado_termina_el_proceso(m, monkeypatch):
    salir = mock.MagicMock()
    monkeypatch.setattr(m.os, "_exit", salir)
    monkeypatch.setattr(m, "responder_segun_modo", mock.MagicMock(return_value=("", "")))
    m.procesar_comando("Azmuth, apágate el sistema por favor apagar")
    salir.assert_called_once_with(0)


def test_atender_ignora_frases_sin_palabra_clave(m):
    assert m.atender("hola mundo", None, None) is False


def test_atender_comando_completo(m, monkeypatch):
    procesar = mock.MagicMock()
    monkeypatch.setattr(m, "procesar_comando", procesar)
    assert m.atender(f"{CLAVE} qué hora es", None, None) is True
    procesar.assert_called_once_with("qué hora es")


def test_atender_pide_el_comando_despues(m, monkeypatch):
    procesar = mock.MagicMock()
    monkeypatch.setattr(m, "procesar_comando", procesar)
    monkeypatch.setattr(m, "escuchar", lambda *a, **k: "abre paint")
    m.atender(CLAVE, None, None)
    m.voice.hablar.assert_called_with("Dígame.")
    procesar.assert_called_once_with("abre paint")


def test_atender_no_escucho_nada(m, monkeypatch):
    monkeypatch.setattr(m, "escuchar", lambda *a, **k: None)
    m.atender(CLAVE, None, None)
    m.voice.hablar.assert_called_with("No escuché ningún comando.")


# ---------- sugerencias de hábitos ----------
def _sugerencia(m, monkeypatch, respuesta, accion=None):
    monkeypatch.setattr(m.skills.habitos, "sugerir_por_hora", lambda: ("¿Le pongo música?", "musica"))
    monkeypatch.setattr(m.skills.habitos, "ACCION_SUGERIDA", {"musica": accion} if accion else {})
    registrar = mock.MagicMock()
    monkeypatch.setattr(m.skills.habitos, "registrar_respuesta_sugerencia", registrar)
    monkeypatch.setattr(m, "escuchar", lambda *a, **k: respuesta)
    procesar = mock.MagicMock()
    monkeypatch.setattr(m, "procesar_comando", procesar)
    m._revisar_sugerencia_pendiente(None, None)
    return registrar, procesar


def test_sugerencia_aceptada_ejecuta_accion(m, monkeypatch):
    registrar, procesar = _sugerencia(m, monkeypatch, "sí", accion="pon mi playlist")
    registrar.assert_called_once_with("musica", aceptada=True)
    procesar.assert_called_once_with("pon mi playlist")


def test_sugerencia_aceptada_sin_accion(m, monkeypatch):
    _sugerencia(m, monkeypatch, "claro")
    m.voice.hablar.assert_called_with("Listo.")


def test_sugerencia_rechazada(m, monkeypatch):
    registrar, _ = _sugerencia(m, monkeypatch, "no")
    registrar.assert_called_once_with("musica", aceptada=False)


def test_sugerencia_sin_respuesta_no_cuenta(m, monkeypatch):
    registrar, _ = _sugerencia(m, monkeypatch, None)
    registrar.assert_not_called()


def test_sin_sugerencia_no_habla(m, monkeypatch):
    monkeypatch.setattr(m.skills.habitos, "sugerir_por_hora", lambda: None)
    m._revisar_sugerencia_pendiente(None, None)
    m.voice.hablar.assert_not_called()


# ---------- vigilantes y arranque ----------
def test_recordatorios_vencidos_se_dicen(m, monkeypatch):
    monkeypatch.setattr(m.skills.recordatorios, "revisar_pendientes", lambda: ["tomar agua"])
    assert m.revisar_recordatorios_una_vez() == 1
    m.voice.hablar.assert_called_with("Recordatorio: tomar agua")


def test_error_en_recordatorios_queda_en_el_log(m, monkeypatch, log_temporal):
    def falla():
        raise RuntimeError("bd bloqueada")
    monkeypatch.setattr(m.skills.recordatorios, "revisar_pendientes", falla)
    assert m.revisar_recordatorios_una_vez() == 0
    assert "bd bloqueada" in log_temporal.read_text(encoding="utf-8")


def test_iniciar_recorre_el_bucle(m, monkeypatch):
    monkeypatch.setattr(m, "calibrar_umbral", lambda: 123)
    monkeypatch.setattr(m.threading, "Thread", mock.MagicMock())
    frases = iter([None, f"{CLAVE} abre paint", "algo", RuntimeError("falla"), SystemExit()])

    def escuchar_falso(*a, **k):
        x = next(frases)
        if isinstance(x, BaseException):
            raise x
        return x
    monkeypatch.setattr(m, "escuchar", escuchar_falso)
    monkeypatch.setattr(m, "_revisar_sugerencia_pendiente", mock.MagicMock())
    procesar = mock.MagicMock()
    monkeypatch.setattr(m, "procesar_comando", procesar)
    with pytest.raises(SystemExit):
        m.iniciar()
    assert m._UMBRAL_VOZ == 123
    procesar.assert_called_once_with("abre paint")
    assert monitoreo.resumen()["ultimos_errores"][-1]["origen"] == "bucle principal"


def test_microfono_compatible():
    mic = main.SoundDeviceMicrophone()
    with mic as mm:
        assert (mm.CHUNK, mm.SAMPLE_RATE, mm.SAMPLE_WIDTH) == (1024, 16000, 2)
