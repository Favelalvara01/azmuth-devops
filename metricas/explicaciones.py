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
        "La más precisa: dar más peso al valor probable, sin ignorar los riesgos, la acercó a las horas reales.",
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


# ---------------------------------------------------------------------------
# Interpretaciones que se muestran debajo de cada comando
# ---------------------------------------------------------------------------
def _marca(ok):
    return {True: "✔", False: "✘", None: "—"}[ok]


def interpretar_cobertura(cov: dict, pruebas_ok=None, total_pruebas=None, warnings=0) -> list:
    """Líneas de texto para después de la tabla de cobertura de pytest."""
    total = round(cov["totals"]["percent_covered"], 2)
    archivos = {f.replace("\\", "/"): round(d["summary"]["percent_covered"], 1) for f, d in cov["files"].items()}
    bajos = sorted((p, f) for f, p in archivos.items() if p < 70)
    completos = sum(1 for p in archivos.values() if p >= 100)
    L = ["", "¿Qué significa esta tabla de cobertura?",
         "  Stmts = líneas ejecutables del archivo · Miss = líneas que ninguna prueba ejecutó · Cover = % cubierto.",
         f"  {_marca(total >= 70)} TOTAL {total} %: {explicar('Cobertura total', total >= 70)}",
         f"  ✔ {completos} de {len(archivos)} archivos tienen 100 %: cada una de sus líneas la ejecuta alguna prueba."]
    for pct, f in bajos:
        L.append(f"  ✘ {f} ({pct} %): {explicar(f, False)}")
    if not bajos:
        L.append("  ✔ Ningún archivo queda por debajo de 70 %.")
    if total_pruebas is not None:
        ok = pruebas_ok == total_pruebas
        L.append(f"  {_marca(ok)} {pruebas_ok}/{total_pruebas} pruebas aprobadas: {explicar('Pruebas aprobadas', ok)}")
    if warnings:
        L.append(f"  — {warnings} warnings: son avisos de librerías (cosas que cambiarán en versiones futuras de Python o "
                 "de una librería). NO son errores ni hacen fallar nada.")
    return L


def interpretar_metricas(m: dict) -> str:
    """Markdown con el significado de la salida de calcular_metricas.py."""
    p, pr, pj = m["producto"], m["proceso"], m["proyecto"]
    c, cov, dd = p["complejidad"], p["cobertura"]["total"], p["densidad_defectos"]
    ef, d = pr["eficacia_pruebas"], pj["desviacion"]
    filas = [
        ("Complejidad promedio", c["promedio"] <= 5, f"{c['promedio']} (meta ≤ 5)"),
        ("Complejidad máxima", c["maxima"] <= 15, f"{c['maxima']} (meta ≤ 15)"),
        ("Funciones en rango A-B", c["porcentaje_A_B"] >= 85, f"{c['porcentaje_A_B']} % (meta ≥ 85 %)"),
        ("Cobertura total", cov >= 70, f"{cov} % (meta ≥ 70 %)"),
        ("Densidad de defectos", None, f"{dd['por_kloc']} defectos/KLOC"),
        ("Defectos abiertos por KLOC", dd["abiertos_por_kloc"] < 2, f"{dd['abiertos_por_kloc']} (meta < 2)"),
        ("Índice de mantenibilidad", p["mantenibilidad_promedio"] >= 65, f"{p['mantenibilidad_promedio']} (meta ≥ 65)"),
        ("MTTD (detección)", pr["mttd_horas"] <= 48, f"{pr['mttd_dias']} días (meta ≤ 2 días)"),
        ("MTTR (reparación)", pr["mttr_horas"] < 1, f"{pr['mttr_horas']} h (meta < 1 h)"),
        ("DRE (antes de producción)", ef["dre_porcentaje"] >= 85, f"{ef['dre_porcentaje']} % (meta ≥ 85 %)"),
        ("Eficacia de la revisión", pj["eficacia_revision"]["porcentaje"] >= 20,
         f"{pj['eficacia_revision']['porcentaje']} % (meta ≥ 20 %)"),
        ("Desviación de tiempo", abs(d["desviacion_porcentaje"]) <= 20, f"{d['desviacion_porcentaje']} % (meta ≤ 20 %)"),
        ("Velocidad (Scrum)", None, f"{d['velocidad_puntos_por_sprint']} puntos/sprint"),
    ]
    L = ["", "### ¿Qué significan estos números?", ""]
    L += [f"- {_marca(ok)} **{n}** = {valor}: {explicar(n, ok)}" for n, ok, valor in filas]
    fases = pr.get("defectos_por_fase") or {}
    if fases:
        L.append(f"- — **Defectos por fase** {fases}: en qué momento se encontró cada defecto. Lo ideal es que la mayoría "
                 "salgan en revisión o pruebas, no en producción (usando el asistente).")
    modulos = [x for x in d.get("por_modulo", []) if x.get("horas_estimadas")]
    if modulos:
        mas = sorted(modulos, key=lambda x: x["desviacion_porcentaje"], reverse=True)[:2]
        dens = sorted((x for x in modulos if x.get("densidad_defectos_kloc")), key=lambda x: x["densidad_defectos_kloc"],
                      reverse=True)[:2]
        L += ["", "**Tabla de sprints:**", "",
              "- **Desv. %** = (horas reales − estimadas) / estimadas × 100. Positivo: tardó más de lo planeado; "
              "negativo: terminó antes.",
              "- **Def/KLOC** = defectos de ese módulo entre su tamaño en miles de líneas. **N/A**: el sprint no agregó "
              "código propio (DevOps o corrección de defectos).",
              f"- Los que más se desviaron fueron **{mas[0]['modulo']}** ({mas[0]['desviacion_porcentaje']} %)"
              + (f" y **{mas[1]['modulo']}** ({mas[1]['desviacion_porcentaje']} %)" if len(mas) > 1 else "")
              + ": integran hardware y servicios externos, lo más difícil de estimar."]
        if dens:
            L.append("- Los de más defectos por KLOC: " + " y ".join(
                f"**{x['modulo']}** ({x['densidad_defectos_kloc']})" for x in dens)
                + ". Coinciden con los más desviados: los defectos consumieron el tiempo extra.")
    return "\n".join(L) + "\n"


