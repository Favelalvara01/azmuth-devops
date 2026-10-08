## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto *Azmuth*
**ISO/IEC 25010 · ISO/IEC 25023 | Fecha de datos: 2026-10-08**

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **74 / 100**. Las fortalezas son notables: suite de pruebas al 100 % de tasa de éxito (339/339), cobertura del 87,37 %, cero defectos abiertos y análisis estático limpio (Ruff). Sin embargo, la **Eficacia de Detección en Revisiones (DRE del 44,44 %)**, el alto MTTD de 9,71 días y la desviación de esfuerzo del 19,61 % respecto a lo estimado impiden un dictamen de liberación sin condiciones; se recomienda **liberación condicionada** a la ejecución de las acciones de mejora de alta prioridad descritas en este informe.

---

## Idoneidad funcional

| Subcaracterística | Evidencia | Valoración |
|---|---|---|
| **Completitud funcional** | 339 pruebas aprobadas; 0 fallidas; 0 xfail. 37 archivos cubren núcleo, skills, IA, persistencia, servidor y DevOps. | ✅ Alta |
| **Corrección funcional** | 18 defectos totales, **0 abiertos** (0,0 por KLOC abiertos). Densidad total: 5,43/KLOC, aceptable para un proyecto de esta complejidad. | ✅ Satisfactoria |
| **Pertinencia funcional** | Las skills cubren voz, multimedia, recordatorios, hábitos, memoria, web, sistema y escritorio: alcance coherente con un asistente de voz IA para Windows. | ✅ Pertinente |

> **Punto de atención:** `app_desktop.py` tiene cobertura **0,0 %**, lo que significa que ninguna prueba automatizada valida la capa de interfaz de escritorio. Aunque no hay defectos abiertos allí (1 defecto ya cerrado), existe riesgo latente de regresiones no detectadas.

---

## Fiabilidad

### Métricas clave

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** (Mean Time To Detect) | 233,09 h (9,71 días) | Detección tardía: indica que los defectos permanecen demasiado tiempo sin ser identificados antes de cerrarse. |
| **MTTR** (Mean Time To Repair) | 3,9 h (234 min) | Excelente capacidad de reparación; el equipo resuelve defectos con rapidez una vez detectados. |
| **DRE** (Defect Removal Effectiveness) | 44,44 % | Crítico. Menos de la mitad de los defectos se detectaron antes de producción. El ideal es ≥ 85 %. |
| Defectos en producción | 10 de 18 (55,56 %) | La mayoría de defectos escaparon a producción, lo que compromete la madurez del proceso. |
| Defectos en pruebas | 5 de 18 (27,78 %) | Las pruebas automatizadas capturaron solo un tercio de los defectos frente a producción. |

### Subcaracterísticas

