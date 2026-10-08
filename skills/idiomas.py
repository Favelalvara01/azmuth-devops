"""
Skill: idiomas — cambia el idioma de Azmuth (voz, respuestas e interfaz).

Español -> inglés: "cambia a inglés", "habla en inglés", "pon el idioma en inglés",
                   "switch to English", "speak English", "English mode".
Inglés -> español: "cambia a español", "switch to Spanish", "speak Spanish"...
"""
import re

import config
import idioma

_A_INGLES = re.compile(
    r"^(?:(?:cambia|cambiar|pon|poner|configura|activa)\s+(?:el\s+)?(?:idioma\s+)?(?:a|al|en)\s+ingl[eé]s"
    r"|(?:habla|h[aá]blame|contesta|responde)(?:me)?\s+en\s+ingl[eé]s|modo\s+ingl[eé]s|idioma\s+ingl[eé]s"
    r"|(?:switch|change)\s+(?:the\s+language\s+)?to\s+english|speak\s+(?:in\s+)?english|english(?:\s+mode)?"
    r"|(?:set\s+)?(?:the\s+)?language\s+(?:to\s+)?english)$")
_A_ESPANOL = re.compile(
    r"^(?:(?:cambia|cambiar|pon|poner|configura|activa)\s+(?:el\s+)?(?:idioma\s+)?(?:a|al|en)\s+espa[ñn]ol"
    r"|(?:habla|h[aá]blame|contesta|responde)(?:me)?\s+en\s+espa[ñn]ol|modo\s+espa[ñn]ol|idioma\s+espa[ñn]ol"
    r"|(?:switch|change)\s+(?:the\s+language\s+)?(?:back\s+)?to\s+spanish|speak\s+(?:in\s+)?spanish"
    r"|spanish(?:\s+mode)?|(?:set\s+)?(?:the\s+)?language\s+(?:to\s+)?spanish)$")


def _limpio(texto: str) -> str:
    t = re.sub(r"[¿?¡!.,]", "", (texto or "").lower()).strip()
    return re.sub(r"^(?:(?:hey|ok|oye)\s+)?(?:azmuth\s+)?(?:please\s+|por\s+favor\s+)?", "", t).strip()


# El dictado en inglés no siempre escribe la frase exacta ("are you a switch in
# Spanish" en vez de "switch to Spanish"). En frases cortas basta con que aparezca
# el idioma junto a una palabra de cambio.
_VERBOS_CAMBIO = re.compile(r"\b(?:switch|change|speak|talk|mode|language|back|cambia|habla|modo|idioma|pon)\b")


def _pide_cambio(t: str, idioma_nombre: str) -> bool:
    return len(t.split()) <= 7 and bool(re.search(idioma_nombre, t)) and bool(_VERBOS_CAMBIO.search(t))


def intentar(texto: str):
    t = _limpio(texto)
    if not _A_ESPANOL.match(t) and idioma.es_ingles() and _pide_cambio(t, r"\b(?:spanish|espa[ñn]ol)\b"):
        t = "spanish"
    elif not _A_INGLES.match(t) and not idioma.es_ingles() and _pide_cambio(t, r"\bingl[eé]s\b|\benglish\b"):
        t = "english"
    if _A_INGLES.match(t):
        if idioma.es_ingles():
            return "I'm already speaking English."
        idioma.cambiar("en")
        return ("Done! From now on I'll understand and answer in English. "
                f"Say \"{config.PALABRA_CLAVE_EN}\" before your command, and \"switch to Spanish\" to go back.")
    if _A_ESPANOL.match(t):
        if not idioma.es_ingles():
            return "Ya estoy hablando en español."
        idioma.cambiar("es")
        return "¡Listo! A partir de ahora le entiendo y le contesto en español."
    return None
