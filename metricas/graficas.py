"""
graficas.py — Genera las gráficas de calidad de Azmuth a partir de los resultados.

Uso:  python metricas/graficas.py --reportes reports --salida metricas/resultados/graficas
Lee reports/metricas.json, reports/estimacion.json, metricas/datos/defectos.csv
y metricas/resultados/historial.csv, y guarda una imagen PNG por gráfica.
El pipeline la ejecuta en cada push, así que las gráficas se actualizan solas
cada vez que cambia el código.
"""
import argparse
import csv
import json
import os

import matplotlib

matplotlib.use("Agg")  # sin pantalla (servidor de GitHub Actions)
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZUL, NARANJA = "#2a78d6", "#eb6834"
TEXTO, SECUNDARIO, REJILLA = "#0b0b0b", "#52514e", "#e6e5e0"
plt.rcParams.update({
    "font.size": 10, "axes.edgecolor": "#b8b7b0", "axes.labelcolor": SECUNDARIO,
    "xtick.color": SECUNDARIO, "ytick.color": SECUNDARIO, "axes.spines.top": False,
    "axes.spines.right": False, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.titlecolor": TEXTO, "axes.titlelocation": "left", "figure.dpi": 150,
})


def guardar(fig, ax, ruta, rejilla="y"):
    for a in (ax if isinstance(ax, (list, tuple)) else [ax]):
        a.grid(axis=rejilla, color=REJILLA, linewidth=0.8)
        a.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    print("  ✓", os.path.relpath(ruta, RAIZ))


def etiquetas(ax, barras, fmt="{:g}", dentro=False):
    for b in barras:
        v = b.get_height()
        y = v / 2 if dentro else v
        ax.text(b.get_x() + b.get_width() / 2, y, fmt.format(v), ha="center",
                va="center" if dentro else "bottom", fontsize=8.5,
                color="white" if dentro else TEXTO, fontweight="bold" if dentro else "normal")


def complejidad(m, salida):
    d = m["producto"]["complejidad"]["distribucion_rangos"]
    fig, ax = plt.subplots(figsize=(7, 3.4))
    b = ax.bar(["A\n1-5", "B\n6-10", "C\n11-15", "D\n16-25", "E\n26-40", "F\n>40"], [d[k] for k in "ABCDEF"], color=AZUL, width=0.6)
    etiquetas(ax, b)
    ax.set_title(f"Funciones por rango de complejidad ciclomática ({m['producto']['complejidad']['funciones_analizadas']} funciones)")
    ax.set_ylabel("Número de funciones")
    guardar(fig, ax, os.path.join(salida, "01_complejidad_rangos.png"))


def top_complejidad(m, salida):
    top = m["producto"]["complejidad"]["top10"][::-1]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.barh([f"{t['archivo'].replace('skills/', '')} · {t['funcion']}" for t in top], [t["complejidad"] for t in top],
            color=[NARANJA if t["complejidad"] > 15 else AZUL for t in top], height=0.6)
    ax.axvline(10, color=SECUNDARIO, linestyle="--", linewidth=1)
    for i, t in enumerate(top):
        ax.text(t["complejidad"] + 0.3, i, str(t["complejidad"]), va="center", fontsize=8)
    ax.set_title("Las 10 funciones más complejas (naranja = rango D o peor)")
    ax.set_xlabel("Complejidad ciclomática (línea punteada = límite recomendado 10)")
    guardar(fig, ax, os.path.join(salida, "02_funciones_mas_complejas.png"), "x")


def cobertura(m, salida):
    c = m["producto"]["cobertura"]
    datos = sorted(c["por_archivo"].items(), key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(7, 5.4))
    ax.barh([k for k, _ in datos], [v for _, v in datos], color=AZUL, height=0.62)
    ax.axvline(c["total"], color=NARANJA, linewidth=1.5)
    ax.text(c["total"] + 1, len(datos) - 0.6, f"total {c['total']} %", fontsize=8)
    for i, (_, v) in enumerate(datos):
        ax.text(v + 1, i, f"{v:.0f}%", va="center", fontsize=7.5, color=SECUNDARIO)
    ax.set_xlim(0, 112)
    ax.tick_params(axis="y", labelsize=8)
    ax.set_title("Cobertura de código por archivo")
    ax.set_xlabel("% de líneas ejecutadas por las pruebas")
    guardar(fig, ax, os.path.join(salida, "03_cobertura_por_archivo.png"), "x")


