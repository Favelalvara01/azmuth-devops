"""
resumen.py — Tabla final en la terminal: cada métrica con su valor, la meta
del informe de calidad y si cumple (✔) o no (✘).

Uso (después de calcular_metricas.py y estimacion.py):
    py -3.13 metricas/resumen.py --reportes reports
"""
import argparse
import json
import os

try:
    from consola import mostrar
except ImportError:  # pragma: no cover
    from metricas.consola import mostrar


def _leer(ruta):
    return json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else None


def indicadores(m, e=None):
    """Lista de (grupo, métrica, valor, meta, cumple)."""
    p, pr, pj = m["producto"], m["proceso"], m["proyecto"]
    c, cov, dd = p["complejidad"], p["cobertura"], p["densidad_defectos"]
    ex, ef, dv = pr["ejecucion_pruebas"], pr["eficacia_pruebas"], pj["desviacion"]
    filas = [
        ("Producto", "Pruebas aprobadas", f"{ex['aprobadas']}/{ex['total']}", "100 %", ex["fallidas"] == 0),
        ("Producto", "Cobertura de código", f"{cov['total']} %", "≥ 70 %", cov["total"] >= 70),
        ("Producto", "Complejidad promedio", f"{c['promedio']}", "≤ 5 (rango A)", c["promedio"] <= 5),
        ("Producto", "Complejidad máxima", f"{c['maxima']}", "≤ 15", c["maxima"] <= 15),
        ("Producto", "Funciones en rango A-B", f"{c['porcentaje_A_B']} %", "≥ 85 %", c["porcentaje_A_B"] >= 85),
        ("Producto", "Índice de mantenibilidad", f"{p['mantenibilidad_promedio']}", "≥ 65", p["mantenibilidad_promedio"] >= 65),
        ("Producto", "Densidad de defectos", f"{dd['por_kloc']} /KLOC", "(informativa)", None),
        ("Producto", "Defectos abiertos por KLOC", f"{dd['abiertos_por_kloc']}", "< 2", dd["abiertos_por_kloc"] < 2),
        ("Proceso", "MTTD (detección)", f"{pr['mttd_horas']} h ({pr['mttd_dias']} días)", "≤ 48 h", pr["mttd_horas"] <= 48),
        ("Proceso", "MTTR (reparación)", f"{pr['mttr_horas']} h", "< 1 h", pr["mttr_horas"] < 1),
        ("Proceso", "DRE (antes de producción)", f"{ef['dre_porcentaje']} %", "≥ 85 %", ef["dre_porcentaje"] >= 85),
        ("Proceso", "Eficacia de las pruebas", f"{ef['porcentaje_pruebas_vs_produccion']} %", "≥ 50 %",
         ef["porcentaje_pruebas_vs_produccion"] >= 50),
        ("Proyecto", "Eficacia de la revisión", f"{pj['eficacia_revision']['porcentaje']} %", "≥ 20 %",
         pj["eficacia_revision"]["porcentaje"] >= 20),
        ("Proyecto", "Desviación de tiempo", f"{dv['desviacion_porcentaje']} % ({dv['horas_reales']} h vs {dv['horas_estimadas']} h)",
         "≤ 20 %", abs(dv["desviacion_porcentaje"]) <= 20),
        ("Proyecto", "Velocidad (Scrum)", f"{dv['velocidad_puntos_por_sprint']} puntos/sprint", "(informativa)", None),
    ]
    if e and e.get("horas_reales"):
        r1, r2 = e["tres_puntos"]["rango_95"]
        filas.append(("Estimación", "Real dentro del intervalo PERT", f"{e['horas_reales']} h en [{r1}, {r2}]",
                      "dentro", r1 <= e["horas_reales"] <= r2))
    return filas


def tabla_markdown(filas):
    marca = {True: "✔ Cumple", False: "✘ No cumple", None: "—"}
    md = ["## ✅ Resumen: ¿están bien las métricas?", "",
          "| Tipo | Métrica | Valor | Meta | Estado |", "|---|---|---|---|---|"]
    md += [f"| {g} | {n} | {v} | {meta} | {marca[ok]} |" for g, n, v, meta, ok in filas]
    evaluadas = [ok for *_, ok in filas if ok is not None]
    md += ["", f"**Cumple {sum(evaluadas)} de {len(evaluadas)} metas.** "
           "Las que dicen «No cumple» son las prioridades del plan de mejora."]
    return "\n".join(md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reportes", default="reports")
    args = ap.parse_args()
    m = _leer(os.path.join(args.reportes, "metricas.json"))
    if not m:
        print("Primero corre: py -3.13 metricas/calcular_metricas.py --reportes", args.reportes)
        return
    e = _leer(os.path.join(args.reportes, "estimacion.json"))
    mostrar(tabla_markdown(indicadores(m, e)))


if __name__ == "__main__":
    main()
