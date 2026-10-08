"""
veredicto.py — Después de cada comando de métricas dice si el resultado está
BIEN (✔) o MAL (✘) comparándolo con la meta del informe de calidad.

Uso:  py -3.13 metricas/veredicto.py <ruff|pruebas|complejidad|mantenibilidad|metricas|estimacion|todo>
"""
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(RAIZ, "reports")
EXCLUIR = "tests/*,metricas/*"


def _leer(nombre):
    ruta = os.path.join(REP, nombre)
    return json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else None


def _cmd(*args):
    r = subprocess.run([sys.executable, "-m", *args], cwd=RAIZ, capture_output=True, text=True)
    return r.stdout


def _tabla(titulo, filas, nota=""):
    """filas: (métrica, valor, meta, cumple: True/False/None)."""
    estado = {True: "[green]✔ BIEN[/]", False: "[red]✘ MAL[/]", None: "[dim]— info[/]"}
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:  # sin rich: texto simple
        print(f"\n== {titulo} ==")
        for m, v, meta, ok in filas:
            print(f"  {m}: {v}  (meta {meta})  -> {'BIEN' if ok else 'MAL' if ok is False else 'info'}")
        if nota:
            print("  " + nota)
        return
    t = Table(title=f"Veredicto: {titulo}", title_justify="left", header_style="bold")
    for col in ("Métrica", "Valor", "Meta", "Estado"):
        t.add_column(col)
    for m, v, meta, ok in filas:
        t.add_row(m, str(v), meta, estado[ok])
    c = Console()
    c.print(t)
    evaluadas = [ok for *_, ok in filas if ok is not None]
    if evaluadas:
        color = "green" if all(evaluadas) else "yellow"
        c.print(f"[{color}]Cumple {sum(evaluadas)} de {len(evaluadas)}.[/] {nota}")
    elif nota:
        c.print(nota)


def ruff():
    salida = _cmd("ruff", "check", ".", "--exit-zero", "--output-format=concise")
    n = sum(1 for linea in salida.splitlines() if linea.count(":") >= 3)
    _tabla("análisis estático (ruff)", [("Hallazgos de ruff", n, "0", n == 0)],
           "Sin hallazgos el código pasa el gate del pipeline." if n == 0 else "Corrige los hallazgos (ruff check . --fix arregla varios).")


def pruebas():
    cov = _leer("coverage.json")
    filas = []
    ruta = os.path.join(REP, "pruebas.xml")
    if os.path.exists(ruta):
        raiz = ET.parse(ruta).getroot()
        s = raiz if raiz.tag == "testsuite" else raiz.find("testsuite")
        total, fallas = int(s.get("tests", 0)), int(s.get("failures", 0)) + int(s.get("errors", 0))
        filas.append(("Pruebas aprobadas", f"{total - fallas}/{total}", "todas", fallas == 0))
    if not cov:
        print("Primero corre pytest con --cov-report=json:reports/coverage.json")
        return
    total = round(cov["totals"]["percent_covered"], 2)
    filas.append(("Cobertura total", f"{total} %", "≥ 70 %", total >= 70))
    bajos = sorted((round(d["summary"]["percent_covered"], 1), f) for f, d in cov["files"].items()
                   if d["summary"]["percent_covered"] < 70)
    for pct, f in bajos:
        filas.append((f"  {f}", f"{pct} %", "≥ 70 %", False))
    _tabla("pruebas y cobertura", filas,
           "Los archivos en ✘ son los que conviene probar más." if bajos else "Todos los archivos superan el 70 %.")