| Subcaracterística | Evaluación |
|---|---|
| **Madurez** | Media-baja: DRE del 44 % y 55 % de defectos en producción señalan que el producto llega a producción con riesgo residual importante. |
| **Disponibilidad** | No se reportan tiempos de caída del servicio; la existencia de `monitoreo.py` (88,89 % cobertura) y `servidor.py` (95,57 %) es positiva. |
| **Tolerancia a fallos** | No hay datos explícitos de pruebas de caos o inyección de fallos. La cobertura de `voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %) deja casos de error sin validar. |
| **Recuperabilidad** | El MTTR de 3,9 h es bueno: el equipo puede restaurar la funcionalidad rápidamente. |

---

## Mantenibilidad

### Índice de mantenibilidad

El **índice promedio de 70,9 / 100** se sitúa en un nivel **aceptable** (umbral de alerta < 65), aunque con margen de mejora antes de alcanzar la zona cómoda (≥ 80).

### Distribución de complejidad ciclomática

| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Riesgo bajo | 197 | 83,1 % |
| **B** (6–10) | Riesgo moderado | 29 | 12,2 % |
| **C** (11–15) | Riesgo alto — **refactorizar** | 11 | 4,6 % |
| D–F | Riesgo muy alto / inaceptable | 0 | 0,0 % |

El **95,36 % de las funciones están en rango A o B**, lo que es positivo. Sin embargo, las 11 funciones en rango **C** concentran el mayor riesgo de mantenibilidad.

### Funciones prioritarias a refactorizar

| Prioridad | Archivo | Función | Línea | CC |
|---|---|---|---|---|
| 1 | `skills/apps_instaladas.py` | `intentar` | 210 | **15** |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | **14** |
| 3 | `skills/apps_instaladas.py` | `resolver` | 166 | **13** |
| 4 | `skills/multimedia.py` | `intentar` | 31 | **13** |
| 5 | `skills/pestanas.py` | `intentar` | 33 | **13** |
| 6 | `groq_ia.py` | `completar` | 85 | **12** |
| 7 | `skills/memoria.py` | `intentar` | 61 | **12** |
| 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | **12** |
| 9 | `skills/web.py` | `intentar` | 53 | **12** |
| 10 | `skills/habitos.py` | `sugerir_por_hora` | 98 | **11** |

> **Patrón detectado:** el nombre `intentar` aparece en 5 de los 10 módulos más complejos, lo que sugiere que este patrón de función monolítica concentra demasiada lógica de despacho/control. Aplicar el principio de responsabilidad única y tablas de despacho reduciría la CC significativamente.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (44 %)**: defectos escapan a producción sin ser detectados en pruebas | Alta | Alto | Ampliar pruebas de integración y de borde; implementar mutation testing para medir la calidad real del conjunto de pruebas. |
| **`app_desktop.py` con 0 % de cobertura** | Alta | Alto | Crear pruebas unitarias/UI para la capa de escritorio antes de la próxima liberación. |
| **MTTD elevado (9,71 días)**: los defectos tardan demasiado en detectarse | Alta | Medio | Activar monitoreo continuo con alertas automáticas y revisar los criterios de aceptación por sprint. |
| **11 funciones en rango C de complejidad ciclomática** | Media | Medio | Refactorizar las 10 funciones listadas; agregar una regla de gate en el pipeline (CC > 10 → fallo de build). |
| **Desviación de esfuerzo del 19,61 %** (especialmente Sprint 5: +60 %, Sprint 1: +40 %) | Media | Medio | Usar la velocidad histórica (7,45 pts/sprint) y el rango 95 % de tres puntos (104–125 h) como base para futuros proyectos; incorporar buffer de riesgo explícito. |
| **`voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %)** con cobertura baja en módulos críticos de voz | Media | Alto | Incrementar cobertura a ≥ 85 % con pruebas de rutas de error (timeouts de API, dispositivo no disponible). |
| **10 de 18 defectos en producción** evidencian proceso de QA insuficiente antes del release | Alta | Alto | Establecer Definition of Done que incluya umbral mínimo de DRE ≥ 75 % medido por fase antes de cada despliegue. |

---

## Plan de mejora

Las acciones están ordenadas por impacto/urgencia:

### 🔴 Prioridad 1 — Crear pruebas para `app_desktop.py`
- **Acción:** Desarrollar al menos 15 casos de prueba para la capa de escritorio, cubriendo inicio, cierre, interacción con el nucleo de voz y manejo de errores de GUI.
- **Métrica que mejora:** Cobertura total (de 87,37 % → meta ≥ 90 %) y DRE (se agregan casos que habrían capturado el defecto registrado en ese archivo).

### 🔴 Prioridad 2 — Implementar *mutation testing* para elevar el DRE
- **Acción:** Integrar `mutmut` o `cosmic-ray` en el pipeline de GitHub Actions. Establecer un umbral mínimo de *mutation score* del 70 % como gate de calidad.
- **Métrica que mejora:** DRE (de 44,44 % → meta ≥ 75 %); reducción de defectos que escapan a producción.

