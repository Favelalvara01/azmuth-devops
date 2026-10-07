## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
*ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-07*

---

## Dictamen general

El proyecto Azmuth alcanza una calificación de **67 / 100**, sustentada en una cobertura de pruebas del 76 %, una tasa de aprobación del 100 % en suite automatizada y un índice de mantenibilidad promedio de 71.26. **No se recomienda su liberación en el estado actual**, principalmente por el DRE del 53 %, que indica que más de la mitad de los defectos graves se escaparon a producción, la cobertura nula en dos archivos críticos (`app_desktop.py`, `skills/interfaz.py`), y la presencia de funciones con complejidad ciclomática en rango D que representan puntos de falla concentrados.

---

## Idoneidad funcional

### Completitud funcional
- **157 pruebas automatizadas**, todas aprobadas; sin `xfail` pendientes.
- Quedan **1 defecto abierto** (0.39 por KLOC), lo que indica que la funcionalidad principal está mayoritariamente entregada.
- Dos archivos (`app_desktop.py` y `skills/interfaz.py`) con **cobertura 0 %** sugieren que rutas funcionales completas —interfaz gráfica e interacción de skills— no están validadas automáticamente.

### Corrección funcional
- Densidad de defectos histórica: **5.83 defectos/KLOC** (total), reduciéndose a **0.39 defectos/KLOC** con solo 1 abierto.
- El módulo con mayor densidad histórica es **Núcleo de voz** (16.89/KLOC, Sprint 1), seguido de **Interfaz y servidor** (7.32/KLOC, Sprint 5), ambos módulos de alto riesgo.
- `main.py` acumula **4 defectos registrados** con solo 26.01 % de cobertura, una combinación de alto riesgo.

### Pertinencia funcional
- El modelado de Puntos de Función arroja **224.7 PF ajustados** con factores elevados en comunicación de datos (4), entrada en línea (4) y eficiencia del usuario (4), coherentes con un asistente de voz que integra APIs externas (Claude, ElevenLabs).
- La arquitectura de skills modulares y el pipeline DevOps completo son pertinentes para el dominio del producto.

---

## Fiabilidad

### Madurez
- **14 de 15 defectos** han sido resueltos; el ritmo de cierre es positivo.
- El **DRE (Defect Removal Effectiveness) es 53.33 %**, calculado como:

  > DRE = defectos detectados en pruebas / defectos totales antes de producción  
  > DRE = 5 / (5 + 3 + 7 pre-producción combinados) → **53.33 %**

  Un DRE saludable supera el 85 %. El valor actual significa que **7 de los 15 defectos llegaron a producción**, incluyendo defectos graves que no fueron capturados en pruebas formales.

- **Graves detectados en pruebas: 0 de 4 graves totales** → todos los defectos graves pasaron a producción sin ser capturados antes.

### Disponibilidad
- La suite de 157 pruebas se ejecuta en **3.66 segundos**, indicando un ciclo de retroalimentación ágil y un pipeline robusto.
- La presencia de contenedores Docker y GitHub Actions favorece la disponibilidad del entorno de despliegue.

### Tolerancia a fallos y recuperabilidad

| Indicador | Valor | Interpretación |
|---|---|---|
| **MTTD** | 279.62 h (11.65 días) | Tiempo elevado para detectar un defecto; sugiere monitoreo reactivo |
| **MTTR** | 2.69 h (162 min) | Tiempo de reparación excelente; el equipo resuelve con rapidez |
| **DRE** | 53.33 % | Crítico: más del 46 % de defectos escapan a producción |
| Defectos en producción | 7 / 15 (46.67 %) | Inaceptable para liberación estable |

El MTTR bajo (2.69 h) es un punto a favor, pero el MTTD alto (≈12 días) revela que los defectos viven demasiado tiempo sin ser detectados, elevando el costo de corrección.

---

## Mantenibilidad

### Índice de mantenibilidad
- **Promedio: 71.26** — zona amarilla (aceptable pero mejorable; el umbral de alerta suele situarse en 65, y el óptimo sobre 85).

### Distribución de complejidad ciclomática

| Rango | Descripción | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Excelente | 117 | 79.05 % |
| **B** (6–10) | Buena | 17 | 11.49 % |
| **C** (11–15) | Moderada — vigilar | 12 | 8.11 % |
| **D** (16–25) | Alta — refactorizar | 2 | 1.35 % |
| **E / F** (>25) | Crítica | 0 | 0.00 % |

