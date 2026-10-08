## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-08 13:43

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **78 / 100**, sustentada en cobertura de pruebas del 86,58 %, 315/315 tests en verde, cero defectos abiertos y análisis estático sin hallazgos (Ruff). Sin embargo, el DRE del 44,44 % y un MTTD de 9,71 días revelan que el proceso de detección temprana es insuficiente para un producto de voz con IA en producción. **El proyecto puede liberarse en versión beta controlada**, condicionado a la ejecución del plan de mejora en las dos semanas siguientes al lanzamiento.

---

## Idoneidad funcional

| Sub-característica | Evidencia | Valoración |
|---|---|---|
| **Completitud funcional** | 315 casos de prueba cubriendo 34 de 35 archivos (app_desktop.py excluido al 0 %) | ⚠️ Aceptable — gap en UI de escritorio |
| **Corrección funcional** | 0 defectos abiertos / 18 corregidos; análisis Ruff limpio | ✅ Buena |
| **Pertinencia funcional** | Skills cubiertas: voz, memoria, recordatorios, multimedia, web, sistema, idiomas, hábitos | ✅ Buena |

**Puntos de atención:**
- `app_desktop.py` tiene **0 % de cobertura**, lo que deja la interfaz de escritorio sin ningún respaldo de pruebas.
- `voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %) son los módulos funcionales con menor cobertura y coinciden con los de mayor densidad de defectos histórica (Sprint 1 y 5).
- Los **4 defectos graves** registrados se detectaron **todos en producción** (DRE graves = 0 %), lo que representa el riesgo funcional más serio del proyecto.

---

## Fiabilidad

### Métricas clave

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** | 233,09 h (9,71 días) | ⚠️ Detección muy tardía; los defectos viven casi 10 días antes de ser descubiertos |
| **MTTR** | 3,9 h (234 min) | ✅ Excelente capacidad de reparación |
| **DRE (Defect Removal Efficiency)** | 44,44 % | 🔴 Crítico — menos de la mitad de defectos se detectan antes de producción |
| **Defectos en producción** | 10 / 18 (55,56 %) | 🔴 Más de la mitad escapan al pipeline |
| **Defectos graves detectados en pruebas** | 0 / 4 (0 %) | 🔴 Los 4 graves llegaron a producción |

### Análisis por sub-característica (ISO/IEC 25010)

| Sub-característica | Evaluación |
|---|---|
| **Madurez** | Media-baja: 10 defectos en producción indican que el producto aún requiere estabilización. El MTTD alto sugiere que los fallos tardan en manifestarse o en ser reportados. |
| **Disponibilidad** | Positiva: el MTTR de 3,9 h implica recuperación rápida; el pipeline CI/CD con Docker facilita despliegues correctivos ágiles. |
| **Tolerancia a fallos** | No evaluable directamente con los datos; sin pruebas de caos o escenarios de fallo de APIs externas (Claude, ElevenLabs) documentados en el dataset. |
| **Recuperabilidad** | Buena: 18/18 defectos reparados, sprint 9 dedicado a corrección ejecutado dentro del presupuesto. |

> **Ratio MTTR/MTTD = 0,017** — Se repara 60 veces más rápido de lo que se detecta. El cuello de botella es la detección, no la corrección.

---

## Mantenibilidad

### Índice de mantenibilidad

| Métrica | Valor | Referencia |
|---|---|---|
| Mantenibilidad promedio (MI) | **72,02** | Rango aceptable: 65–100; >85 = bueno |
| % funciones en rango A–B | **94,39 %** | ✅ Excelente distribución |
| Complejidad promedio | **3,44** | ✅ Rango A (1–5) |
| Complejidad mediana | **2,0** | ✅ Muy buena |
| Complejidad máxima | **15** | ⚠️ Rango C — requiere atención |

### Distribución de rangos ciclomáticos

| Rango | Umbral CC | Funciones | % | Interpretación |
|---|---|---|---|---|
| **A** | 1–5 | 180 | 84,11 % | ✅ Simple, bajo riesgo |
| **B** | 6–10 | 22 | 10,28 % | ✅ Moderado, manejable |
| **C** | 11–15 | 12 | 5,61 % | ⚠️ Complejo, propenso a errores |
| **D** | 16–20 | 0 | 0 % | — |
| **E** | 21–25 | 0 | 0 % | — |
| **F** | >25 | 0 | 0 % | — |

### Funciones prioritarias a refactorizar (top 10, todas en rango C)

| Prioridad | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 🔴 1 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | Descomponer en sub-handlers por tipo de app |
| 🔴 2 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Extraer lógica de parsing de tiempo a función dedicada |
| 🟠 3 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | Aplicar patrón Strategy o diccionario de despacho |
| 🟠 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | Separar control de volumen, reproducción y búsqueda |
| 🟠 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | Extraer ramas de acción a métodos privados |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 205 | 12 | Dividir condiciones de actualización en predicados nombrados |
| 🟡 7 | `skills/memoria.py` | `intentar` | 61 | 12 | Separar lectura, escritura y búsqueda de memoria |
| 🟡 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 | Extraer notificación y cálculo de tiempo restante |
| 🟡 9 | `skills/web.py` | `intentar` | 53 | 12 | Separar búsqueda, navegación y extracción de contenido |
| 🟡 10 | `cerebro.py` | `preguntar` | 104 | 11 | Descomponer flujo de diálogo en estados explícitos |

> **Nota:** El patrón común en las funciones `intentar` es un `if/elif` extenso de intención de usuario. Se recomienda aplicar un **diccionario de despacho** o el patrón **Command** para reducir CC a rango A–B en todos los casos.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (44 %): defectos graves llegan a producción** | Alta | Crítico | Agregar pruebas de integración para APIs externas (Claude, ElevenLabs) y pruebas de regresión para los 4 escenarios graves históricos |
| **MTTD de 9,71 días: detección muy tardía** | Alta | Alto | Implementar monitoreo de errores en producción (Sentry o similar) y alertas automáticas ante excepciones no controladas |
| **app_desktop.py con 0 % de cobertura** | Media | Alto | Crear suite de pruebas UI (pytest-qt o similar) antes del siguiente sprint; establecer umbral mínimo de cobertura en GitHub Actions |
| **voice.py y skills/multimedia.py con cobertura <75 %** | Media | Medio | Añadir pruebas unitarias con mocks de hardware (micrófono, altavoces) en el siguiente ciclo de calidad |
| **Desviación de estimación del 19,61 % global** | Media | Medio | Adoptar planning poker con histórico de velocidad (7,45 pts/sprint) para futuros sprints; el Sprint 5 mostró 60 % de desviación como señal de alarma |
| **12 funciones en rango C de complejidad ciclomática** | Media | Medio | Establecer umbral de CC ≤ 10 en el pipeline CI/CD (p. ej., con `radon` + umbral de falla en GitHub Actions) |
| **Dependencia de APIs externas de pago sin circuit breaker** | Baja | Alto | Implementar patrón Circuit Breaker y modo degradado (respuestas locales) ante fallos de Claude o ElevenLabs |
| **Sprint 1 con densidad de defectos de 13,74/KLOC** | Baja (ya corregido) | Medio | Aplicar revisiones de código obligatorias en módulos de núcleo para nuevas funciones de voz |

---

## Plan de mejora

Las siguientes acciones están ordenadas por impacto en calidad y urgencia, con enfoque **preventivo**.

---

**Acción 1 — Elevar el DRE mediante pruebas de integración y escenarios de regresión graves**
- **Qué:** Crear al menos 4 casos de prueba que reproduzcan los defectos graves históricos (actualmente con DRE graves = 0 %). Incluir mocks de APIs externas (Claude, ElevenLabs) con respuestas de error, timeout y rate-limit.
- **Cómo:** Agregar carpeta `tests/integration/` con pytest y `responses`/`httpx` para simular APIs; ejecutar en GitHub Actions en rama `main`.
- **Métrica que mejora:** `DRE` (objetivo: ≥ 70 %) y `defectos_por_fase.produccion` (reducir de 10 a ≤ 5).

---

**Acción 2 — Reducir el MTTD con monitoreo de errores en tiempo real**
- **Qué:** Integrar Sentry (plan gratuito) en `main.py` y `cerebro.py` para captura automática de excepciones no controladas con trazas de contexto de voz.
- **Cómo:** `sentry_sdk.init()` al arranque; configurar alertas de error rate y nuevo issue en Discord/email del equipo.
- **Métrica que mejora:** `MTTD` (objetivo: < 24 h, desde los actuales 233 h).

---

**Acción 3 — Cubrir app_desktop.py y elevar la cobertura global al 90 %**
- **Qué:** Escribir pruebas para `app_desktop.py` (actualmente 0 %) y mejorar `voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %) usando mocks de PyAudio y subprocess.
- **Cómo:** Configurar `--cov-fail-under=90` en el `pytest` del workflow de GitHub Actions para que el pipeline falle si la cobertura baja de ese umbral.
- **Métrica que mejora:** `cobertura.total` (de 86,58 % → ≥ 90 %) y cobertura de `app_desktop.py` (de 0 % → ≥ 80 %).

