"""
analisis_ia.py — Análisis de calidad con IA (Claude) sobre las métricas.

En el pipeline de CI, después de calcular las métricas, este script le
manda a Claude los resultados (complejidad, cobertura, defectos, tiempos,
estimaciones y hallazgos del análisis estático) y le pide un dictamen de
calidad: grado de cumplimiento ISO/IEC 25010 (idoneidad funcional y
fiabilidad), riesgos, y acciones preventivas priorizadas.

Uso:  python metricas/analisis_ia.py --reportes reports
Necesita la variable ANTHROPIC_API_KEY (en GitHub: Settings → Secrets →
Actions → ANTHROPIC_API_KEY). Si no está, deja un aviso y NO rompe el pipeline.
"""
import argparse
import json
import os
import sys

from consola import mostrar  # noqa: E402  (tablas con formato en la terminal)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:  # en local toma la clave del mismo .env que usa Azmuth (en CI viene de los Secrets)
    from dotenv import load_dotenv
    load_dotenv(os.path.join(RAIZ, ".env"))
except ImportError:
    pass

MODELO = os.getenv("MODELO_IA", "claude-sonnet-4-6")

INSTRUCCIONES = """Eres un auditor de aseguramiento de calidad de software (ISO/IEC 25010 e ISO/IEC 25023).
Analiza las métricas del proyecto "Azmuth", un asistente de voz con IA en Python para Windows, con
pipeline DevOps (pytest, GitHub Actions, Docker). Responde en español, en Markdown, con estas secciones:

### Dictamen general
2-3 oraciones con una calificación de 0 a 100 y si el proyecto cumple para liberarse.
### Idoneidad funcional
Completitud, corrección y pertinencia funcional según las pruebas y defectos abiertos.
### Fiabilidad
Madurez, disponibilidad, tolerancia a fallos y recuperabilidad (usa MTTD, MTTR, DRE).
### Mantenibilidad
Interpreta la complejidad ciclomática (rangos A-F) y nombra las funciones a refactorizar.
### Riesgos
Tabla Markdown: Riesgo | Probabilidad | Impacto | Acción preventiva.
### Plan de mejora
5 acciones concretas y priorizadas (enfoque preventivo), cada una con la métrica que mejorará.
### Estimación (juicio experto de la IA)
Comenta qué técnica de estimación se acercó más a las horas reales y por qué.

Basa todo en los datos; no inventes cifras que no estén en ellos."""


def cargar(ruta, por_defecto=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return por_defecto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reportes", default="reports")
    args = ap.parse_args()
    salida = os.path.join(args.reportes, "analisis_ia.md")

    metricas = cargar(os.path.join(args.reportes, "metricas.json"))
    if not metricas:
        print("No hay reports/metricas.json — corre primero calcular_metricas.py")
        sys.exit(1)
    datos = json.loads(metricas)
    # El detalle por archivo es muy largo; Claude solo necesita los agregados y el top 10
    datos["producto"]["lineas"].pop("por_archivo", None)
    contexto = {
        "metricas": datos,
        "estimacion": json.loads(cargar(os.path.join(args.reportes, "estimacion.json"), "{}")),
        "analisis_estatico_ruff": (cargar(os.path.join(args.reportes, "ruff.txt"), "") or "")[-3000:],
    }

    clave = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not clave:
        aviso = ("## 🤖 Análisis con IA\n\n_No se configuró el secreto ANTHROPIC_API_KEY; "
                 "se omitió el análisis con Claude en esta ejecución._\n")
        open(salida, "w", encoding="utf-8").write(aviso)
        mostrar(aviso)
        return

    import anthropic
    cliente = anthropic.Anthropic(api_key=clave)
    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=8000,
        system=INSTRUCCIONES,
        messages=[{"role": "user", "content": "Datos del pipeline:\n```json\n"
                   + json.dumps(contexto, ensure_ascii=False, indent=1) + "\n```"}],
    )
    texto = "".join(b.text for b in respuesta.content if b.type == "text").strip()
    md = f"## 🤖 Análisis de calidad con IA ({MODELO})\n\n{texto}\n"
    open(salida, "w", encoding="utf-8").write(md)
    mostrar(md)


if __name__ == "__main__":
    main()
