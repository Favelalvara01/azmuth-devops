"""
Skill: comandos sobre el propio JARVIS.
"""
import re


def intentar(texto: str):
    t = texto.lower().strip()

    if re.match(r"^(borra|borrar|limpia|limpiar)( el)? historial", t):
        import cerebro
        cerebro.borrar_historial()
        return "Historial de conversación reiniciado."

    return None