---

**Acción 4 — Refactorizar las 5 funciones con CC ≥ 13 y añadir gate de complejidad en CI**
- **Qué:** Refactorizar `apps_instaladas.intentar` (CC=15), `recordatorios.intentar` (CC=14), `apps_instaladas.resolver` (CC=13), `multimedia.intentar` (CC=13) y `pestanas.intentar` (CC=13) aplicando diccionarios de despacho.
- **Cómo:** Agregar `radon cc -n C .` como paso de falla en GitHub Actions (ninguna función debe superar CC=10 para fusionar a `main`).
- **Métrica que mejora:** `complejidad.maxima` (de 15 → ≤ 10), `mantenibilidad_promedio` (de 72,02 → objetivo ≥ 80) y cobertura de ramas en esas funciones.

---

**Acción 5 — Establecer revisiones de código obligatorias (code review) con checklist de calidad**
- **Qué:** Configurar en GitHub la regla de protección de rama `main` exigiendo ≥ 1 aprobación con checklist: (a) CC ≤ 10, (b) cobertura no regresa, (c) no hay defectos conocidos sin ticket abierto, (d) se actualizó documentación de la función si cambió su firma.
- **Cómo:** Añadir archivo `.github/pull_request_template.md` con el checklist y activar "Require pull request reviews before merging".
- **Métrica que mejora:** `eficacia_revision` (de 16,67 % → objetivo ≥ 30 %) y `defectos_por_fase.revision` (detectar más defectos en revisión, menos en producción).