def defectos(salida):
    filas = list(csv.DictReader(open(os.path.join(RAIZ, "metricas", "datos", "defectos.csv"), encoding="utf-8")))
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for ax, campo, claves, nombres, titulo in (
        (axs[0], "fase_deteccion", ["revision", "pruebas", "produccion"], ["Revisión", "Pruebas", "Producción"],
         "Defectos por fase de detección"),
        (axs[1], "severidad", ["critica", "alta", "media", "baja"], ["Crítica", "Alta", "Media", "Baja"], "Defectos por severidad"),
    ):
        b = ax.bar(nombres, [sum(1 for f in filas if f[campo] == k) for k in claves], color=AZUL, width=0.55)
        etiquetas(ax, b)
        ax.set_title(titulo, fontsize=10.5)
    abiertos = sum(1 for f in filas if not f["fecha_reparado"])
    fig.suptitle(f"{len(filas)} defectos registrados · {abiertos} abiertos", x=0.01, ha="left", fontsize=9, color=SECUNDARIO)
    guardar(fig, list(axs), os.path.join(salida, "04_defectos.png"))


def desviacion(m, salida):
    mods = m["proyecto"]["desviacion"]["por_modulo"]
    x = range(len(mods))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.bar([i - w / 2 for i in x], [q["horas_estimadas"] for q in mods], w, color=AZUL, label="Estimadas")
    ax.bar([i + w / 2 for i in x], [q["horas_reales"] for q in mods], w, color=NARANJA, label="Reales")
    for i, q in enumerate(mods):
        ax.text(i + w / 2, q["horas_reales"] + 0.3, f"{q['desviacion_porcentaje']:+.0f}%", ha="center", fontsize=8)
    ax.set_xticks(list(x), [f"S{q['sprint']}\n{q['modulo'].replace('Persistencia ', '')}" for q in mods], fontsize=7.5)
    ax.set_ylabel("Horas")
    ax.legend(frameon=False, loc="upper left")
    ax.set_title(f"Horas estimadas vs reales por sprint (desviación total {m['proyecto']['desviacion']['desviacion_porcentaje']:+.0f} %)")
    guardar(fig, ax, os.path.join(salida, "05_desviacion_por_sprint.png"))


def densidad(m, salida):
    mods = [q for q in m["proyecto"]["desviacion"]["por_modulo"] if q["densidad_defectos_kloc"] is not None]
    prom = m["producto"]["densidad_defectos"]["por_kloc"]
    fig, ax = plt.subplots(figsize=(7, 3.2))
    b = ax.bar([q["modulo"] for q in mods], [q["densidad_defectos_kloc"] for q in mods], color=AZUL, width=0.55)
    etiquetas(ax, b)
    ax.axhline(prom, color=NARANJA, linewidth=1.5)
    ax.text(len(mods) - 0.6, prom + 0.3, f"promedio {prom}", fontsize=8, ha="right")
    ax.tick_params(axis="x", labelsize=7.5)
    ax.set_title("Densidad de defectos por módulo (defectos / KLOC)")
    guardar(fig, ax, os.path.join(salida, "06_densidad_por_modulo.png"))


def estimacion(e, salida):
    if not e:
        return
    tecnicas = ["Juicio de\nexpertos", "Análoga", "Tres puntos\n(PERT)", "Puntos de\nfunción"]
    horas = [e[k]["total_horas"] for k in ("juicio_expertos", "analoga", "tres_puntos", "puntos_funcion")]
    fig, ax = plt.subplots(figsize=(7, 3.3))
    b = ax.bar(tecnicas, horas, color=AZUL, width=0.55)
    etiquetas(ax, b, "{:.1f} h", dentro=True)
    if e.get("horas_reales"):
        ax.axhline(e["horas_reales"], color=NARANJA, linewidth=1.8)
        ax.text(3.35, e["horas_reales"] + 2, f"real: {e['horas_reales']:.0f} h", fontsize=8.5, ha="right")
    ax.set_ylabel("Horas")
    ax.set_title("Horas estimadas por técnica vs horas reales")
    guardar(fig, ax, os.path.join(salida, "07_estimacion.png"))


