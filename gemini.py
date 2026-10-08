"""Cliente mínimo de Google Gemini (API REST) para usar Azmuth sin clave de Anthropic.

Se usa solo cuando el .env NO tiene ANTHROPIC_API_KEY pero sí GEMINI_API_KEY
(la clave se saca gratis en https://aistudio.google.com). Recibe los mensajes en
el mismo formato que la API de Claude y los convierte al de Gemini, así el resto
de Azmuth no tiene que saber qué IA está usando.

No usa ninguna librería nueva (solo `requests`), para no engordar Azmuth.exe.
"""
import time

import requests

import config

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
# Si un modelo no existe (404) o está saturado (503), se prueba el siguiente.
# Se usan los alias "-latest" (Google los apunta al modelo vigente) y después
# modelos con nombre fijo, por si un alias falla o está saturado.
_RESPALDOS = ("gemini-flash-latest", "gemini-3.5-flash-lite", "gemini-3-flash-preview")
_REINTENTABLES = (404, 500, 503)
_FRASES_RETIRADO = ("no longer available", "not found", "is not supported")
_TIMEOUT = 25  # si un modelo tarda más, se pasa al siguiente en vez de dejar al usuario esperando
_modelo_que_funciona = None  # se recuerda para no volver a probar los que fallaron


class ErrorGemini(RuntimeError):
    pass


def _partes(contenido):
    """Convierte el contenido de un mensaje estilo Claude (texto o bloques) en partes de Gemini."""
    if isinstance(contenido, str):
        return [{"text": contenido}]
    partes = []
    for bloque in contenido:
        if bloque.get("type") == "text":
            partes.append({"text": bloque["text"]})
        elif bloque.get("type") == "image":
            fuente = bloque["source"]
            partes.append({"inline_data": {"mime_type": fuente["media_type"], "data": fuente["data"]}})
    return partes


def convertir(system: str, mensajes: list, max_tokens: int) -> dict:
    contenidos = [{"role": "model" if m["role"] == "assistant" else "user", "parts": _partes(m["content"])}
                  for m in mensajes]
    return {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": contenidos,
        # Los modelos Flash recientes "piensan" antes de contestar y eso también
        # gasta tokens de salida: se deja margen para que la respuesta no se corte.
        # Un asistente de voz necesita rapidez: se pide el mínimo de "pensamiento".
        "generationConfig": {"maxOutputTokens": max_tokens + 2048, "thinkingConfig": {"thinkingLevel": "low"}},
    }


def _texto(datos: dict) -> str:
    candidatos = datos.get("candidates") or []
    if not candidatos:
        motivo = (datos.get("promptFeedback") or {}).get("blockReason", "sin respuesta")
        raise ErrorGemini(f"Gemini no respondió ({motivo})")
    partes = (candidatos[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()


def _avisar(texto: str):
    try:
        import estado
        import monitoreo
        estado.log(texto)
        monitoreo.registrar_evento(texto)  # queda en datos/errores.log para revisar tiempos
    except Exception:
        pass


def _detalle(r) -> str:
    try:
        return r.json()["error"]["message"]
    except Exception:
        return r.text[:200]


def completar(system: str, mensajes: list, max_tokens: int = 800) -> str:
    global _modelo_que_funciona
    cuerpo = convertir(system, mensajes, max_tokens)
    modelos = list(dict.fromkeys([m for m in (_modelo_que_funciona, config.GEMINI_MODELO, *_RESPALDOS) if m]))
    ultimo = None
    inicio = time.time()
    for modelo in modelos:
        try:
            r = requests.post(_URL.format(modelo=modelo), json=cuerpo, timeout=_TIMEOUT,
                              headers={"x-goog-api-key": config.GEMINI_API_KEY})
        except requests.Timeout:
            _avisar(f"Gemini ({modelo}) tardó más de {_TIMEOUT} s, se prueba otro")
            continue  # tardó demasiado: siguiente modelo
        if r.status_code == 400 and "thinking" in _detalle(r).lower() and "thinkingConfig" in cuerpo["generationConfig"]:
            # este modelo no acepta el nivel de pensamiento: se repite la petición sin él
            cuerpo["generationConfig"].pop("thinkingConfig")
            r = requests.post(_URL.format(modelo=modelo), json=cuerpo, timeout=_TIMEOUT,
                              headers={"x-goog-api-key": config.GEMINI_API_KEY})
        if r.status_code == 200:
            _modelo_que_funciona = modelo
            _avisar(f"🧠 Gemini ({modelo}) respondió en {time.time() - inicio:.1f} s")
            return _texto(r.json())
        if r.status_code == 429:
            raise ErrorGemini("se alcanzó el límite gratuito de Gemini; espere un momento e intente de nuevo")
        retirado = any(f in _detalle(r).lower() for f in _FRASES_RETIRADO)
        if r.status_code not in _REINTENTABLES and not retirado:
            raise ErrorGemini(f"Gemini respondió {r.status_code}: {_detalle(r)}")
        ultimo = r
        _avisar(f"Gemini ({modelo}) falló con {r.status_code}: {_detalle(r)[:80]}")
        if modelo == _modelo_que_funciona:
            _modelo_que_funciona = None  # dejó de funcionar: se vuelve a buscar
        time.sleep(0.3)  # el modelo no existe o está saturado: se intenta con el siguiente
    if ultimo is not None and ultimo.status_code == 503:
        raise ErrorGemini("los servidores de Gemini están saturados en este momento; intente de nuevo en unos segundos")
    raise ErrorGemini(f"ningún modelo de Gemini respondió ({_detalle(ultimo) if ultimo is not None else 'sin respuesta'})")
