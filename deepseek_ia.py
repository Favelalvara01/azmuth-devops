"""Cliente mínimo de DeepSeek (API compatible con OpenAI, de pago y muy económica).

Se usa para conversar cuando el .env tiene DEEPSEEK_API_KEY (https://platform.deepseek.com
→ API keys). Va después de Claude y antes de las gratuitas (Groq y Gemini). Para "¿qué hay
en mi pantalla?" se usa Claude o Gemini.

Si el modelo configurado ya no existe, se prueban los de respaldo y luego los que la
API diga que tiene disponibles.
"""
import time

import requests

import config

_BASE = "https://api.deepseek.com"
_RESPALDOS = ("deepseek-flash", "deepseek-v4-pro", "deepseek-chat")
_TIMEOUT = 40
_modelo_que_funciona = None


class ErrorDeepSeek(RuntimeError):
    pass


def _headers():
    return {"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"}


def _detalle(r) -> str:
    try:
        return r.json()["error"]["message"]
    except Exception:
        return (getattr(r, "text", "") or "")[:200]


def _texto(contenido) -> str:
    if isinstance(contenido, str):
        return contenido
    return "\n".join(b.get("text", "") for b in contenido if b.get("type") == "text")


def convertir(system: str, mensajes: list, max_tokens: int) -> dict:
    return {
        "messages": [{"role": "system", "content": system}]
        + [{"role": m["role"], "content": _texto(m["content"])} for m in mensajes],
        "max_tokens": max_tokens + 1024,
        "thinking": {"type": "disabled"},  # sin "pensar" = responde más rápido (asistente de voz)
        "stream": False,
    }


def modelos_disponibles() -> list:
    try:
        r = requests.get(f"{_BASE}/models", headers=_headers(), timeout=10)
        return [m["id"] for m in r.json().get("data", [])]
    except Exception:
        return []


def _pedir(modelo, cuerpo):
    try:
        r = requests.post(f"{_BASE}/chat/completions", json=dict(cuerpo, model=modelo), headers=_headers(), timeout=_TIMEOUT)
    except requests.Timeout:
        _avisar(f"DeepSeek ({modelo}) tardó más de {_TIMEOUT} s, se prueba otro")
        return None
    if r.status_code == 400 and "thinking" in cuerpo and "think" in _detalle(r).lower():
        cuerpo.pop("thinking")  # este modelo no acepta apagar el razonamiento: se repite sin eso
        return _pedir(modelo, cuerpo)
    return r


def _revisar_error(r):
    if r.status_code in (401, 403):
        raise ErrorDeepSeek(f"la clave de DeepSeek no es válida ({_detalle(r)[:80]})")
    if r.status_code == 402:
        raise ErrorDeepSeek("la cuenta de DeepSeek no tiene saldo; recárguela en platform.deepseek.com")
    if r.status_code == 429:
        raise ErrorDeepSeek("DeepSeek está recibiendo demasiadas peticiones; espere un momento")


def completar(system: str, mensajes: list, max_tokens: int = 800) -> str:
    global _modelo_que_funciona
    cuerpo = convertir(system, mensajes, max_tokens)
    candidatos = list(dict.fromkeys(m for m in (_modelo_que_funciona, config.DEEPSEEK_MODELO, *_RESPALDOS) if m))
    probados, ultimo, inicio = set(), None, time.time()
    for _ronda in range(2):  # 2.ª ronda: los modelos que la cuenta tiene disponibles hoy
        for modelo in [m for m in candidatos if m not in probados]:
            probados.add(modelo)
            r = _pedir(modelo, cuerpo)
            if r is not None and r.status_code == 200:
                _modelo_que_funciona = modelo
                _avisar(f"🐋 DeepSeek ({modelo}) respondió en {time.time() - inicio:.1f} s")
                return (r.json()["choices"][0]["message"].get("content") or "").strip()
            if r is not None:
                _revisar_error(r)
                ultimo = r
                _avisar(f"DeepSeek ({modelo}) falló con {r.status_code}: {_detalle(r)[:80]}")
        _modelo_que_funciona = None
        candidatos = modelos_disponibles()
    raise ErrorDeepSeek(f"ningún modelo de DeepSeek respondió ({_detalle(ultimo) if ultimo is not None else 'sin respuesta'})")


def _avisar(texto: str):
    try:
        import estado
        import monitoreo
        estado.log(texto)
        monitoreo.registrar_evento(texto)
    except Exception:
        pass
