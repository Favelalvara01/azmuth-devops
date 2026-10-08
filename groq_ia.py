"""Cliente mínimo de Groq (API compatible con OpenAI): IA gratuita y muy rápida.

Se usa para la conversación cuando el .env NO tiene ANTHROPIC_API_KEY pero sí
GROQ_API_KEY (gratis en https://console.groq.com/keys). Groq no se usa para ver
imágenes: para "¿qué hay en mi pantalla?" Azmuth usa Gemini si hay clave.

Como Groq retira modelos seguido, si el modelo configurado ya no existe se
pregunta a la API qué modelos de chat tiene y se usa el primero disponible.
"""
import time

import requests

import config

_BASE = "https://api.groq.com/openai/v1"
_RESPALDOS = ("openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.1-8b-instant")
_TIMEOUT = 25
_NO_CHAT = ("whisper", "tts", "guard", "playai", "orpheus", "prompt-guard", "compound")
_modelo_que_funciona = None


class ErrorGroq(RuntimeError):
    pass


def _headers():
    return {"Authorization": f"Bearer {config.GROQ_API_KEY}"}


def _detalle(r) -> str:
    try:
        return r.json()["error"]["message"]
    except Exception:
        return r.text[:200]


def _texto(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    return "\n".join(b.get("text", "") for b in contenido if b.get("type") == "text")


def convertir(system: str, mensajes: list, max_tokens: int) -> dict:
    return {
        "messages": [{"role": "system", "content": system}]
        + [{"role": m["role"], "content": _texto(m["content"])} for m in mensajes],
        "max_completion_tokens": max_tokens + 1024,
    }


def modelos_disponibles() -> list:
    """Modelos de chat que la cuenta puede usar ahora mismo (por si los de la lista se retiraron)."""
    try:
        r = requests.get(f"{_BASE}/models", headers=_headers(), timeout=10)
        ids = [m["id"] for m in r.json().get("data", []) if m.get("active", True)]
    except Exception:
        return []
    return [i for i in ids if not any(x in i.lower() for x in _NO_CHAT)]


def _pedir(modelo, cuerpo):
    datos = dict(cuerpo, model=modelo)
    if modelo.startswith("openai/gpt-oss"):
        datos["reasoning_effort"] = "low"  # razonar poco = responder más rápido
    return requests.post(f"{_BASE}/chat/completions", json=datos, headers=_headers(), timeout=_TIMEOUT)


def _revisar_error(r):
    if r.status_code == 429:
        raise ErrorGroq("se alcanzó el límite gratuito de Groq; espere un momento e intente de nuevo")
    if r.status_code in (401, 403):
        raise ErrorGroq(f"la clave de Groq no es válida ({_detalle(r)[:80]})")


def _intentar(modelo, cuerpo):
    """Devuelve la respuesta del modelo, o None si tardó demasiado."""
    try:
        return _pedir(modelo, cuerpo)
    except requests.Timeout:
        _avisar(f"Groq ({modelo}) tardó más de {_TIMEOUT} s, se prueba otro")
        return None


def completar(system: str, mensajes: list, max_tokens: int = 800) -> str:
    global _modelo_que_funciona
    cuerpo = convertir(system, mensajes, max_tokens)
    candidatos = list(dict.fromkeys([m for m in (_modelo_que_funciona, config.GROQ_MODELO, *_RESPALDOS) if m]))
    probados, ultimo, inicio = set(), None, time.time()
    for ronda in range(2):  # 2.ª ronda: los modelos que la cuenta tiene disponibles hoy
        for modelo in [m for m in candidatos if m not in probados]:
            probados.add(modelo)
            r = _intentar(modelo, cuerpo)
            if r is not None and r.status_code == 200:
                _modelo_que_funciona = modelo
                _avisar(f"⚡ Groq ({modelo}) respondió en {time.time() - inicio:.1f} s")
                return (r.json()["choices"][0]["message"].get("content") or "").strip()
            if r is not None:
                _revisar_error(r)
                ultimo = r
                _avisar(f"Groq ({modelo}) falló con {r.status_code}: {_detalle(r)[:80]}")
        _modelo_que_funciona = None
        candidatos = modelos_disponibles()
    raise ErrorGroq(f"ningún modelo de Groq respondió ({_detalle(ultimo) if ultimo is not None else 'sin respuesta'})")


def _avisar(texto: str):
    try:
        import estado
        import monitoreo
        estado.log(texto)
        monitoreo.registrar_evento(texto)
    except Exception:
        pass
