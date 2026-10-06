"""
calcular_metricas.py — Métricas de calidad de Azmuth (producto, proceso, proyecto).

Uso:
    pytest --cov --cov-report=json:reports/coverage.json --junitxml=reports/pruebas.xml
    python metricas/calcular_metricas.py --reportes reports

Lee:
  * el código fuente (complejidad ciclomática y líneas con radon)
  * reports/coverage.json   (cobertura generada por pytest-cov)
  * reports/pruebas.xml     (resultados de pytest en formato JUnit)
  * metricas/datos/defectos.csv  (registro de defectos)
  * metricas/datos/sprints.csv   (planeación ágil: horas estimadas vs reales)
Genera:
  * reports/metricas.json  (datos crudos, los usa analisis_ia.py)
  * reports/metricas.md    (tablas legibles; se publican en el resumen de GitHub Actions)
"""
import argparse
import csv
import json
import os
import statistics
import xml.etree.ElementTree as ET
from datetime import datetime

from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "metricas", "datos")
EXCLUIR = {"tests", "metricas", ".github", "__pycache__", ".venv", "venv", "reports"}
FORMATO_FECHA = "%Y-%m-%d %H:%M"


# ----------------------------------------------------------------- utilidades
def archivos_python():
    for carpeta, subcarpetas, archivos in os.walk(RAIZ):
        subcarpetas[:] = [d for d in subcarpetas if d not in EXCLUIR and not d.startswith(".")]
        for a in sorted(archivos):
            if a.endswith(".py"):
                ruta = os.path.join(carpeta, a)
                yield os.path.relpath(ruta, RAIZ).replace(os.sep, "/"), ruta


