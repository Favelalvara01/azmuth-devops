"""
explicaciones.py — El "¿por qué?" de cada métrica: qué significa que salga BIEN y,
si sale MAL, la causa y qué se hizo (o se hará) para mejorarla.

Lo usan veredicto.py y resumen.py para que la terminal no solo diga BIEN / MAL,
sino también la razón, igual que en el informe de calidad.
"""

# métrica -> (por qué está BIEN, por qué está MAL)
_TEXTOS = {
    "Hallazgos de ruff": (
        "El código no tiene errores de sintaxis, variables sin definir ni imports sin usar; pasa el gate del pipeline.",
        "ruff encontró problemas en el código y el pipeline se detendría. Se corrigen con: py -3.13 -m ruff check . --fix",
    ),
    "Pruebas aprobadas": (
        "Todas las pruebas automáticas pasan: ninguna función probada está rota.",
        "Alguna prueba falló: hay una función rota que se debe corregir antes de subir el cambio.",
    ),
    "Cobertura total": (
        "Las pruebas ejecutan más del 70 % del código (meta del informe). Lo que falta es sobre todo el arranque "
        "de la ventana y el hardware (micrófono, pantalla), que no se pueden probar sin Windows.",
        "Las pruebas ejecutan menos del 70 % del código: hay partes que podrían fallar sin que ninguna prueba lo note.",
    ),
    "Complejidad promedio": (
        "En promedio las funciones son simples (rango A): fáciles de leer, probar y modificar.",
        "En promedio las funciones son complejas: conviene dividirlas en funciones más pequeñas.",
    ),
    "Complejidad máxima": (
        "La función más compleja está dentro del límite. Antes llegaba a 27; se refactorizó con una tabla de "
        "despacho (diccionario acción → función).",
        "Hay una función demasiado compleja (muchos if/for): es difícil de probar y conviene dividirla.",
    ),
    "Funciones en rango A-B": (
        "Casi todo el código es simple (rango A-B); solo unas pocas funciones quedan en rango C.",
        "Demasiadas funciones son complejas (rango C o peor): el código es difícil de mantener.",
    ),
    "Funciones en rango D o peor": (
        "Ya no hay funciones de rango D: las dos que había en la línea base (27 y 24) se refactorizaron.",
        "Hay funciones de rango D o peor: son las primeras que se deben refactorizar.",
    ),
    "Índice de mantenibilidad": (
        "El código es fácil de mantener (≥ 65 de 100): poca complejidad y archivos de tamaño razonable.",
        "El código es difícil de mantener: archivos muy largos o muy complejos.",
    ),
    "Archivo más bajo": (
        "Incluso el archivo más difícil de mantener sigue en rango A.",
        "Hay un archivo difícil de mantener: conviene dividirlo o simplificarlo.",
    ),
    "Archivos fuera del rango A": (
        "Todos los archivos están en rango A (mantenibles).",
        "Hay archivos fuera del rango A: son los primeros que conviene simplificar.",
    ),
    "Densidad de defectos": (
        "Es informativa: cuenta TODOS los defectos registrados (ya corregidos) entre el tamaño del código.",
        "",
    ),
    "Defectos abiertos por KLOC": (
        "Todos los defectos registrados ya se corrigieron: no queda ninguno abierto.",
        "Quedan defectos sin corregir: se deben cerrar en el siguiente sprint.",
    ),
    "MTTD (detección)": (
        "Los defectos se detectan rápido después de introducirse.",
        "Antes del pipeline los defectos se descubrían usando el asistente, días después de introducirse. Es "
        "historia del proyecto: ahora las pruebas de cada push los detectan antes y el monitoreo (errores.log, "
        "/salud) avisa de las fallas.",
    ),
    "MTTR (reparación)": (
        "Los defectos se reparan en menos de 1 hora.",
        "Los defectos se repararon el mismo día, pero varios dependían de servicios externos (Ngrok, la API de "
        "Claude, librerías de Python) y tardaron más de 1 hora.",
    ),
    "DRE (antes de producción)": (
        "La mayoría de los defectos se atrapan antes de llegar al usuario.",
        "La mayoría de los defectos se encontraron usando el asistente (producción), porque las pruebas "
        "automáticas llegaron hasta el Sprint 7. Los defectos nuevos ya se atrapan en el pipeline, así que "
        "este porcentaje irá subiendo.",
    ),
    "Eficacia de las pruebas": (
        "Las pruebas atrapan más defectos que los que se escapan a producción.",
        "Las pruebas atraparon menos defectos que los encontrados en uso real: la mayoría eran de antes de que "
        "existieran las pruebas automáticas.",
    ),
    "Eficacia de la revisión": (
        "Una buena parte de los defectos se atrapa al revisar el código antes de probarlo.",
        "Pocos defectos se encontraron revisando el código antes de probarlo. Por eso ruff se convirtió en un "
        "gate obligatorio del pipeline.",
    ),
    "Desviación de tiempo": (
        "El proyecto tardó un poco más de lo estimado, pero dentro del margen de 20 %. Lo que más se desvió "
        "fueron la voz y la interfaz, porque dependen de hardware y servicios externos.",
        "El proyecto tardó mucho más de lo estimado: la estimación de los siguientes sprints debe ajustarse.",
    ),
    "Velocidad (Scrum)": (
        "Es informativa: puntos de historia terminados por sprint; sirve para planear cuánto cabe en el siguiente.",
        "",
    ),
    "Juicio de expertos": (
        "Error menor al 15 %: el alumno y la IA conocían bien cada módulo.",
        "Los expertos se equivocaron más del 15 %: subestimaron la integración con hardware y servicios externos.",
    ),
    "Análoga": (
        "Error menor al 15 %: el proyecto de referencia era parecido.",
        "Se comparó con Easy Learning (un CRUD en C#), mucho más sencillo que un asistente con voz, IA y APIs; "
        "por eso sobreestimó.",
    ),
    "Tres puntos (PERT)": (
        "La más precisa: combina un escenario optimista, uno probable y uno pesimista, E = (O + 4M + P) / 6.",
        "Error mayor al 15 %: los tres escenarios no reflejaron bien el riesgo.",
    ),
    "Puntos de función": (
        "Error menor al 15 %: el tamaño funcional reflejó bien el esfuerzo.",
        "Mide el tamaño por las funciones para el usuario, pero no considera que la IA ayudó a programar más "
        "rápido; por eso sobreestimó.",
    ),
    "Real dentro del intervalo PERT": (
        "Las horas reales cayeron dentro del intervalo de confianza del 95 % de PERT: la estimación fue confiable.",
        "Las horas reales quedaron fuera del intervalo de PERT: hubo imprevistos que no se consideraron.",
    ),
}
_SINONIMOS = {"Cobertura de código": "Cobertura total", "Promedio": "Índice de mantenibilidad"}

_APP_DESKTOP = ("Solo abre la ventana (PyWebView) y arranca la voz y el servidor; necesita pantalla y Windows "
                "reales, por eso no se prueba con pytest. Se valida con la prueba de humo del .exe (/salud) en el "
                "workflow de Release.")


def explicar(metrica: str, cumple):
    """Texto del "¿por qué?" de una métrica, o None si no hay nada que explicar."""
    nombre = metrica.strip()
    if nombre.endswith(".py"):  # archivo con cobertura baja (veredicto de pruebas)
        if nombre.endswith("app_desktop.py"):
            return _APP_DESKTOP
        return "Este archivo tiene poca cobertura: conviene agregarle pruebas." if cumple is False else None
    textos = _TEXTOS.get(_SINONIMOS.get(nombre, nombre))
    if not textos:
        return None
    bien, mal = textos
    if cumple is None:
        return bien or None
    return (bien if cumple else mal) or None