El 90.54 % de las funciones están en rango A-B, lo cual es positivo. Sin embargo, las 2 funciones en rango D y las 12 en rango C concentran riesgo desproporcionado.

### Funciones a refactorizar (ordenadas por urgencia)

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción sugerida |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 161 | 27 | D | Descomponer por tipo de acción usando tabla de despacho o patrón Command |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | D | Extraer sub-handlers por intención; aplicar early return |
| 🟠 3 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | C | Extraer lógica de resolución a métodos privados |
| 🟠 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Separar parsing de ejecución |
| 🟠 5 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | C | Simplificar condicionales con diccionarios de estrategia |
| 🟡 6 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Agrupar variantes de comando en enumeraciones |
| 🟡 7 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Mismo patrón que multimedia |
| 🟡 8 | `cerebro.py` | `actualizar_perfil_si_toca` | 136 | 12 | C | Extraer evaluación de condiciones a función predicado |
| 🟡 9 | `main.py` | `escuchar` | 102 | 12 | C | Refactorizar junto con aumento de cobertura (actualmente 26 %) |
| 🟡 10 | `skills/memoria.py` | `intentar` | 61 | 12 | C | Reducir anidamiento con guardas |

### Análisis estático (Ruff)
- **16 violaciones E501** (líneas demasiado largas, máximo 363 caracteres en `servidor.py:231`), todas concentradas en `servidor.py`, `skills/__init__.py`, `skills/aplicaciones.py` y `skills/web.py`.
- Cero errores de linting de nivel error o crítico; las violaciones son de estilo, pero dificultan la revisión y el diff en PR.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos graves no detectados antes de producción (DRE 53 %) | **Alta** | **Crítico** | Incrementar pruebas de integración enfocadas en flujos graves; establecer criterio de salida: DRE ≥ 85 % antes de merge a main |
| Fallo silencioso en `app_desktop.py` y `skills/interfaz.py` (cobertura 0 %) | **Alta** | **Alto** | Agregar pruebas unitarias/de integración o al menos smoke tests; bloquear merge si cobertura de módulo es 0 % |
| Regresiones en `ejecutar_accion` (CC=27) y `intentar` de aplicaciones (CC=24) | **Media** | **Alto** | Refactorizar antes de siguiente sprint; añadir pruebas de caja blanca que cubran cada rama |
| MTTD elevado (≈12 días): defectos viven demasiado tiempo | **Media** | **Medio** | Implementar alertas automáticas de excepciones en runtime (p. ej., Sentry); revisiones de código con checklist de calidad |
| Desviación de estimación recurrente en módulos de integración (Sprint 5: +60 %) | **Media** | **Medio** | Usar estimación por tres puntos como línea base oficial; añadir buffer explícito del 20 % para módulos con APIs externas |
| Líneas excesivamente largas en `servidor.py` dificultan revisiones (hasta 373 chars) | **Alta** | **Bajo** | Configurar Ruff/Black en pre-commit hook con `max-line-length=140`; bloquear PR con violaciones E501 |
| Concentración de defectos en `main.py` (4 defectos, cobertura 26 %) | **Media** | **Alto** | Refactorizar función `escuchar` (CC=12) y elevar cobertura de `main.py` a ≥ 70 % en próximo sprint |

---

## Plan de mejora

Las siguientes 5 acciones están ordenadas de mayor a menor impacto en calidad liberada, con enfoque preventivo:

---

**Acción 1 — Elevar el DRE mediante pruebas de integración para defectos graves** 🔴
- **Qué:** Diseñar al menos 1 caso de prueba de integración por cada uno de los 4 defectos graves históricos, simulando el flujo end-to-end (voz → cerebro → skill → respuesta).
- **Métrica que mejorará:** DRE: de 53.33 % → objetivo ≥ 85 %; defectos que llegan a producción: de 7 → ≤ 2.
- **Cuándo:** Antes del siguiente merge a `main`; criterio de salida obligatorio.

---

**Acción 2 — Cubrir `app_desktop.py` y `skills/interfaz.py` con pruebas mínimas** 🔴
- **Qué:** Implementar smoke tests o pruebas de integración básicas (mocking de GUI/OS); agregar regla en GitHub Actions que falle el pipeline si algún archivo tiene cobertura < 20 %.
- **Métrica que mejorará:** Cobertura total: de 76.43 % → objetivo ≥ 82 %; archivos con 0 % de cobertura: de 2 → 0.
- **Cuándo:** Sprint inmediato, antes de liberación.

