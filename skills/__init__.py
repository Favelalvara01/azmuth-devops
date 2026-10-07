"""
Registro central de skills.
Cada skill es un módulo con una función intentar(texto) que regresa
un texto de respuesta si supo manejar el comando, o None si no le tocaba.

IMPORTANTE sobre el orden de SKILLS: se revisan de arriba a abajo, y la
primera que conteste algo (no None) gana. "aplicaciones" tiene un patrón
muy amplio que agarra cualquier "abre X" o "cierra X", así que SIEMPRE
debe ir al final — si no, se roba comandos que le tocan a otras skills
más específicas (como "abre pestaña" o "cierra pestaña").

Por la misma razón "pestanas" va ANTES que "multimedia": la regla de
multimedia "^siguiente" se robaba "siguiente pestaña" (DEF-013).

Para agregar una skill nueva:
1. Crea un archivo nuevo aquí en skills/, por ejemplo skills/musica.py
2. Dale una función intentar(texto: str) -> str | None igual que las demás
3. Impórtala abajo y agrégala a la lista SKILLS — si usa frases como
    "abre X" o "cierra X", ponla ANTES de aplicaciones en la lista.
Ese es todo el contrato — no hay que tocar nada más del programa.
"""
import re

from . import (modos, tiempo, notas, recordatorios, memoria, contactos, habitos, web, sistema,
               multimedia, pestanas, ayuda, aplicaciones, apps_instaladas)

SKILLS = [modos, sistema, tiempo, notas, recordatorios, memoria, contactos, habitos, web,
          pestanas, multimedia, ayuda, aplicaciones, apps_instaladas]


# Palabras de comando que, escritas SIN acento, no reconocerían las skills
# (sus patrones usan la ortografía con acento que entrega el dictado por voz).
_ACENTOS = {
    "que": "qué", "cual": "cuál", "cuales": "cuáles", "como": "cómo", "donde": "dónde", "cuantos": "cuántos",
    "dia": "día", "recuerdame": "recuérdame", "llevame": "llévame", "buscame": "búscame", "mandale": "mándale",
    "escribele": "escríbele", "enviale": "envíale", "habitos": "hábitos", "pestana": "pestaña", "olvidate": "olvídate",
}
_RE_PALABRA = re.compile(r"\b(" + "|".join(_ACENTOS) + r")\b", re.IGNORECASE)


def variantes(texto: str):
    """Versiones del texto a probar, de la más fiel a la más corregida.
    DEF-016: escrito en el chat llegaba "¿Qué clima hace?" (con signos) o
    "que hora es" (sin acentos) y ninguna skill lo reconocía, aunque por voz
    sí funcionaba. Se prueba primero el texto tal cual, luego sin los signos
    de inicio/fin y luego con los acentos de las palabras de comando."""
    original = (texto or "").strip()
    limpio = original.lstrip("¿¡ ").rstrip("?!.¡¿ ").strip()
    con_acentos = _RE_PALABRA.sub(lambda m: _ACENTOS[m.group(1).lower()], limpio)
    vistas = []
    for v in (original, limpio, con_acentos):
        if v and v not in vistas:
            vistas.append(v)
    return vistas


def procesar(texto: str):
    """Prueba cada skill en orden; regresa (respuesta, nombre_skill) de la
    primera que conteste algo (no None), o (None, None) si ninguna supo
    manejarlo. El nombre del módulo (ej. "multimedia", "notas") es lo que
    main.py usa para llevar el registro silencioso de hábitos."""
    versiones = variantes(texto)
    # El orden de las SKILLS manda: cada skill prueba todas las versiones antes
    # de pasar a la siguiente (así "siguiente pestana" llega a pestanas y no a
    # multimedia), y siempre recibe primero el texto tal cual se escribió.
    for skill in SKILLS:
        for version in versiones:
            resultado = skill.intentar(version)
            if resultado is not None:
                return resultado, skill.__name__.rsplit(".", 1)[-1]
    return None, None
