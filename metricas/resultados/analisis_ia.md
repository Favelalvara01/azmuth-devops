## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-08 02:11

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **76 / 100**, posicionándose en un nivel de calidad *aceptable con reservas*. Las fortalezas son notables: 227/227 pruebas en verde, 0 defectos abiertos, análisis estático Ruff sin hallazgos y cobertura global del 85.28 %. Sin embargo, la **tasa de detección de defectos en pruebas (DRE 50 %)** y los **dos archivos con cobertura 0 %** representan riesgos residuales que deben mitigarse antes de una liberación a producción amplia; se recomienda **liberar en modo controlado (beta supervisada)** con un plan de mejora activo.

---

## Idoneidad funcional

| Sub-característica | Evidencia | Valoración |
|---|---|---|
| **Completitud funcional** | 227 casos de prueba cubren el 85.28 % del código ejecutable; 7 módulos de skills identificados y probados | ✅ Alta |
| **Corrección funcional** | 16 defectos totales, **0 abiertos**; densidad global de 5.77 defectos/KLOC | ✅ Alta |
| **Pertinencia funcional** | Skills de voz, recordatorios, multimedia, web, contactos, hábitos, sistema alineadas con el propósito declarado del asistente | ✅ Alta |

**Puntos de atención:**

- `app_desktop.py` y `skills/interfaz.py` tienen **cobertura 0 %**. Ninguna prueba automatizada valida la interfaz de usuario de escritorio. Si estas rutas de código son accesibles al usuario final, existe riesgo de defectos no detectados.
- `cerebro.py` alcanza solo **70.59 %** de cobertura, siendo el módulo cognitivo central del sistema.
- `voice.py` llega a **73.33 %**, crítico para un asistente de voz.
- La densidad de defectos del Sprint 1 (*Núcleo de voz*: 14.88/KLOC) y Sprint 5 (*Interfaz y servidor*: 7.89/KLOC) superan la media del proyecto, indicando mayor fragilidad en esas áreas.

---

## Fiabilidad

### Métricas clave del proceso

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** (Mean Time To Detect) | 262.18 h (≈ 10.9 días) | Detección tardía; la mayoría de defectos se descubren en producción |
| **MTTR** (Mean Time To Repair) | 4.37 h (262 min) | Corrección ágil una vez detectado el defecto |
| **DRE** (Defect Removal Effectiveness) | 50.0 % | Solo 1 de cada 2 defectos fue capturado antes de producción |
| **Defectos en producción** | 8 de 16 (50 %) | Proporción alta para un producto de voz con usuario final directo |
| **Defectos en pruebas** | 5 de 16 (31.25 %) | La cobertura existente captura menos de un tercio |
| **Defectos en revisión** | 3 de 16 (18.75 %) | Las revisiones de código aportan, pero tienen alcance limitado |

### Sub-características ISO/IEC 25010

| Sub-característica | Evidencia | Valoración |
|---|---|---|
| **Madurez** | 0 defectos abiertos; 16/16 reparados | ✅ Alta |
| **Disponibilidad** | Pipeline CI sin fallos; Docker garantiza entorno reproducible | ✅ Alta |
| **Tolerancia a fallos** | No hay datos de pruebas de caos o manejo de caídas de API (Claude, ElevenLabs) | ⚠️ No medida |
| **Recuperabilidad** | MTTR de 4.37 h indica recuperación rápida ante incidentes conocidos | ✅ Aceptable |

> **Riesgo latente:** El DRE del 50 % significa que el proceso de pruebas no está suficientemente maduro para garantizar que no existan defectos significativos no descubiertos. Los 4 defectos graves **ninguno fue detectado en pruebas** (graves detectados en pruebas = 0 / graves totales = 4), lo cual es el hallazgo de fiabilidad más crítico de este informe.

---

## Mantenibilidad

### Escala de complejidad ciclomática (McCabe)

| Rango | CC | Significado | Funciones en Azmuth | % |
|---|---|---|---|---|
| **A** | 1–5 | Código simple, bajo riesgo | 163 | 84.9 % |
| **B** | 6–10 | Moderada, manejable | 18 | 9.4 % |
| **C** | 11–15 | Alta, candidata a refactorización | 11 | 5.7 % |
| **D** | 16–20 | Muy alta, propensa a defectos | 0 | 0 % |
| **E** | 21–25 | Extrema | 0 | 0 % |
| **F** | > 25 | Caótica, ingobernables | 0 | 0 % |

