"""Cliente mínimo de Google Gemini (API REST) para usar Azmuth sin clave de Anthropic.

Se usa solo cuando el .env NO tiene ANTHROPIC_API_KEY pero sí GEMINI_API_KEY
(la clave se saca gratis en https://aistudio.google.com). Recibe los mensajes en
el mismo formato que la API de Claude y los convierte al de Gemini, así el resto
de Azmuth no tiene que saber qué IA está usando.

No usa ninguna librería nueva (solo `requests`), para no engordar Azmuth.exe.
"""
import requests

import config

_URL = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
_MODELO_RESPALDO = "gemini-2.5-flash"
_TIMEOUT = 60


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
        "generationConfig": {"maxOutputTokens": max_tokens + 2048},
    }


def _texto(datos: dict) -> str:
    candidatos = datos.get("candidates") or []
    if not candidatos:
        motivo = (datos.get("promptFeedback") or {}).get("blockReason", "sin respuesta")
        raise ErrorGemini(f"Gemini no respondió ({motivo})")
    partes = (candidatos[0].get("content") or {}).get("parts") or []
    return "".join(p.get("text", "") for p in partes if not p.get("thought")).strip()


def completar(system: str, mensajes: list, max_tokens: int = 800) -> str:
    cuerpo = convertir(system, mensajes, max_tokens)
    modelos = [config.GEMINI_MODELO] + ([_MODELO_RESPALDO] if config.GEMINI_MODELO != _MODELO_RESPALDO else [])
    for i, modelo in enumerate(modelos):
        r = requests.post(_URL.format(modelo=modelo), json=cuerpo, timeout=_TIMEOUT,
                          headers={"x-goog-api-key": config.GEMINI_API_KEY})
        if r.status_code == 404 and i + 1 < len(modelos):
            continue  # el alias del modelo cambió: se intenta con el de respaldo
        if r.status_code == 429:
            raise ErrorGemini("se alcanzó el límite gratuito de Gemini; espere un momento e intente de nuevo")
        if r.status_code != 200:
            try:
                detalle = r.json()["error"]["message"]
            except Exception:
                detalle = r.text[:200]
            raise ErrorGemini(f"Gemini respondió {r.status_code}: {detalle}")
        return _texto(r.json())
    raise ErrorGemini("no se encontró un modelo de Gemini disponible")
