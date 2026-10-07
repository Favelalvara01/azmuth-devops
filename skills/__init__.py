"""
Registro central de skills.
Cada skill es un módulo con una función intentar(texto) que regresa
un texto de respuesta si supo manejar el comando, o None si no le tocaba.

IMPORTANTE sobre el orden de SKILLS: se revisan de arriba a abajo, y la
primera que conteste algo (no None) gana. "aplicaciones" tiene un patrón
muy amplio que agarra cualquier "abre X" o "cierra X", así que SIEMPRE
debe ir al final — si no, se roba comandos que le tocan a otras skills
más específicas (como "abre pestaña" o "cierra pestaña").

Para agregar una skill nueva:
1. Crea un archivo nuevo aquí en skills/, por ejemplo skills/musica.py
2. Dale una función intentar(texto: str) -> str | None igual que las demás
3. Impórtala abajo y agrégala a la lista SKILLS — si usa frases como
    "abre X" o "cierra X", ponla ANTES de aplicaciones en la lista.
Ese es todo el contrato — no hay que tocar nada más del programa.
"""
from . import modos, tiempo, notas, recordatorios, memoria, contactos, habitos, web, sistema, multimedia, pestanas, ayuda, aplicaciones

SKILLS = [modos, sistema, tiempo, notas, recordatorios, memoria, contactos, habitos, web, multimedia, pestanas, ayuda, aplicaciones]


def procesar(texto: str):
    """Prueba cada skill en orden; regresa (respuesta, nombre_skill) de la
    primera que conteste algo (no None), o (None, None) si ninguna supo
    manejarlo. El nombre del módulo (ej. "multimedia", "notas") es lo que
    main.py usa para llevar el registro silencioso de hábitos."""
    for skill in SKILLS:
        resultado = skill.intentar(texto)
        if resultado is not None:
            return resultado, skill.__name__.rsplit(".", 1)[-1]
    return None, None