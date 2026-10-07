"""
estimacion.py — Técnicas de estimación aplicadas a Azmuth.

  1. Juicio de expertos   (promedio de varios expertos, uno de ellos la IA)
  2. Estimación análoga   (productividad de un proyecto anterior parecido)
  3. Estimación de tres puntos (PERT: (O + 4M + P) / 6, con desviación estándar)
  4. Puntos de función    (IFPUG: EI, EO, EQ, ILF, EIF + 14 factores de ajuste)

Uso:  python metricas/estimacion.py --reportes reports
Lee metricas/datos/estimacion.json (y reports/metricas.json para el tamaño real)
y genera reports/estimacion.json y reports/estimacion.md
"""
import argparse
import json
import math
import os
import statistics

from consola import mostrar  # noqa: E402  (tablas con formato en la terminal)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PESOS = {  # tabla estándar IFPUG
    "EI": {"simple": 3, "media": 4, "compleja": 6},
    "EO": {"simple": 4, "media": 5, "compleja": 7},
    "EQ": {"simple": 3, "media": 4, "compleja": 6},
    "ILF": {"simple": 7, "media": 10, "compleja": 15},
    "EIF": {"simple": 5, "media": 7, "compleja": 10},
}


def juicio_expertos(d):
    modulos, expertos = d["modulos"], d["expertos"]
    filas = []
    for i, m in enumerate(modulos):
        valores = [v[i] for v in expertos.values()]
        filas.append({"modulo": m, "valores": valores, "promedio": round(statistics.mean(valores), 2)})
    totales = {k: sum(v) for k, v in expertos.items()}
    return {"expertos": list(expertos), "por_modulo": filas, "totales_por_experto": totales,
            "total_horas": round(sum(f["promedio"] for f in filas), 2)}


def analoga(d, sloc_actual):
    productividad = d["sloc_referencia"] / d["horas_referencia"]
    horas = sloc_actual / productividad * d["factor_ajuste"]
    return {**d, "sloc_actual": sloc_actual, "productividad_sloc_por_hora": round(productividad, 2),
            "total_horas": round(horas, 2)}


def tres_puntos(d):
    filas, var_total = [], 0
    for m, v in d.items():
        o, mp, p = v["optimista"], v["probable"], v["pesimista"]
        e = (o + 4 * mp + p) / 6
        sd = (p - o) / 6
        var_total += sd ** 2
        filas.append({"modulo": m, "O": o, "M": mp, "P": p, "pert": round(e, 2),
                      "triangular": round((o + mp + p) / 3, 2), "desv_std": round(sd, 2)})
    total = sum(f["pert"] for f in filas)
    sd_total = math.sqrt(var_total)
    return {"por_modulo": filas, "total_horas": round(total, 2), "desv_std_total": round(sd_total, 2),
            "rango_95": [round(total - 2 * sd_total, 2), round(total + 2 * sd_total, 2)]}


def puntos_funcion(d):
    detalle, pfna = [], 0
    for tipo, pesos in PESOS.items():
        for nivel, peso in pesos.items():
            n = len(d[tipo][nivel])
            detalle.append({"tipo": tipo, "complejidad": nivel, "cantidad": n, "peso": peso, "subtotal": n * peso})
            pfna += n * peso
    suma_gsc = sum(d["factores_ajuste"].values())
    vaf = 0.65 + 0.01 * suma_gsc
    pfa = pfna * vaf
    return {"detalle": detalle, "pf_no_ajustados": pfna, "suma_factores": suma_gsc, "vaf": round(vaf, 2),
            "pf_ajustados": round(pfa, 2), "horas_por_pf": d["horas_por_punto_funcion"],
            "total_horas": round(pfa * d["horas_por_punto_funcion"], 2),
            "factores": d["factores_ajuste"]}