**Promedio:** 3.39 (Rango A) · **Mediana:** 2.0 (Rango A) · **% A+B:** 94.27 %

El 94.27 % de las funciones se ubica en rangos A o B, lo que refleja una base de código **bien estructurada en general**. El índice de mantenibilidad promedio de **72.32** se considera aceptable (umbral recomendado ≥ 65).

### Funciones que requieren refactorización (Rango C)

| Prioridad | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 🔴 1 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | Extraer ramas de intención a funciones auxiliares |
| 🔴 2 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Separar lógica de creación/modificación/eliminación |
| 🔴 3 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | Aplicar tabla de despacho o patrón Strategy |
| 🔴 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | Dividir por tipo de acción multimedia |
| 🔴 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | Refactorizar con despacho por comando |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 136 | 12 | Simplificar condicionales anidados |
| 🟡 7 | `skills/memoria.py` | `intentar` | 61 | 12 | Extraer casos de memoria a métodos privados |
| 🟡 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 | Separar lógica de notificación y persistencia |
| 🟡 9 | `skills/web.py` | `intentar` | 53 | 12 | Separar búsqueda, navegación y scraping |
| 🟡 10 | `cerebro.py` | `preguntar` | 93 | 11 | Extraer manejo de contexto a clase propia |

> **Patrón detectado:** Las 11 funciones en rango C son principalmente métodos `intentar()` de skills. Este patrón sugiere que el contrato de la interfaz de skills obliga a centralizar demasiada lógica condicional. Evaluar introducir un despachador de intenciones o sub-handlers por acción.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (50 %): defectos graves llegan a producción sin detección previa** | Alta | Crítico | Diseñar casos de prueba específicos para los 4 defectos graves; implementar pruebas de mutación (p. ej. `mutmut`) para evaluar la calidad del suite |
| **Cobertura 0 % en `app_desktop.py` e `interfaz.py`**: funcionalidad de UI sin pruebas | Alta | Alto | Integrar pruebas de UI con `pytest-qt` o `pywinauto`; al menos smoke tests antes del siguiente release |
| **MTTD de ~11 días**: defectos permanecen ocultos demasiado tiempo | Media | Alto | Habilitar alertas automáticas de errores en runtime (logging estructurado + Sentry o similar) |
| **Dependencias de APIs externas (Claude, ElevenLabs) sin pruebas de resiliencia** | Media | Alto | Agregar mocks/stubs de las APIs y pruebas de fallback; implementar circuit breaker |
| **Desviación de estimación del 25 % global (60 % en Sprint 5)** | Media | Medio | Usar velocidad histórica (7.86 pts/sprint) y tres puntos para futuros sprints; agregar buffer del 15 % en módulos de integración |
| **11 funciones con CC rango C concentradas en skills**: mayor probabilidad de regresiones** | Media | Medio | Refactorizar las 5 funciones 🔴 antes del próximo ciclo de features; exigir CC ≤ 10 en nuevos PRs |
| **Núcleo de voz (`voice.py` 73 %, `cerebro.py` 70 %)** con cobertura insuficiente en el corazón del producto | Media | Alto | Elevar cobertura de ambos archivos al 85 % mínimo; priorizar ramas de manejo de errores de reconocimiento de voz |

---

## Plan de mejora

> Ordenado por impacto en calidad y urgencia. Horizonte sugerido: **próximos 2 sprints**.

### Acción 1 — Elevar el DRE mediante pruebas de los escenarios de defectos graves *(Prioridad: Crítica)*
**Qué hacer:** Analizar los 4 defectos graves históricos; escribir al menos 1 caso de prueba de regresión por cada uno. Añadir pruebas de mutación con `mutmut` o `cosmic-ray` para validar la efectividad del suite.
**Métrica que mejora:** DRE (objetivo: pasar de 50 % → ≥ 80 %) · Porcentaje de defectos detectados en pruebas vs. producción.

---

### Acción 2 — Cubrir `app_desktop.py`, `skills/interfaz.py`, `cerebro.py` y `voice.py` *(Prioridad: Alta)*
**Qué hacer:** Incorporar pruebas de integración y/o UI para los módulos con 0 % de cobertura. Para `cerebro.py` y `voice.py`, agregar pruebas unitarias de las ramas no cubiertas (manejo de excepciones, flujos alternativos).
**Métrica que mejora:** Cobertura total (objetivo: 85.28 % → ≥ 90 %) · Cobertura de `cerebro.py` (70 % → ≥ 85 %) · `voice.py` (73 % → ≥ 85 %).

---

