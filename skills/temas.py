"""
Skill: temas — cambia la temática de Azmuth (colores, animaciones, saludo y sonido).

"temática de Halloween", "pon el modo Navidad", "tema Día de Muertos", "temática normal",
"temática automática" (según la fecha), "quita la temática", "qué temáticas tienes".
En inglés: "Halloween theme", "Christmas mode", "normal theme", "what themes do you have".
"""
import re
import threading

import idioma
import tematicas

_CLAVES = (
    ("halloween", r"h?[ae]?ll?o[uw]+[ei]+n|jalo[uw]?[ie]n"),
    ("muertos", r"(?:el\s+)?d[ií]a\s+de\s+(?:los\s+)?muertos|muertos|day\s+of\s+the\s+dead|dead"),
    ("navidad", r"navidad|navide[ñn][ao]|christmas|xmas|fiestas"),
    ("normal", r"normal|omnitrix|original|cl[aá]sic[ao]|por\s+defecto|default|verde"),
    ("auto", r"autom[aá]tic[ao]|auto|seg[uú]n\s+la\s+fecha|automatic"),
)
_LLAVE = "|".join(f"(?P<{n}>{p})" for n, p in _CLAVES)
_VERBO = (r"(?:(?:pon(?:me|le)?|cambia(?:r)?(?:\s+a)?|activa(?:r)?|usa(?:r)?|quiero|set|switch(?:\s+to)?|use|"
          r"enable|turn\s+on|change(?:\s+to)?)\s+)?(?:(?:a|al|la|el|una|un|the|to)\s+)?")
_TIPO = r"(?:tem[aá]tica|tema|modo|decoraci[oó]n|estilo|theme|mode|look)"
_ES = re.compile(rf"^{_VERBO}{_TIPO}\s+(?:de\s+(?:la\s+|los\s+)?|del\s+)?(?:{_LLAVE})$")
_EN = re.compile(rf"^{_VERBO}(?:{_LLAVE})\s+{_TIPO}$")
_QUITAR = re.compile(rf"^(?:quita(?:r)?|desactiva(?:r)?|sin|remove|turn\s+off)\s+(?:la\s+|el\s+|the\s+)?{_TIPO}$")
_LISTA = re.compile(r"^(?:qu[eé]|cu[aá]les?)\s+(?:son\s+(?:las\s+|tus\s+)?)?(?:tem[aá]ticas|temas)\s*(?:hay|tienes|tiene)?$"
                    r"|^(?:tus|mis|las)\s+tem[aá]ticas$|^(?:what|which)\s+themes(?:\s+do\s+you\s+have)?$")

_RESPUESTAS = {
    "halloween": ("¡Temática de Halloween activada! Que comience la noche más tenebrosa.",
                  "Halloween theme on! Let the spookiest night begin."),
    "muertos": ("¡Temática de Día de Muertos activada! Ya puse el cempasúchil y el papel picado.",
                "Day of the Dead theme on! Marigolds and papel picado are up."),
    "navidad": ("¡Temática navideña activada! Ya prendí las luces y empezó a nevar.",
                "Holiday theme on! The lights are on and it's snowing."),
    "normal": ("Listo, regresé a mi temática normal de Omnitrix.", "Done, I'm back to my normal Omnitrix theme."),
}


def _limpio(texto: str) -> str:
    t = re.sub(r"[¿?¡!.,]", "", (texto or "").lower()).strip()
    return re.sub(r"^(?:(?:hey|ok|oye)\s+)?(?:azmuth\s+)?(?:please\s+|por\s+favor\s+)?", "", t).strip()


def _sonar():
    threading.Thread(target=tematicas.reproducir_sonido, daemon=True).start()


def _descripcion_actual() -> str:
    actual = tematicas.nombre_visible()
    if tematicas.preferencia() == "auto":
        return idioma.t(f"Ahora está {actual}, puesta automáticamente según la fecha.",
                        f"Right now it's {actual}, set automatically by date.")
    return idioma.t(f"Ahora está {actual}, elegida por usted.", f"Right now it's {actual}, chosen by you.")


def intentar(texto: str):
    t = _limpio(texto)
    if _LISTA.match(t):
        return idioma.t("Tengo estas temáticas: normal, Halloween, Día de Muertos y Navidad. ",
                        "I have these themes: normal, Halloween, Day of the Dead and Christmas. ") + \
            _descripcion_actual() + idioma.t(" Diga, por ejemplo, «temática de Navidad» o «temática automática».",
                                             " Say, for example, \"Christmas theme\" or \"automatic theme\".")
    if _QUITAR.match(t):
        elegido = "normal"
    else:
        m = _ES.match(t) or _EN.match(t)
        if not m:
            return None
        elegido = next(n for n, _ in _CLAVES if m.group(n))
    tematicas.cambiar(elegido)
    if elegido == "auto":
        _sonar()
        return idioma.t("Listo, la temática cambiará sola según la fecha. ",
                        "Done, the theme will change by itself with the date. ") + _descripcion_actual()
    _sonar()
    return idioma.t(*_RESPUESTAS[elegido])