def complejidad():
    m = _leer("metricas.json")
    if m:  # mismos números que el informe (calcular_metricas.py)
        c = m["producto"]["complejidad"]
        top = c["top10"][0] if c.get("top10") else {"funcion": "-", "complejidad": c["maxima"]}
        d_o_peor = sum(c["distribucion_rangos"].get(r, 0) for r in "DEF")
        _tabla("complejidad ciclomática", [
            ("Funciones analizadas", c["funciones_analizadas"], "—", None),
            ("Complejidad promedio", c["promedio"], "≤ 5 (rango A)", c["promedio"] <= 5),
            ("Complejidad máxima", f"{c['maxima']} ({top.get('funcion', '-')})", "≤ 15", c["maxima"] <= 15),
            ("Funciones en rango A-B", f"{c['porcentaje_A_B']} %", "≥ 85 %", c["porcentaje_A_B"] >= 85),
            ("Funciones en rango D o peor", d_o_peor, "0", d_o_peor == 0),
        ], "Rangos: A 1-5 simple · B 6-10 · C 11-15 · D 16-25 refactorizar · E/F muy compleja.")
        return
    datos = _leer("complejidad.json")
    if datos is None:
        datos = json.loads(_cmd("radon", "cc", ".", "-j", "-e", EXCLUIR) or "{}")
    bloques = [b for lista in datos.values() if isinstance(lista, list) for b in lista]
    funcs = [b for b in bloques if b.get("type") in ("function", "method")]
    ccs = [b["complexity"] for b in funcs] or [0]
    prom = round(sum(ccs) / len(ccs), 2)
    peor = max(funcs, key=lambda b: b["complexity"]) if funcs else {"name": "-", "complexity": 0}
    ab = round(sum(1 for c in ccs if c <= 10) / len(ccs) * 100, 2)
    d_o_peor = sum(1 for c in ccs if c > 20)
    _tabla("complejidad ciclomática", [
        ("Funciones analizadas", len(funcs), "—", None),
        ("Complejidad promedio", prom, "≤ 5 (rango A)", prom <= 5),
        ("Complejidad máxima", f"{peor['complexity']} ({peor['name']})", "≤ 15", peor["complexity"] <= 15),
        ("Funciones en rango A-B", f"{ab} %", "≥ 85 %", ab >= 85),
        ("Funciones en rango D o peor", d_o_peor, "0", d_o_peor == 0),
    ], "Rangos: A 1-5 simple · B 6-10 · C 11-15 · D 16-25 refactorizar · E/F muy compleja.")


def mantenibilidad():
    datos = json.loads(_cmd("radon", "mi", ".", "-j", "-e", EXCLUIR) or "{}")
    mis = {f: round(v["mi"], 2) for f, v in datos.items() if isinstance(v, dict) and "mi" in v}
    if not mis:
        print("No se pudo calcular el índice de mantenibilidad.")
        return
    prom = round(sum(mis.values()) / len(mis), 2)
    peor = min(mis, key=mis.get)
    no_a = [f for f, v in mis.items() if v <= 19]
    _tabla("índice de mantenibilidad", [
        ("Archivos analizados", len(mis), "—", None),
        ("Promedio", prom, "≥ 65", prom >= 65),
        ("Archivo más bajo", f"{mis[peor]} ({peor})", "> 19 (rango A)", mis[peor] > 19),
        ("Archivos fuera del rango A", len(no_a), "0", not no_a),
    ], "Escala: A > 19 fácil de mantener · B 10-19 · C < 10 difícil.")


def metricas():
    m = _leer("metricas.json")
    if not m:
        print("Primero corre: py -3.13 metricas/calcular_metricas.py --reportes reports")
        return
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from resumen import indicadores
    filas = [(n, v, meta, ok) for g, n, v, meta, ok in indicadores(m) if g != "Producto"]
    _tabla("métricas de proceso y proyecto", filas,
           "Las que salen en ✘ son las prioridades del plan de mejora (sección 9.1 del informe).")


def estimacion():
    e = _leer("estimacion.json")
    if not e or not e.get("horas_reales"):
        print("Primero corre: py -3.13 metricas/estimacion.py --reportes reports")
        return
    real = e["horas_reales"]
    tecnicas = [("Juicio de expertos", e["juicio_expertos"]["total_horas"]), ("Análoga", e["analoga"]["total_horas"]),
                ("Tres puntos (PERT)", e["tres_puntos"]["total_horas"]), ("Puntos de función", e["puntos_funcion"]["total_horas"])]
    filas = [(n, f"{h} h (error {round((h - real) / real * 100, 1)} %)", "error ≤ 15 %", abs(h - real) / real <= 0.15)
             for n, h in tecnicas]
    r1, r2 = e["tres_puntos"]["rango_95"]
    filas.append(("Real dentro del intervalo PERT", f"{real} h en [{r1}, {r2}]", "dentro", r1 <= real <= r2))
    mejor = min(tecnicas, key=lambda t: abs(t[1] - real))[0]
    _tabla("técnicas de estimación", filas, f"La técnica más cercana a las {real} h reales fue: {mejor}.")


ACCIONES = {"ruff": ruff, "pruebas": pruebas, "complejidad": complejidad, "mantenibilidad": mantenibilidad,
            "metricas": metricas, "estimacion": estimacion}

if __name__ == "__main__":
    pedido = sys.argv[1] if len(sys.argv) > 1 else "todo"
    for nombre, funcion in ACCIONES.items():
        if pedido in (nombre, "todo"):
            funcion()
