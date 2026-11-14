## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-11-14 01:58

---

## Dictamen general

El proyecto Azmuth alcanza una calificación de **78 / 100**, sustentada en una cobertura de pruebas del 87,87 %, ausencia de defectos abiertos, análisis estático sin hallazgos (Ruff) y una complejidad ciclomática predominantemente baja (94,63 % en rangos A-B). No obstante, el DRE del 54,55 % evidencia que más de la mitad de los defectos graves escaparon a las pruebas y llegaron a producción, y la cobertura de tres archivos críticos (`voice.py`, `skills/multimedia.py`, `skills/web.py`) cae por debajo del 76 %, lo que representa un riesgo residual no despreciable. **El proyecto puede liberarse condicionalmente**, siempre que se ejecuten las acciones de mejora priorizadas antes de la siguiente iteración de producción.

---

## Idoneidad funcional

### Completitud funcional
| Indicador | Valor | Referencia |
|---|---|---|
| Pruebas totales ejecutadas | 576 | — |
| Pruebas aprobadas | 567 (98,44 %) | ≥ 95 % ✅ |
| Defectos conocidos (xfail) | 9 | Documentados |
| Defectos abiertos | **0** | 0 ✅ |
| Cobertura global | 87,87 % | ≥ 80 % ✅ |

La suite de 576 pruebas cubre el flujo principal del asistente. Los 9 casos `xfail` están documentados como defectos conocidos y no bloquean funcionalidad liberada. La completitud funcional es **satisfactoria**.

### Corrección funcional
- Densidad total: **5,49 defectos/KLOC** — aceptable para un proyecto de esta complejidad (asistente de voz con múltiples APIs).
- **Todos los 22 defectos históricos están resueltos** (abiertos/KLOC = 0,0). ✅
- El sprint con mayor densidad fue el Núcleo de voz (12,5/KLOC), ya cerrado.

### Pertinencia funcional
Los 325,28 Puntos de Función ajustados (VAF = 1,07) reflejan correctamente la naturaleza del sistema: comunicación de datos (factor 4), entrada en línea (factor 4) y eficiencia del usuario final (factor 4) son los dominios de mayor peso, alineados con la propuesta de valor de un asistente de voz con IA.

---

## Fiabilidad

### Métricas clave
| Métrica | Valor | Interpretación |
|---|---|---|
| MTTD | **14,51 días** (348,25 h) | Detección tardía; defectos llegan a producción antes de detectarse |
| MTTR | **3,21 h** (193 min) | Reparación ágil ✅ |
| DRE (Detection Rate Efficiency) | **54,55 %** | ⚠️ Crítico — sólo 9 de 22 defectos detectados en pruebas; 10 llegaron a producción |
| Defectos en producción | 10 (45,45 %) | Superior al umbral recomendado (< 20 %) |
| Defectos graves en pruebas | 3 de 7 (42,86 %) | Más de la mitad de los graves escaparon |

### Madurez
- 0 defectos abiertos al cierre del proyecto → **madurez del producto: alta**.
- Tiempo de suite de pruebas: **15,89 s** para 576 casos — ejecución ultrarrápida, favorable para CI/CD.

### Disponibilidad y tolerancia a fallos
- El pipeline de GitHub Actions con Docker asegura entornos reproducibles.
- `app_desktop.py` tiene cobertura **0,0 %** — componente completamente fuera de la red de seguridad de pruebas; cualquier fallo en la capa de escritorio es indetectable automáticamente. ⚠️
- `skills/_compat.py` al **53,85 %** representa un riesgo de compatibilidad entre plataformas.

### Recuperabilidad
El MTTR de 3,21 h indica capacidad de recuperación ágil una vez detectado el defecto. El problema estructural es el MTTD elevado, no la recuperación.

---

## Mantenibilidad

### Índice de mantenibilidad
- **Promedio global:** 68,56 / 100 — rango *moderado* (umbral recomendado ≥ 70). Apenas por debajo del nivel óptimo.

### Complejidad ciclomática — distribución
| Rango | CC | Funciones | % | Significado |
|---|---|---|---|---|
| **A** | 1–5 | 245 | 82,21 % | Simple, muy mantenible ✅ |
| **B** | 6–10 | 37 | 12,42 % | Moderada, aceptable ✅ |
| **C** | 11–15 | 16 | 5,37 % | Compleja, requiere atención ⚠️ |
| **D** | 16–20 | 0 | 0 % | — |
| **E** | 21–25 | 0 | 0 % | — |
| **F** | > 25 | 0 | 0 % | — |