def a_markdown(r):
    je, an, tp, pf = r["juicio_expertos"], r["analoga"], r["tres_puntos"], r["puntos_funcion"]
    L = ["## ⏱️ Estimación del proyecto Azmuth", "", "### 1. Juicio de expertos", "",
         "| Módulo | " + " | ".join(je["expertos"]) + " | Promedio |", "|---" * (len(je["expertos"]) + 2) + "|"]
    L += [f"| {f['modulo']} | " + " | ".join(str(v) for v in f["valores"]) + f" | {f['promedio']} |" for f in je["por_modulo"]]
    L += ["| **Total** | " + " | ".join(str(v) for v in je["totales_por_experto"].values()) + f" | **{je['total_horas']}** |",
          "", "### 2. Estimación análoga", "",
          f"Proyecto de referencia: {an['proyecto_referencia']} — {an['sloc_referencia']} SLOC en {an['horas_referencia']} h "
          f"→ {an['productividad_sloc_por_hora']} SLOC/h. Azmuth: {an['sloc_actual']} SLOC × factor {an['factor_ajuste']} "
          f"= **{an['total_horas']} h**.", "", "### 3. Tres puntos (PERT)", "",
          "| Módulo | O | M | P | PERT | Triangular | σ |", "|---|---|---|---|---|---|---|"]
    L += [f"| {f['modulo']} | {f['O']} | {f['M']} | {f['P']} | {f['pert']} | {f['triangular']} | {f['desv_std']} |"
          for f in tp["por_modulo"]]
    L += [f"| **Total** | | | | **{tp['total_horas']}** | | {tp['desv_std_total']} |", "",
          f"Con 95 % de confianza: entre {tp['rango_95'][0]} y {tp['rango_95'][1]} horas.", "",
          "### 4. Puntos de función", "", "| Tipo | Complejidad | Cantidad | Peso | Subtotal |", "|---|---|---|---|---|"]
    L += [f"| {f['tipo']} | {f['complejidad']} | {f['cantidad']} | {f['peso']} | {f['subtotal']} |" for f in pf["detalle"] if f["cantidad"]]
    L += [f"| **PFNA** | | | | **{pf['pf_no_ajustados']}** |", "",
          f"VAF = 0.65 + 0.01 × {pf['suma_factores']} = {pf['vaf']} → PFA = {pf['pf_ajustados']} → "
          f"{pf['pf_ajustados']} × {pf['horas_por_pf']} h/PF = **{pf['total_horas']} h**.", "",
          "### Comparación", "", "| Técnica | Horas estimadas |", "|---|---|"]
    for nombre, clave in (("Juicio de expertos", "juicio_expertos"), ("Análoga", "analoga"),
                          ("Tres puntos (PERT)", "tres_puntos"), ("Puntos de función", "puntos_funcion")):
        L.append(f"| {nombre} | {r[clave]['total_horas']} |")
    if r.get("horas_reales"):
        L.append(f"| **Real (registro de sprints)** | **{r['horas_reales']}** |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reportes", default="reports")
    args = ap.parse_args()
    d = json.load(open(os.path.join(RAIZ, "metricas", "datos", "estimacion.json"), encoding="utf-8"))
    met_path = os.path.join(args.reportes, "metricas.json")
    met = json.load(open(met_path, encoding="utf-8")) if os.path.exists(met_path) else None
    sloc = met["producto"]["lineas"]["sloc"] if met else 2000
    r = {
        "juicio_expertos": juicio_expertos(d["juicio_expertos"]),
        "analoga": analoga(d["analoga"], sloc),
        "tres_puntos": tres_puntos(d["tres_puntos"]),
        "puntos_funcion": puntos_funcion(d["puntos_funcion"]),
        "horas_reales": met["proyecto"]["desviacion"]["horas_reales"] if met else None,
    }
    json.dump(r, open(os.path.join(args.reportes, "estimacion.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    md = a_markdown(r)
    open(os.path.join(args.reportes, "estimacion.md"), "w", encoding="utf-8").write(md)
    mostrar(md)


if __name__ == "__main__":
    main()