def tendencia(salida):
    ruta = os.path.join(RAIZ, "metricas", "resultados", "historial.csv")
    if not os.path.exists(ruta):
        return
    filas = list(csv.DictReader(open(ruta, encoding="utf-8")))
    if not filas:
        return
    muchas = len(filas) > 4
    # Con muchas ejecuciones las etiquetas se enciman: se inclinan y se deja solo el commit
    x = [f["commit"] if muchas else f"{f['commit']}\n{f['fecha'][5:10]}" for f in filas]
    fig, axs = plt.subplots(1, 3, figsize=(8.4, 3.4 if muchas else 3.0))
    for ax, campo, titulo in ((axs[0], "cobertura_pct", "Cobertura (%)"),
                              (axs[1], "defectos_abiertos", "Defectos abiertos"),
                              (axs[2], "cc_promedio", "Complejidad promedio")):
        y = [float(f[campo]) for f in filas]
        ax.plot(x, y, color=AZUL, linewidth=2, marker="o", markersize=6)
        ax.annotate(f"{y[-1]:g}", (len(y) - 1, y[-1]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8.5)
        ax.set_title(titulo, fontsize=10.5)
        if muchas:
            ax.tick_params(axis="x", labelsize=7, rotation=45)
            for etiqueta in ax.get_xticklabels():
                etiqueta.set_horizontalalignment("right")
        else:
            ax.tick_params(axis="x", labelsize=7)
        ax.set_ylim(0, 100 if campo == "cobertura_pct" else max(y) * 1.5 + 1)
    fig.suptitle(f"Tendencia de la calidad por ejecución del pipeline ({len(filas)} ejecuciones)", x=0.01, ha="left",
                 fontsize=11, fontweight="bold")
    guardar(fig, list(axs), os.path.join(salida, "08_tendencia_historial.png"))


def scrum(m, salida):
    """Release burndown (puntos pendientes al cerrar cada sprint) y velocidad."""
    mods = m["proyecto"]["desviacion"]["por_modulo"]
    pts = [q["puntos_historia"] for q in mods]
    n, total = len(pts), sum(pts)
    restantes = [total]
    for p in pts:
        restantes.append(restantes[-1] - p)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.3))
    xs = list(range(n + 1))
    a.plot(xs, [total - total * i / n for i in xs], "--", color="#444444", linewidth=2, label="Ideal")
    a.plot(xs, restantes, "-o", color=AZUL, linewidth=2.5, label="Real")
    for x, y in zip(xs, restantes):
        a.annotate(str(y), (x, y), textcoords="offset points", xytext=(6, 6), fontsize=9)
    a.set_xticks(xs, ["Inicio"] + [f"S{q['sprint']}" for q in mods], fontsize=8.5)
    a.set_ylabel("Puntos pendientes")
    a.legend(frameon=False)
    a.set_title(f"Release burndown ({total} puntos)", loc="left", fontweight="bold")
    barras = b.bar(range(1, n + 1), pts, color=AZUL, width=0.62)
    etiquetas(b, barras)
    prom = total / n
    b.axhline(prom, color=NARANJA, linewidth=2)
    b.text(n + 0.4, prom + 0.3, f"promedio {prom:.2f}", ha="right", fontsize=9.5)
    b.set_xticks(range(1, n + 1), [f"S{q['sprint']}" for q in mods])
    b.set_title("Velocidad (puntos por sprint)", loc="left", fontweight="bold")
    guardar(fig, [a, b], os.path.join(salida, "09_scrum_burndown_velocidad.png"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reportes", default="reports")
    ap.add_argument("--salida", default=os.path.join("metricas", "resultados", "graficas"))
    args = ap.parse_args()
    os.makedirs(args.salida, exist_ok=True)
    m = json.load(open(os.path.join(args.reportes, "metricas.json"), encoding="utf-8"))
    ruta_e = os.path.join(args.reportes, "estimacion.json")
    e = json.load(open(ruta_e, encoding="utf-8")) if os.path.exists(ruta_e) else None
    print("Generando gráficas en", args.salida)
    complejidad(m, args.salida)
    top_complejidad(m, args.salida)
    cobertura(m, args.salida)
    defectos(args.salida)
    desviacion(m, args.salida)
    densidad(m, args.salida)
    estimacion(e, args.salida)
    tendencia(args.salida)
    scrum(m, args.salida)


if __name__ == "__main__":
    main()