> **94,63 % en rangos A-B** es un resultado excelente. Sin embargo, las 16 funciones en rango C concentran el riesgo de mantenibilidad.

### Funciones prioritarias a refactorizar (Top 10, todas en rango C)

| Prioridad | Archivo | Función | Línea | CC | Riesgo adicional |
|---|---|---|---|---|---|
| 🔴 1 | `tematicas.py` | `_sintetizar` | 238 | **16** | Alta densidad de lógica de síntesis de voz |
| 🔴 2 | `skills/tiempo.py` | `_pronostico` | 100 | **16** | Integración API meteorológica |
| 🟠 3 | `skills/apps_instaladas.py` | `intentar` | 210 | 15 | Cobertura 84,09 % |
| 🟠 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Lógica temporal crítica |
| 🟡 5 | `skills/apps_instaladas.py` | `resolver` | 166 | 13 | Duplicidad de riesgo en mismo archivo |
| 🟡 6 | `skills/multimedia.py` | `intentar` | 34 | 13 | Cobertura baja (74,55 %) |
| 🟡 7 | `skills/pestanas.py` | `intentar` | 36 | 13 | — |
| 🟡 8 | `skills/tiempo.py` | `_recomendaciones` | 71 | 13 | Mismo módulo que `_pronostico` |
| 🟡 9 | `skills/web.py` | `intentar` | 93 | 13 | Cobertura baja (75,0 %) |
| 🟢 10 | `deepseek_ia.py` | `completar` | 82 | 12 | Cobertura 75,0 % |

**Estrategia recomendada:** Aplicar *Extract Method* para reducir CC ≤ 10 (rango B) en las funciones 🔴 y 🟠 antes del siguiente release.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (54,55 %):** defectos graves escapan a producción | Alta | Alto | Ampliar suite con pruebas de integración y mutation testing; establecer DRE ≥ 80 % como gate de calidad en CI |
| **Cobertura 0 % en `app_desktop.py`** | Alta | Alto | Crear pruebas unitarias con mocking de UI (pytest-qt o similar); bloquear merge si cobertura < 60 % |
| **MTTD de 14,51 días:** detección tardía de defectos | Alta | Medio | Implementar monitoreo de errores en producción (Sentry/logging estructurado) para reducir MTTD < 48 h |
| **16 funciones en CC rango C:** deuda técnica acumulable | Media | Medio | Refactorizar top-5 en próximo sprint; añadir umbral CC ≤ 10 en pipeline (Radon/flake8-bugbear) |
| **`skills/_compat.py` al 53,85 %:** riesgo de compatibilidad entre entornos | Media | Medio | Cubrir ramas de compatibilidad con pruebas parametrizadas por plataforma en matrix de GitHub Actions |
| **Desviación del 19,61 % en estimación total** | Media | Bajo | Usar velocidad histórica (7,45 pts/sprint) y rangos del método PERT para futuros sprints |
| **Dependencia de APIs externas (Gemini, Groq, DeepSeek, ElevenLabs)** sin circuit-breaker evidente | Baja | Alto | Implementar patrón *circuit-breaker* y fallback local; añadir pruebas de contrato (contract testing) |

---

## Plan de mejora

> Priorizadas por impacto en calidad y riesgo residual.

### 🥇 Acción 1 — Elevar el DRE mediante mutation testing
**Qué:** Integrar `mutmut` o `Cosmic Ray` en el pipeline de CI para validar la efectividad real de las pruebas.
**Cómo:** Configurar como tarea semanal en GitHub Actions; establecer *mutation score* ≥ 70 % como criterio de aceptación.
**Métrica que mejorará:** DRE (de 54,55 % → objetivo ≥ 80 %) y porcentaje de defectos graves detectados en pruebas (de 42,86 % → ≥ 70 %).

---

