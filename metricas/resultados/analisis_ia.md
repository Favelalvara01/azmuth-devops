## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-08 13:49**

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **76 / 100**, posicionándose en un nivel de calidad **aceptable con observaciones**. Sus fortalezas son la cobertura de pruebas (86.58 %), la complejidad ciclomática mayoritariamente baja (94.39 % en rangos A-B) y la ausencia total de defectos abiertos al cierre. **El proyecto puede liberarse condicionalmente**, sujeto al plan de mejora en la Tasa de Detección de Defectos en pruebas (DRE 44.44 %) y a la cobertura crítica de `app_desktop.py` (0 %), que representan los dos riesgos de mayor peso antes de un despliegue amplio.

---

## Idoneidad funcional

### Completitud funcional
- **315 pruebas ejecutadas, 315 aprobadas (100 % de paso)**, con 0 fallos y 0 *xfail* pendientes, lo que indica que las funcionalidades especificadas tienen respaldo de prueba en su gran mayoría.
- 34 de 35 archivos tienen cobertura > 0 %, sugiriendo que casi todo el código declarado está contemplado en el alcance de prueba.

### Corrección funcional
- **0 defectos abiertos** sobre 18 históricos totales: todos los defectos encontrados han sido corregidos.
- La densidad de defectos global es **5.77 defectos/KLOC**; el módulo más problemático fue *Interfaz y servidor* (Sprint 5, 9.42/KLOC) seguido de *Núcleo de voz* (Sprint 1, 13.74/KLOC). Estos módulos requieren vigilancia en futuros sprints.

### Pertinencia funcional
- El análisis estático con **Ruff** no reportó ningún hallazgo (`All checks passed!`), indicando que el código implementado se alinea con las convenciones del lenguaje y no contiene construcciones superfluas o erróneas detectables estáticamente.
- La velocidad de **7.45 puntos/sprint** es consistente a lo largo de 11 sprints, señal de que el equipo entregó de forma predecible.

**Valoración: 80/100** — Funcionalidad completa y correcta al cierre; penalización por DRE bajo y cobertura nula en `app_desktop.py`.

---

## Fiabilidad

### Métricas clave

| Indicador | Valor | Interpretación |
|---|---|---|
| MTTD | 233.09 h (9.71 días) | Los defectos tardan casi 10 días en descubrirse; detección lenta |
| MTTR | 3.9 h (234 min) | Una vez detectado, la reparación es ágil |
| DRE (fase pruebas) | **44.44 %** | Solo 4 de 9 defectos preproducción fueron capturados en pruebas |
| Defectos en producción | 10 / 18 (55.56 %) | Más de la mitad escaparon al entorno productivo |
| Tasa pruebas vs producción | 33.33 % | 1 de cada 3 defectos detectados apareció en la fase de pruebas |

### Madurez
Con 0 defectos abiertos y un historial de 18 defectos ya cerrados, el sistema está en un estado maduro al momento del cierre. Sin embargo, el elevado MTTD indica que la suite de pruebas no está configurada para detectar defectos en etapas tempranas.

### Disponibilidad
No se dispone de datos de tiempo de inactividad en producción, pero el MTTR de 3.9 h sugiere que, ante una incidencia, el equipo puede restablecer el servicio en menos de una jornada laboral: comportamiento adecuado para un asistente personal.

### Tolerancia a fallos y recuperabilidad
- La cobertura de `voice.py` (72.88 %) y `skills/multimedia.py` (74.07 %) son las más bajas entre los archivos con lógica crítica, lo que expone rutas de fallo ante entradas de voz inesperadas.
- `cerebro.py` al 75 % cubre parcialmente la lógica de decisión central del asistente, riesgo potencial ante escenarios no contemplados.

**Valoración: 68/100** — MTTR excelente, pero DRE insuficiente y MTTD elevado reducen significativamente la fiabilidad preventiva.

---

## Mantenibilidad

### Escala de complejidad ciclomática (McCabe)