def interpretar_estimacion(r: dict) -> str:
    """Markdown con el significado de la salida de estimacion.py."""
    real = r.get("horas_reales")
    que_es = {
        "Juicio de expertos": "personas con experiencia (el alumno y la IA) estiman cada módulo y se promedia.",
        "Análoga": "se compara con un proyecto anterior parecido ya terminado y se ajusta con un factor.",
        "Tres puntos (PERT)": "para cada módulo se da un valor optimista (O), probable (M) y pesimista (P); "
                              "E = (O + 4M + P) / 6 y σ = (P − O) / 6.",
        "Puntos de función": "se mide el tamaño por las funciones que ve el usuario (entradas, salidas, consultas, "
                             "archivos) y se convierte a horas.",
    }
    L = ["", "### ¿Qué significan estas estimaciones?", ""]
    for nombre, clave in (("Juicio de expertos", "juicio_expertos"), ("Análoga", "analoga"),
                          ("Tres puntos (PERT)", "tres_puntos"), ("Puntos de función", "puntos_funcion")):
        horas = r[clave]["total_horas"]
        if real:
            error = round((horas - real) / real * 100, 1)
            ok = abs(error) <= 15
            L.append(f"- {_marca(ok)} **{nombre}** = {horas} h (error {error:+} % contra {real} h reales; meta ≤ 15 %). "
                     f"Qué es: {que_es[nombre]} {explicar(nombre, ok)}")
        else:
            L.append(f"- **{nombre}** = {horas} h. Qué es: {que_es[nombre]}")
    r1, r2 = r["tres_puntos"]["rango_95"]
    L.append(f"- **Intervalo de PERT** [{r1}, {r2}] h: con 95 % de confianza el proyecto debía durar entre esas horas "
             "(E ± 2σ).")
    L.append("- **Triangular** = (O + M + P) / 3: otra forma de promediar los tres escenarios, sin darle más peso al probable.")
    if real:
        dentro = r1 <= real <= r2
        L.append(f"- {_marca(dentro)} **Real dentro del intervalo PERT**: {explicar('Real dentro del intervalo PERT', dentro)}")
        tecnicas = {n: r[k]["total_horas"] for n, k in (("Juicio de expertos", "juicio_expertos"), ("Análoga", "analoga"),
                                                        ("Tres puntos (PERT)", "tres_puntos"),
                                                        ("Puntos de función", "puntos_funcion"))}
        mejor = min(tecnicas, key=lambda n: abs(tecnicas[n] - real))
        L.append(f"- **Conclusión:** la técnica más cercana a las {real} h reales fue **{mejor}**.")
    return "\n".join(L) + "\n"