---

**Acción 3 — Refactorizar `ejecutar_accion` (CC=27) y `intentar` de aplicaciones (CC=24)** 🟠
- **Qué:** Aplicar patrón Command o tabla de despacho (diccionario función→handler) para eliminar cadenas de `if/elif`; meta: CC ≤ 10 en ambas funciones.
- **Métrica que mejorará:** Complejidad ciclomática máxima: de 27 → ≤ 10; funciones en rango D: de 2 → 0; índice de mantenibilidad promedio: de 71.26 → objetivo ≥ 78.
- **Cuándo:** Sprint siguiente, prioritario sobre nuevas features.

---

**Acción 4 — Reducir MTTD mediante monitoreo activo de excepciones en runtime** 🟠
- **Qué:** Integrar una herramienta de tracking de errores (p. ej., Sentry con SDK Python) o al menos logging estructurado con alertas en GitHub Actions/Discord; establecer SLA interno: MTTD ≤ 48 h.
- **Métrica que mejorará:** MTTD: de 279.62 h → objetivo ≤ 48 h; costo de corrección asociado al tiempo de vida del defecto.
- **Cuándo:** Configuración en Sprint 7 (DevOps ya establecido, bajo esfuerzo marginal).

---

**Acción 5 — Estandarizar linting y formato en el pipeline CI** 🟡
- **Qué:** Agregar `ruff --select E501` y `black --check` como paso obligatorio en GitHub Actions; configurar pre-commit hook local para que ningún desarrollador haga push con las 16 violaciones actuales; corregir las líneas largas existentes en `servidor.py`.
- **Métrica que mejorará:** Violaciones de estilo (Ruff E501): de 16 → 0; mantenibilidad del código (legibilidad en PR reviews); tiempo de revisión de código estimado.
- **Cuándo:** Inmediato; esfuerzo < 2 horas.

---

## Estimación (juicio experto de la IA)

### Resumen comparativo de técnicas

| Técnica | Horas estimadas | Error absoluto vs. 90 h reales | Error % |
|---|---|---|---|
| Juicio de expertos (promedio) | 80.33 h | 9.67 h | 10.74 % |
| Tres puntos PERT (total) | 81.85 h | 8.15 h | 9.06 % |
| Puntos de función | 101.12 h | 11.12 h | 12.36 % |
| Analogía | 125.89 h | 35.89 h | 39.88 % |

### Técnica más cercana: **Tres Puntos (PERT)** — 81.85 h, error del 9.06 %

La técnica de **tres puntos con distribución PERT** fue la que más se acercó a las 90 horas reales, con un error absoluto de solo **8.15 horas (9.06 %)**. Adicionalmente, el intervalo de confianza al 95 % que produjo (**72.26 h – 91.44 h**) **contiene el valor real de 90 horas**, lo que demuestra que no solo el punto central fue cercano, sino que la incertidumbre fue modelada correctamente.

**Por qué funcionó mejor:**

1. **Capturó la asimetría de riesgo:** Al solicitar estimación optimista (O), más probable (M) y pesimista (P) por módulo, la técnica absorbió la variabilidad real de módulos como "Interfaz y servidor" (O=8, P=22), que terminó siendo el sprint con mayor desviación (+60 %).

2. **Contrarrestó el sesgo de anclaje individual:** El juicio de expertos suele estar anclado en la estimación del desarrollador (72 h), que fue la más optimista y quedó 18 h por debajo de la realidad. PERT mitiga esto al forzar un escenario pesimista explícito.

3. **La analogía sobreestimó severamente (+39.88 %)** porque el factor de ajuste del +10 % sobre el proyecto de referencia (Easy Learning, 1 800 SLOC, 80 h) no capturó adecuadamente que la diferencia en complejidad de integración con APIs de voz e IA no es lineal con el SLOC.

4. **Los puntos de función (101.12 h)** sobreestimaron moderadamente porque la tasa de productividad aplicada (0.45 h/PF) puede no ser representativa del equipo específico; sin calibración histórica propia, este valor introduce sesgo sistemático al alza.

**Recomendación para futuros proyectos:** Usar **Tres Puntos PERT como técnica principal**, complementado con juicio de expertos para validar el escenario más probable (M), y reservar Puntos de Función para proyectos con historial de productividad calibrado del equipo.

---

*Auditoría elaborada con base exclusiva en los datos del pipeline proporcionados. Fecha de referencia de los datos: 2026-10-07 06:58.*