| Rango | CC | Significado | Funciones | % |
|---|---|---|---|---|
| **A** | 1–5 | Muy simple, sin riesgo | 180 | 84.11 % |
| **B** | 6–10 | Moderada, riesgo bajo | 22 | 10.28 % |
| **C** | 11–15 | Compleja, riesgo medio | 12 | 5.61 % |
| **D** | 16–20 | Alta complejidad | 0 | 0 % |
| **E** | 21–25 | Muy alta | 0 | 0 % |
| **F** | > 25 | Imposible de mantener | 0 | 0 % |

- **Promedio: 3.44 (Rango A)** — salud general muy buena.
- **Mediana: 2.0** — la función típica es trivial.
- **Índice de mantenibilidad promedio: 72.02 / 100** — nivel aceptable, con margen de mejora.

### Funciones a refactorizar (Rango C — prioridad decreciente)

| Prioridad | Archivo | Función | Línea | CC |
|---|---|---|---|---|
| 1 | `skills/apps_instaladas.py` | `intentar` | 213 | **15** |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | **14** |
| 3 | `skills/apps_instaladas.py` | `resolver` | 169 | **13** |
| 4 | `skills/multimedia.py` | `intentar` | 31 | **13** |
| 5 | `skills/pestanas.py` | `intentar` | 33 | **13** |
| 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 205 | **12** |
| 7 | `skills/memoria.py` | `intentar` | 61 | **12** |
| 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | **12** |
| 9 | `skills/web.py` | `intentar` | 53 | **12** |
| 10 | `cerebro.py` | `preguntar` | 104 | **11** |

> **Patrón detectado:** El nombre `intentar` aparece en 5 archivos distintos con alta complejidad. Esto sugiere que existe una lógica de manejo de intentos/reintentos que no está centralizada — candidata natural para un *template method* o un decorador de reintentos reutilizable.

**Valoración: 78/100** — Sin funciones en rangos D-F; el patrón repetido en `intentar` y la mantenibilidad de 72 impiden una nota más alta.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (44.44 %)**: defectos escapan a producción | Alta | Alto | Ampliar casos de prueba en módulos críticos; implementar pruebas de regresión automáticas por cada bug cerrado |
| **Cobertura 0 % en `app_desktop.py`** | Alta | Alto | Crear suite de pruebas de integración/UI; usar mocking de la interfaz gráfica (ej. `pytest-qt`) |
| **MTTD de 9.71 días**: detección tardía de defectos | Alta | Medio | Habilitar monitoreo activo de errores en producción (ej. Sentry) y alertas automáticas |
| **Cobertura < 80 % en módulos de voz** (`voice.py` 72.88 %, `multimedia.py` 74.07 %) | Media | Alto | Añadir pruebas con audio simulado y mocks de API de voz (ElevenLabs, STT) |
| **Complejidad CC=15 en `apps_instaladas.intentar`** | Media | Medio | Refactorizar con estrategia de extracción de métodos antes del próximo sprint de nuevas funciones |
| **Desviación del 60 % en Sprint 5** (Interfaz y servidor) | Media | Medio | Aplicar estimación por 3 puntos con percentil 85 % para módulos de integración UI/red |
| **10 defectos llegaron a producción** (55.56 %) | Baja (ya ocurrió) | Medio | Establecer *Definition of Done* que exija DRE ≥ 80 % antes de cualquier release |

---

## Plan de mejora

Las acciones están ordenadas por impacto en la calidad del producto; cada una incluye la métrica ISO/IEC 25023 que mejora.

---

**Acción 1 — Cobertura crítica en `app_desktop.py` y módulos de voz** *(Prioridad: Urgente)*

Crear pruebas unitarias e integración para `app_desktop.py` (actualmente 0 %) y elevar `voice.py` y `skills/multimedia.py` por encima del 80 %. Usar mocks para las APIs externas (ElevenLabs, motor STT).

- 📈 Métrica mejorada: **Cobertura de pruebas** → objetivo ≥ 85 % en todos los archivos; **DRE** → objetivo ≥ 70 %.

---

**Acción 2 — Reducir el MTTD mediante monitoreo en producción** *(Prioridad: Alta)*

