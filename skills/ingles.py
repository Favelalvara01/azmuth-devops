"""
Capa de inglés: convierte los comandos principales dichos o escritos en
inglés al comando equivalente en español, para reutilizar las mismas skills
(no se duplica la lógica). Solo se usa cuando el idioma activo es inglés.

Ej.: "open Discord" -> "abre Discord", "volume to 40" -> "volumen a 40",
"remind me to study at 7 pm" -> "recuérdame study a las 7 pm".
El ORDEN importa: lo específico ("new tab") va antes que lo general ("open X").
"""
import re

_CORTESIA = re.compile(r"^(?:(?:hey|ok|okay)\s+)?(?:azmuth[,]?\s+)?(?:(?:can|could|would)\s+you\s+)?(?:please\s+)?", re.I)

_REGLAS = [
    # Pestañas y ventanas
    (r"^(?:open\s+(?:a\s+)?)?new\s+tab$", "nueva pestaña"),
    (r"^close\s+(?:this\s+|the\s+)?tab$", "cierra pestaña"),
    (r"^(?:next|switch)\s+tab$", "siguiente pestaña"),
    (r"^(?:previous|last)\s+tab$", "pestaña anterior"),
    (r"^(?:go\s+to\s+)?tab\s+(?:number\s+)?(\d+)$", r"pestaña \1"),
    (r"^(?:switch|change)\s+(?:the\s+)?window$", "cambia de ventana"),
    # Modos
    (r"^(?:switch\s+to\s+|go\s+to\s+|enable\s+)?(?:desktop|chat|text)\s+mode$", "modo escritorio"),
    (r"^(?:switch\s+to\s+|go\s+to\s+|enable\s+)?voice\s+mode$", "modo voz"),
    # Música y volumen
    (r"^(?:play|put\s+on)\s+my\s+(?:playlist|music|mix)$", "pon mi playlist"),
    (r"^(?:set\s+(?:the\s+)?)?volume\s+(?:to\s+|at\s+)?(\d+)(?:\s*%|\s+percent)?$", r"volumen a \1"),
    (r"^(?:turn\s+(?:the\s+)?volume\s+up|volume\s+up|louder|turn\s+it\s+up)$", "sube el volumen"),
    (r"^(?:turn\s+(?:the\s+)?volume\s+down|volume\s+down|quieter|lower\s+(?:the\s+)?volume|turn\s+it\s+down)$",
     "baja el volumen"),
    (r"^(?:mute|silence|unmute)(?:\s+.*)?$", "silencia"),
    (r"^(?:pause|resume|play|stop)(?:\s+(?:the\s+)?(?:music|song|video))?$", "pausa"),
    (r"^(?:next|skip)(?:\s+(?:song|track|video))?$", "siguiente"),
    (r"^(?:previous|go\s+back)(?:\s+(?:song|track|video))?$", "anterior"),
    # Notas
    (r"^(?:take|make|write(?:\s+down)?)\s+(?:a\s+)?note(?:\s+that)?[:\s]+(.+)$", r"toma nota: \1"),
    (r"^(?:(?:show|read)\s+(?:me\s+)?)?my\s+notes$", "mis notas"),
    # Recordatorios
    (r"^remind\s+me\s+to\s+(.+?)\s+every\s+day\s+at\s+(.+)$", r"recuérdame \1 todos los días a las \2"),
    (r"^remind\s+me\s+to\s+(.+?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?)$", r"recuérdame \1 a las \2"),
    (r"^remind\s+me\s+to\s+(.+)$", r"recuérdame \1"),
    (r"^(?:(?:show|read)\s+(?:me\s+)?)?my\s+reminders$", "mis recordatorios"),
    # Memoria
    (r"^remember\s+that\s+(.+)$", r"recuerda que \1"),
    (r"^what\s+do\s+you\s+(?:know|remember)(?:\s+about\s+me)?$", "qué sabes"),
    # Hora, fecha y clima
    (r"^(?:what\s+time\s+is\s+it|what'?s\s+the\s+time|tell\s+me\s+the\s+time)$", "qué hora es"),
    (r"^(?:what'?s|what\s+is)\s+(?:the\s+|today'?s\s+)?date(?:\s+today)?$|^what\s+day\s+is\s+(?:it|today)$", "qué fecha es"),
    (r"^(?:what'?s|what\s+is|how'?s|how\s+is)\s+the\s+weather(?:\s+(?:like|today))*$|^weather$", "qué clima hace"),
    (r"^(?:will|is)\s+it\s+(?:going\s+to\s+)?rain\s+tomorrow$", "va a llover mañana"),
    (r"^(?:will|is)\s+it\s+(?:going\s+to\s+)?rain(?:\s+today)?$", "va a llover hoy"),
    (r"^(?:do\s+i\s+need|should\s+i\s+(?:take|bring))\s+an?\s+umbrella(?:\s+today)?$", "necesito paraguas"),
    (r"^(?:what'?s|what\s+is)\s+the\s+(?:weather\s+)?forecast\s+(?:for\s+)?tomorrow$"
     r"|^how\s+will\s+(?:the\s+)?(?:day|weather)\s+be\s+tomorrow$", "cómo estará el día mañana"),
    (r"^(?:what'?s|what\s+is)\s+the\s+(?:weather\s+)?forecast(?:\s+for\s+today|\s+today)?$"
     r"|^how\s+will\s+(?:the\s+)?(?:day|weather)\s+be(?:\s+today)?$", "cómo estará el día hoy"),
    (r"^what\s+should\s+i\s+(?:wear|bring|take)(?:\s+today)?$", "qué me recomiendas llevar hoy"),
    # Hábitos, ayuda, sistema
    (r"^my\s+habits$", "mis hábitos"),
    (r"^(?:help|commands|what\s+can\s+you\s+do|show\s+(?:me\s+)?(?:your\s+)?commands)$", "ayuda"),
    (r"^(?:clear|delete)\s+(?:the\s+|my\s+)?(?:chat\s+)?history$", "borra el historial"),
    # Búsquedas y aplicaciones (lo más general, al final)
    (r"^(?:search|google|look\s+up)(?:\s+for)?\s+(.+)$", r"busca \1"),
    (r"^(?:open|launch|start|run)\s+(.+)$", r"abre \1"),
    (r"^(?:close|quit|kill|exit)\s+(.+)$", r"cierra \1"),
]
_COMPILADAS = [(re.compile(p, re.IGNORECASE), r) for p, r in _REGLAS]


def a_espanol(texto: str):
    """Devuelve el comando equivalente en español, o None si no es un comando conocido."""
    t = _CORTESIA.sub("", (texto or "").strip()).strip()
    t = t.rstrip("?!. ").strip()
    for patron, reemplazo in _COMPILADAS:
        m = patron.match(t)
        if m:
            return m.expand(reemplazo).strip()
    return None