def leer_csv(nombre):
    with open(os.path.join(DATOS, nombre), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fecha(texto):
    return datetime.strptime(texto, FORMATO_FECHA) if texto else None


def horas(delta):
    return round(delta.total_seconds() / 3600, 2)


def r2(x):
    return round(x, 2)


# ------------------------------------------------------- métricas de producto
def metricas_producto(dir_reportes, defectos):
    funciones, lineas = [], {}
    for rel, ruta in archivos_python():
        codigo = open(ruta, encoding="utf-8").read()
        raw = analyze(codigo)
        lineas[rel] = {"loc": raw.loc, "sloc": raw.sloc, "comentarios": raw.comments + raw.multi,
                       "mi": r2(mi_visit(codigo, multi=True))}
        for bloque in cc_visit(codigo):
            elementos = [bloque] + list(getattr(bloque, "methods", []))
            for b in elementos:
                if b.__class__.__name__ == "Class":
                    continue
                funciones.append({"archivo": rel, "funcion": b.name, "linea": b.lineno,
                                  "complejidad": b.complexity, "rango": cc_rank(b.complexity)})

    valores = [f["complejidad"] for f in funciones]
    distribucion = {r: sum(1 for f in funciones if f["rango"] == r) for r in "ABCDEF"}
    sloc_total = sum(v["sloc"] for v in lineas.values())
    kloc = sloc_total / 1000

    # Cobertura (pytest-cov)
    cobertura = {"total": None, "por_archivo": {}}
    ruta_cov = os.path.join(dir_reportes, "coverage.json")
    if os.path.exists(ruta_cov):
        cov = json.load(open(ruta_cov, encoding="utf-8"))
        cobertura["total"] = r2(cov["totals"]["percent_covered"])
        cobertura["lineas_cubiertas"] = cov["totals"]["covered_lines"]
        cobertura["lineas_ejecutables"] = cov["totals"]["num_statements"]
        for archivo, datos in cov["files"].items():
            cobertura["por_archivo"][archivo.replace(os.sep, "/")] = r2(datos["summary"]["percent_covered"])

    # Densidad de defectos (defectos / KLOC)
    por_archivo = {}
    for d in defectos:
        por_archivo[d["archivo"]] = por_archivo.get(d["archivo"], 0) + 1

    return {
        "complejidad": {
            "funciones_analizadas": len(funciones),
            "promedio": r2(statistics.mean(valores)),
            "mediana": statistics.median(valores),
            "maxima": max(valores),
            "distribucion_rangos": distribucion,
            "porcentaje_A_B": r2(100 * (distribucion["A"] + distribucion["B"]) / len(funciones)),
            "top10": sorted(funciones, key=lambda f: -f["complejidad"])[:10],
        },
        "lineas": {"archivos": len(lineas), "loc": sum(v["loc"] for v in lineas.values()),
                   "sloc": sloc_total, "kloc": r2(kloc), "por_archivo": lineas},
        "cobertura": cobertura,
        "densidad_defectos": {
            "defectos_totales": len(defectos),
            "por_kloc": r2(len(defectos) / kloc),
            "abiertos": sum(1 for d in defectos if not d["fecha_reparado"]),
            "abiertos_por_kloc": r2(sum(1 for d in defectos if not d["fecha_reparado"]) / kloc),
            "por_archivo": por_archivo,
        },
        "mantenibilidad_promedio": r2(statistics.mean(v["mi"] for v in lineas.values())),
    }


# --------------------------------------------------------- métricas de proceso
def metricas_proceso(dir_reportes, defectos):
    detecciones = [horas(fecha(d["fecha_detectado"]) - fecha(d["fecha_introducido"])) for d in defectos]
    reparados = [d for d in defectos if d["fecha_reparado"]]
    reparaciones = [horas(fecha(d["fecha_reparado"]) - fecha(d["fecha_detectado"])) for d in reparados]

    graves = [d for d in defectos if d["severidad"] in ("critica", "alta")]
    fases = {f: sum(1 for d in defectos if d["fase_deteccion"] == f) for f in ("revision", "pruebas", "produccion")}
    antes_de_produccion = fases["revision"] + fases["pruebas"]

    pruebas = {}
    ruta_xml = os.path.join(dir_reportes, "pruebas.xml")
    if os.path.exists(ruta_xml):
        raiz = ET.parse(ruta_xml).getroot()
        suite = raiz if raiz.tag == "testsuite" else raiz.find("testsuite")
        total = int(suite.get("tests"))
        fallos = int(suite.get("failures")) + int(suite.get("errors"))
        omitidas = int(suite.get("skipped"))  # aquí caen los xfail (defectos conocidos)
        pruebas = {"total": total, "aprobadas": total - fallos - omitidas, "fallidas": fallos,
                   "defectos_conocidos_xfail": omitidas, "tiempo_seg": r2(float(suite.get("time")))}

    return {
        "mttd_horas": r2(statistics.mean(detecciones)),
        "mttd_dias": r2(statistics.mean(detecciones) / 24),
        "mttr_horas": r2(statistics.mean(reparaciones)) if reparaciones else None,
        "mttr_minutos": round(statistics.mean(reparaciones) * 60) if reparaciones else None,
        "defectos_reparados": len(reparados),
        "defectos_por_fase": fases,
        "eficacia_pruebas": {
            "detectados_en_pruebas": fases["pruebas"],
            "graves_detectados_en_pruebas": sum(1 for d in graves if d["fase_deteccion"] == "pruebas"),
            "graves_totales": len(graves),
            "dre_porcentaje": r2(100 * antes_de_produccion / len(defectos)),
            "porcentaje_pruebas_vs_produccion": r2(100 * fases["pruebas"] / (fases["pruebas"] + fases["produccion"])),
        },
        "ejecucion_pruebas": pruebas,
    }


# -------------------------------------------------------- métricas de proyecto
def metricas_proyecto(defectos, producto):
    fases = {f: sum(1 for d in defectos if d["fase_deteccion"] == f) for f in ("revision", "pruebas", "produccion")}
    sloc = producto["lineas"]["por_archivo"]

    modulos = []
    for s in leer_csv("sprints.csv"):
        archivos = s["archivos"].split(";")
        est, real = float(s["horas_estimadas"]), float(s["horas_reales"])
        sloc_mod = sum(v["sloc"] for k, v in sloc.items() if any(k == a or k.startswith(a + "/") for a in archivos))
        defs = sum(1 for d in defectos if d["archivo"] in archivos)
        modulos.append({
            "sprint": int(s["sprint"]), "modulo": s["modulo"], "horas_estimadas": est, "horas_reales": real,
            "desviacion_horas": r2(real - est), "desviacion_porcentaje": r2(100 * (real - est) / est),
            "puntos_historia": int(s["puntos_historia"]), "sloc": sloc_mod, "defectos": defs,
            "densidad_defectos_kloc": r2(defs / (sloc_mod / 1000)) if sloc_mod else None,
            "horas_por_punto": r2(real / int(s["puntos_historia"])),
        })
    est_total = sum(m["horas_estimadas"] for m in modulos)
    real_total = sum(m["horas_reales"] for m in modulos)
    return {
        "eficacia_revision": {
            "defectos_en_revision": fases["revision"], "defectos_totales": len(defectos),
            "porcentaje": r2(100 * fases["revision"] / len(defectos)),
        },
        "desviacion": {
            "horas_estimadas": est_total, "horas_reales": real_total,
            "desviacion_porcentaje": r2(100 * (real_total - est_total) / est_total),
            "velocidad_puntos_por_sprint": r2(statistics.mean(m["puntos_historia"] for m in modulos)),
            "por_modulo": modulos,
        },
    }


# ---------------------------------------------------------------- markdown
def a_markdown(m):
    p, pr, pj = m["producto"], m["proceso"], m["proyecto"]
    c = p["complejidad"]
    L = ["## 📊 Métricas de calidad — Azmuth", "",
         f"_Generado: {m['generado']}_", "",
         "### Métricas de producto", "",
         "| Métrica | Valor |", "|---|---|",
         f"| Complejidad ciclomática promedio | {c['promedio']} ({c['funciones_analizadas']} funciones) |",
         f"| Complejidad máxima | {c['maxima']} |",
         f"| Funciones en rango A-B (simples) | {c['porcentaje_A_B']} % |",
         f"| Cobertura de código | {p['cobertura']['total']} % |",
         f"| Tamaño | {p['lineas']['sloc']} SLOC ({p['lineas']['kloc']} KLOC) |",
         f"| Densidad de defectos | {p['densidad_defectos']['por_kloc']} defectos/KLOC |",
         f"| Defectos abiertos | {p['densidad_defectos']['abiertos']} ({p['densidad_defectos']['abiertos_por_kloc']}/KLOC) |",
         f"| Índice de mantenibilidad promedio | {p['mantenibilidad_promedio']} |", "",
         "**Funciones más complejas**", "", "| Archivo | Función | CC | Rango |", "|---|---|---|---|"]
    L += [f"| {f['archivo']} | {f['funcion']} | {f['complejidad']} | {f['rango']} |" for f in c["top10"]]
    e = pr["eficacia_pruebas"]
    L += ["", "### Métricas de proceso", "", "| Métrica | Valor |", "|---|---|",
          f"| Tiempo medio de detección (MTTD) | {pr['mttd_horas']} h ({pr['mttd_dias']} días) |",
          f"| Tiempo medio de reparación (MTTR) | {pr['mttr_horas']} h ({pr['mttr_minutos']} min) |",
          f"| Defectos detectados en pruebas | {e['detectados_en_pruebas']} |",
          f"| Eficiencia de remoción antes de producción (DRE) | {e['dre_porcentaje']} % |",
          f"| Defectos por fase | {pr['defectos_por_fase']} |"]
    if pr["ejecucion_pruebas"]:
        t = pr["ejecucion_pruebas"]
        L.append(f"| Pruebas automatizadas | {t['aprobadas']}/{t['total']} aprobadas, {t['fallidas']} fallidas, "
                 f"{t['defectos_conocidos_xfail']} defectos conocidos (xfail) |")
    r = pj["eficacia_revision"]
    d = pj["desviacion"]
    L += ["", "### Métricas de proyecto", "", "| Métrica | Valor |", "|---|---|",
          f"| Eficacia de la revisión | {r['porcentaje']} % ({r['defectos_en_revision']}/{r['defectos_totales']}) |",
          f"| Desviación total de tiempo | {d['desviacion_porcentaje']} % ({d['horas_reales']} h reales vs {d['horas_estimadas']} h) |",
          f"| Velocidad promedio | {d['velocidad_puntos_por_sprint']} puntos/sprint |", "",
          "| Sprint | Módulo | Est. (h) | Real (h) | Desv. % | SLOC | Defectos | Def/KLOC |",
          "|---|---|---|---|---|---|---|---|"]
    for x in d["por_modulo"]:
        dens = x["densidad_defectos_kloc"] if x["densidad_defectos_kloc"] is not None else "N/A"
        L.append(f"| {x['sprint']} | {x['modulo']} | {x['horas_estimadas']} | {x['horas_reales']} | "
                 f"{x['desviacion_porcentaje']} | {x['sloc']} | {x['defectos']} | {dens} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reportes", default="reports")
    args = ap.parse_args()
    os.makedirs(args.reportes, exist_ok=True)

    defectos = leer_csv("defectos.csv")
    producto = metricas_producto(args.reportes, defectos)
    resultado = {
        "generado": datetime.now().strftime(FORMATO_FECHA),
        "producto": producto,
        "proceso": metricas_proceso(args.reportes, defectos),
        "proyecto": metricas_proyecto(defectos, producto),
    }
    with open(os.path.join(args.reportes, "metricas.json"), "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    md = a_markdown(resultado)
    with open(os.path.join(args.reportes, "metricas.md"), "w", encoding="utf-8") as f:
        f.write(md)
    print(md)


if __name__ == "__main__":
    main()