### 🟠 Prioridad 3 — Refactorizar las 5 funciones `intentar` de mayor CC
- **Acción:** Descomponer cada función `intentar` (CC ≥ 12) en sub-funciones de responsabilidad única. Aplicar tabla de despacho o patrón *Command* para reducir ramificaciones.
- **Métrica que mejora:** Complejidad ciclomática máxima (de 15 → meta ≤ 10); índice de mantenibilidad (de 70,9 → meta ≥ 78).

### 🟠 Prioridad 4 — Reducir el MTTD mediante alertas de monitoreo continuo
- **Acción:** Configurar alertas automáticas en `monitoreo.py` con notificación inmediata ante excepciones no controladas; añadir Sentry o equivalente al pipeline de producción.
- **Métrica que mejora:** MTTD (de 9,71 días → meta ≤ 3 días); madurez del proceso.

### 🟡 Prioridad 5 — Elevar cobertura de `voice.py` y `skills/multimedia.py` al 85 %
- **Acción:** Agregar pruebas parametrizadas que simulen fallos de dispositivo de audio, timeouts de API de síntesis de voz y formatos multimedia no soportados (usar `unittest.mock` o `pytest-mock`).
- **Métrica que mejora:** Cobertura de `voice.py` (72,88 % → ≥ 85 %) y `skills/multimedia.py` (74,07 % → ≥ 85 %); tolerancia a fallos del sistema de voz.

---

## Estimación (juicio experto de la IA)

### Comparación de técnicas frente a las 122 horas reales

| Técnica | Total estimado | Error absoluto | Error % |
|---|---|---|---|
| Juicio de expertos (promedio) | 110,5 h | 11,5 h | 9,43 % |
| **Tres puntos — PERT** | **114,68 h** | **7,32 h** | **5,97 %** |
| Puntos de función | 146,38 h | 24,38 h | 19,98 % |
| Análoga | 161,92 h | 39,92 h | 32,72 % |

### Técnica más acertada: **Tres Puntos (PERT)**

La estimación por tres puntos PERT fue la que más se aproximó a las 122 horas reales, con un error de solo **7,32 h (5,97 %)**. Además, el rango del 95 % calculado fue **104,03 – 125,33 h**, y las 122 horas reales caen **dentro de ese intervalo de confianza**, lo que valida la técnica estadísticamente.

**¿Por qué funcionó mejor?**

1. **Captura la asimetría del riesgo.** Al solicitar explícitamente un escenario optimista (O), uno más probable (M) y uno pesimista (P) por módulo, la fórmula PERT penaliza los casos optimistas y modera los pesimistas, reflejo real de lo ocurrido en sprints como el 5 (Interfaz y servidor: estimado 10 h, real 16 h) y el 1 (Núcleo de voz: estimado 10 h, real 14 h).

2. **La estimación análoga sobreestimó** porque el factor de ajuste de 1,1 resultó insuficiente para capturar la complejidad real de integrar APIs de voz e IA (3,31 KLOC vs. 1,8 KLOC de referencia implica casi el doble de líneas, pero con arquitectura distinta).

3. **Los puntos de función sobreestimaron** en parte porque la productividad asumida (0,45 h/PF) puede no ajustarse perfectamente al stack Python + APIs externas de este proyecto específico.

4. **El juicio de expertos estuvo cerca**, pero el alumno desarrollador subestimó sistemáticamente (especialmente en los sprints de mayor novedad técnica), lo que arrastró el promedio hacia abajo. La IA como segundo experto compensó parcialmente, elevando el promedio global a 110,5 h, todavía 11,5 h por debajo de la realidad.

**Recomendación:** Para proyectos futuros similares (asistente de voz, integración de APIs externas), usar **Tres Puntos PERT como técnica base**, complementado con la velocidad histórica medida (7,45 pts/sprint y ~1,5 h/punto promedio ponderado) para validar la coherencia del resultado.