### Acción 3 — Refactorizar las 5 funciones `intentar()` con CC ≥ 13 *(Prioridad: Alta)*
**Qué hacer:** Aplicar el patrón de despacho por tabla de comandos o sub-handlers en `apps_instaladas.intentar`, `recordatorios.intentar`, `multimedia.intentar`, `pestanas.intentar` y `apps_instaladas.resolver`. Definir una regla de linting que rechace CC > 10 en nuevos PRs (configurable en `ruff` o `flake8-cognitive-complexity`).
**Métrica que mejora:** Complejidad ciclomática máxima (15 → ≤ 10) · Índice de mantenibilidad promedio (72.32 → ≥ 78) · % funciones en rango A+B (94.27 % → ≥ 97 %).

---

### Acción 4 — Implementar resiliencia ante fallos de APIs externas *(Prioridad: Alta)*
**Qué hacer:** Agregar mocks de Claude y ElevenLabs en el suite de pruebas para simular timeouts, errores HTTP 429/503 y respuestas malformadas. Implementar un patrón *circuit breaker* (p. ej. con `pybreaker`) en los adaptadores de API. Agregar prueba de integración que verifique el modo degradado (respuesta local si la API no responde).
**Métrica que mejora:** Tolerancia a fallos (actualmente no medida → medible) · MTTR ante incidentes de API · Disponibilidad percibida por el usuario.

---

### Acción 5 — Instrumentar telemetría de errores en runtime para reducir MTTD *(Prioridad: Media)*
**Qué hacer:** Integrar logging estructurado (p. ej. `structlog`) y una herramienta de rastreo de errores (Sentry OSS o similar) con alertas automáticas. Definir un SLO de MTTD objetivo (p. ej. ≤ 48 h). Revisar y fortalecer el proceso de revisión de código (actualmente captura solo el 18.75 % de defectos).
**Métrica que mejora:** MTTD (262 h → objetivo ≤ 48 h) · Eficacia de revisión (18.75 % → ≥ 30 %) · Visibilidad de defectos en producción.

---

## Estimación (juicio experto de la IA)

### Comparativa contra las 90 horas reales

| Técnica | Total estimado (h) | Error absoluto | Error relativo |
|---|---|---|---|
| Juicio de expertos (promedio) | 80.33 | 9.67 h | 10.7 % |
| **Tres puntos — PERT** | **81.85** | **8.15 h** | **9.1 %** |
| Puntos de función | 101.12 | 11.12 h | 12.4 % |
| Análoga | 135.57 | 45.57 h | 50.6 % |
| Alumno desarrollador (juicio individual) | 72.00 | 18.00 h | 20.0 % |

### Técnica más cercana: **Tres puntos (PERT) — 81.85 h**

La estimación por **tres puntos PERT** fue la que mejor aproximó las 90 horas reales, con un error del **9.1 %** y, lo más relevante, las 90 horas reales caen **dentro del rango de confianza del 95 % calculado [72.26 h – 91.44 h]**, lo que valida la técnica estadísticamente.

**¿Por qué funcionó mejor?**

1. **Captura la incertidumbre explícitamente.** Al requerir estimaciones optimista (O), más probable (M) y pesimista (P) por módulo, obligó al equipo a razonar sobre los riesgos de cada componente, algo especialmente valioso en un proyecto con integraciones externas novedosas (Claude, ElevenLabs).

2. **Compensó sesgos individuales.** El alumno developer subestimó sistemáticamente (72 h, -20 %); los valores pesimistas del PERT corrigieron ese sesgo optimista sin caer en el exceso de la estimación análoga.

3. **La estimación análoga falló significativamente (+50.6 %)** porque el proyecto de referencia (*Easy Learning*, CRUD en C#) no es comparable en complejidad arquitectural: Azmuth integra reconocimiento de voz, síntesis, LLMs y automatización del SO, dominios que el factor de ajuste del +10 % subestimó considerablemente.

4. **Puntos de función** sobreestimaron (+12.4 %) probablemente porque el modelo de productividad de 0.45 h/PF no estaba calibrado para el stack Python del equipo ni para la curva de aprendizaje de las APIs de voz.

**Recomendación:** En futuros proyectos del mismo equipo, usar **tres puntos como técnica primaria** y calibrar el coeficiente de productividad de puntos de función con al menos 2 proyectos históricos propios antes de usarlos como referencia.

---

*Informe generado automáticamente con base en los datos del pipeline. Todos los valores numéricos provienen exclusivamente de las métricas suministradas.*