---

## Estimación (juicio experto de la IA)

### Comparativo de técnicas frente a las 122 horas reales

| Técnica | Total estimado | Error absoluto | Error % |
|---|---|---|---|
| **Juicio de expertos** (promedio) | 110,5 h | 11,5 h | 9,43 % |
| **Tres puntos PERT** | 114,68 h | 7,32 h | 6,00 % |
| **Puntos de función** | 146,38 h | 24,38 h | 19,98 % |
| **Análoga** | 152,53 h | 30,53 h | 25,02 % |

### Técnica ganadora: **Tres Puntos (PERT)**

La estimación por **tres puntos PERT** fue la más precisa con un error del **6 %** (7,32 h sobre 122 h reales), y las 122 h reales caen cómodamente dentro del **intervalo de confianza al 95 % [104,03 – 125,33 h]**, lo que valida el modelo estadístico.

**¿Por qué funcionó mejor?**

1. **Capturó la asimetría del riesgo:** Al pedir un escenario optimista (O), más probable (M) y pesimista (P) por módulo, la técnica absorbió la incertidumbre de integrar APIs externas de voz e IA, que son los módulos que más se desviaron (Sprint 1: +40 %, Sprint 5: +60 %).
2. **La fórmula PERT pondera el escenario más probable:** La ponderación `(O + 4M + P) / 6` redujo el efecto de los valores extremos, mientras que la estimación análoga sobreestimó al no diferenciar suficientemente la complejidad de Azmuth respecto a un CRUD convencional (factor de ajuste del 10 % insuficiente dada la complejidad real de integración).
3. **El juicio de expertos fue el segundo más cercano** (error del 9,43 %), impulsado por la estimación de la IA (Claude) que fue más conservadora (119 h vs. 102 h del alumno) y se acercó más a la realidad, lo que sugiere que el **alumno tendió a subestimar sistemáticamente** en módulos de alta incertidumbre técnica.
4. **Puntos de función y estimación análoga sobreestimaron** porque su calibración (0,45 h/PF y 22,5 SLOC/h respectivamente) no refleja la productividad real del equipo (velocidad observada: ~7,45 pts/sprint con horas variables por punto de 0,88 a 2,0).

> **Recomendación para proyectos futuros:** Usar **PERT como técnica base**, complementada con el juicio del experto externo (IA) como ancla pesimista, especialmente en módulos con integraciones de terceros o hardware (voz, sensores).