Integrar una herramienta de seguimiento de errores en tiempo real (Sentry o equivalente) con alertas al repositorio GitHub. Establecer un SLA interno de notificación ≤ 24 h.

- 📈 Métrica mejorada: **MTTD** → reducir de 233 h a < 48 h; mejora directa en **Disponibilidad** y **Madurez**.

---

**Acción 3 — Refactorizar las 5 funciones `intentar` de rango C** *(Prioridad: Alta)*

Extraer la lógica de reintentos/dispatch a un decorador o clase base `SkillBase.intentar()`, reduciendo CC de cada función a rango A-B. Ejecutar *refactor sprint* de 4-6 h antes de nuevas funcionalidades.

- 📈 Métrica mejorada: **Complejidad ciclomática máxima** → bajar de 15 a ≤ 10; **Índice de mantenibilidad** → objetivo > 80.

---

**Acción 4 — Elevar la eficacia de revisiones (DRE de fase revisión)** *(Prioridad: Media)*

La eficacia de revisión fue solo 16.67 % (3/18 defectos). Implementar *checklist* de revisión de código estructurado (pair review o revisiones formales de 30 min por PR), con foco en los módulos de mayor densidad (núcleo de voz: 13.74/KLOC, interfaz: 9.42/KLOC).

- 📈 Métrica mejorada: **DRE global** → objetivo ≥ 75 %; **Densidad de defectos** en módulos críticos → objetivo < 5/KLOC.

---

**Acción 5 — Mejorar precisión de estimación en módulos de integración** *(Prioridad: Media)*

Los sprints 1 (40 % desviación) y 5 (60 % desviación) involucraron APIs externas e interfaz. Para futuros módulos similares, usar **estimación por 3 puntos con percentil 85 %** como estimación oficial, en lugar del valor medio.

- 📈 Métrica mejorada: **Desviación de estimación** → reducir de 19.61 % a < 10 %; mejora indirecta en **velocidad de puntos por sprint** (predictibilidad).

---

## Estimación — Juicio experto de la IA

### Resumen comparativo

| Técnica | Horas estimadas | Horas reales | Error absoluto | Error % |
|---|---|---|---|---|
| Juicio experto — Alumno | 102.0 | 122.0 | 20.0 h | 16.39 % |
| Juicio experto — IA (Claude) | 119.0 | 122.0 | **3.0 h** | **2.46 %** |
| Juicio experto — Promedio | 110.5 | 122.0 | 11.5 h | 9.43 % |
| **Tres Puntos (PERT)** | **114.68** | 122.0 | **7.32 h** | **6.00 %** | 
| Puntos de Función | 146.38 | 122.0 | 24.38 h | 19.98 % |
| Analogía | 152.53 | 122.0 | 30.53 h | 25.02 % |

### Análisis

La técnica que se acercó más a las **122 horas reales** fue el **juicio experto individual de la IA (Claude)**, con solo **3 horas de error (2.46 %)**. Esto no es coincidencia: la IA analizó el código fuente real módulo a módulo, lo que le permitió calibrar la complejidad integración con APIs externas de forma más precisa que una estimación basada en puntos de historia o en un proyecto análogo de distinta tecnología.

En segundo lugar más precisa estuvo la **estimación por tres puntos (PERT)** con 6 % de error. Esta técnica incorporó explícitamente la incertidumbre mediante escenarios pesimistas (P), y el rango al 95 % **[104 h – 125 h] sí contenía las 122 horas reales**, lo que la hace la técnica más **estadísticamente confiable y trazable** para futuros proyectos.

> **Recomendación:** Combinar ambas técnicas: usar el **juicio de la IA sobre el código** como estimación de referencia puntual y la **distribución PERT** para comunicar rangos de incertidumbre a stakeholders. Las técnicas de **analogía** y **puntos de función** sobreestimaron considerablemente porque no capturaron la alta productividad del equipo ni la reutilización de componentes entre sprints.

---

*Auditoría generada con base exclusiva en los datos del pipeline — ISO/IEC 25010:2023 · ISO/IEC 25023:2016*