### 🥈 Acción 2 — Cubrir `app_desktop.py` y archivos críticos de baja cobertura
**Qué:** Crear pruebas unitarias para `app_desktop.py` (0 %), `voice.py` (72,88 %), `skills/multimedia.py` (74,55 %) y `skills/web.py` (75,0 %) usando mocking de dependencias de sistema.
**Cómo:** Dedicar 1 sprint (≈ 6–8 h) exclusivamente a cobertura; añadir *coverage gate* de 85 % por archivo en `pytest --cov-fail-under`.
**Métrica que mejorará:** Cobertura total (de 87,87 % → objetivo ≥ 92 %) y fiabilidad de detección.

---

### 🥉 Acción 3 — Refactorizar las 5 funciones de mayor CC
**Qué:** Aplicar *Extract Method* y *Replace Conditional with Polymorphism* en `_sintetizar` (CC=16), `_pronostico` (CC=16), `intentar` en apps_instaladas (CC=15), `intentar` en recordatorios (CC=14) y `resolver` (CC=13).
**Cómo:** Programar en el siguiente sprint de mantenimiento; verificar con `radon cc -n C` que el resultado es 0 funciones en rango C.
**Métrica que mejorará:** Índice de mantenibilidad (de 68,56 → objetivo ≥ 72) y complejidad ciclomática máxima (de 16 → ≤ 10).

---

### 4️⃣ Acción 4 — Reducir el MTTD mediante observabilidad en producción
**Qué:** Integrar logging estructurado (p. ej. `structlog`) con niveles diferenciados y un sistema de alertas (Sentry free tier o equivalente) que notifique errores no controlados en tiempo real.
**Cómo:** Instrumentar `cerebro.py`, `nucleo.py` y `servidor.py` con trazas de error; configurar alerta en < 15 min para excepciones no capturadas.
**Métrica que mejorará:** MTTD (de 14,51 días → objetivo < 2 días).

---

### 5️⃣ Acción 5 — Institucionalizar revisiones de código con checklist de calidad
**Qué:** Formalizar pull-request reviews con checklist basado en ISO/IEC 25010 (funcionalidad, seguridad, mantenibilidad) para elevar la eficacia de revisión actual del 13,64 % (3 de 22 defectos).
**Cómo:** Crear plantilla de PR en GitHub con checklist obligatorio; establecer mínimo 1 revisor aprobador; meta de detectar ≥ 25 % de defectos en fase de revisión.
**Métrica que mejorará:** Eficacia de revisión (de 13,64 % → objetivo ≥ 25 %) y densidad de defectos en producción.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas

| Técnica | Horas estimadas | Error vs. 122 h reales | Error % |
|---|---|---|---|
| Juicio de expertos (promedio) | 110,5 h | −11,5 h | −9,43 % |
| — Alumno desarrollador | 102,0 h | −20,0 h | −16,39 % |
| — IA (Claude) | 119,0 h | −3,0 h | **−2,46 %** |
| **PERT (valor central)** | **114,68 h** | **−7,32 h** | **−6,0 %** |
| PERT (rango 95 %, límite sup.) | 125,33 h | +3,33 h | +2,73 % |
| Puntos de función | 146,38 h | +24,38 h | +19,98 % |
| Analogía | 195,8 h | +73,8 h | +60,49 % |

### Veredicto

**La técnica más precisa fue el juicio experto de la IA (Claude), con apenas −3 h de desviación (−2,46 %)**, seguida de cerca por el límite superior del intervalo PERT al 95 % (+3,33 h). Esto se explica porque la IA analizó el código fuente módulo a módulo con contexto específico sobre la integración de APIs externas, superando al estimador humano (alumno) que subestimó sistemáticamente en módulos de alta integración como "Interfaz y servidor" (estimó 10 h, real 16 h) y "Núcleo de voz" (estimó 10 h, real 14 h).

El método **PERT** es el más recomendable para futuros proyectos similares: aunque su valor central (114,68 h) subestimó levemente, su intervalo al 95 % (104–125 h) **capturó las 122 h reales**, lo que lo hace robusto y transparente en la comunicación del riesgo de estimación. La analogía falló por el factor de ajuste conservador (+10 %) insuficiente para capturar la complejidad real de integración con múltiples APIs de IA, que debería haberse calibrado en al menos +50–60 %.

---

*Auditoría generada con base exclusiva en los datos del pipeline proporcionados. Ninguna cifra ha sido interpolada fuera del conjunto de datos.*
