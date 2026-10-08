## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-08

---

## Dictamen general

El proyecto Azmuth alcanza una calificación de **78 / 100**, sustentada en una cobertura de pruebas del 86.58 %, cero defectos abiertos al cierre y un análisis estático Ruff sin hallazgos. Sin embargo, la baja eficacia de detección en pruebas (DRE = 44.44 %) y la cobertura nula de `app_desktop.py` representan riesgos residuales que deben mitigarse antes de una liberación en producción amplia; **se recomienda liberación condicionada** a la resolución de las acciones del plan de mejora de prioridad alta.

---

## Idoneidad funcional

| Sub-característica | Indicador | Valor | Interpretación |
|---|---|---|---|
| **Completitud funcional** | Pruebas aprobadas / total | 315/315 (100 %) | Todos los casos de prueba definidos pasan; ningún xfail registrado |
| **Corrección funcional** | Defectos abiertos | **0** | Sin deuda de defectos al momento de la auditoría |
| **Corrección funcional** | Densidad total de defectos | 5.77 / KLOC | Aceptable para un asistente de voz con integraciones externas |
| **Pertinencia funcional** | Distribución de defectos por fase | 10 en producción (55.6 %) | Preocupante: más de la mitad se detectaron en producción |
| **Cobertura de casos** | Archivos con cobertura < 80 % | 3 (`app_desktop.py` 0 %, `voice.py` 72.88 %, `skills/multimedia.py` 74.07 %) | Riesgo funcional en componentes de UI y multimedia |

**Conclusión:** La completitud y corrección son satisfactorias en el estado actual, pero la pertinencia se ve cuestionada por el alto porcentaje de defectos escapados a producción, señal de que las pruebas no cubren adecuadamente los flujos de usuario reales.

---

## Fiabilidad

| Sub-característica | Métrica | Valor | Interpretación |
|---|---|---|---|
| **Madurez** | DRE (Defect Removal Efficiency) | **44.44 %** | Crítico: sólo 4 de 9 defectos pre-entrega se capturaron antes de producción; estándar aceptable ≥ 85 % |
| **Madurez** | Defectos detectados en revisión | 3/18 (16.67 %) | El proceso de revisión de código aporta poco al filtrado |
| **Disponibilidad** | Pruebas aprobadas continuas (CI) | 315/315 | El pipeline no reporta regresiones; disponibilidad de build = 100 % |
| **Tolerancia a fallos** | Cobertura global | 86.58 % | Moderada-alta; los módulos críticos de voz y UI tienen cobertura insuficiente |
| **Recuperabilidad** | MTTR | **3.9 h (234 min)** | Excelente; los defectos se cierran rápidamente una vez identificados |
| **Madurez** | MTTD | **233.09 h (9.71 días)** | Elevado; los defectos tardan ~10 días en detectarse, lo que explica el volumen escapado a producción |

**Análisis MTTD/MTTR:** La combinación de MTTD alto (9.71 días) y MTTR bajo (3.9 h) indica que el equipo resuelve defectos con eficiencia una vez los encuentra, pero el sistema de detección es el cuello de botella crítico. Un DRE del 44.44 % está muy por debajo del umbral recomendado (≥ 85 %), lo que supone el principal riesgo de fiabilidad del producto.

---

## Mantenibilidad

**Índice de mantenibilidad promedio: 72.02 / 100** — Calificación: **Moderada** (umbral recomendado ≥ 80).

### Distribución de complejidad ciclomática

| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Simple, sin riesgo | 180 | 84.11 % |
| **B** (6–10) | Moderada, manejable | 22 | 10.28 % |
| **C** (11–15) | Compleja, refactorizar | 12 | 5.61 % |
| **D** (16–20) | Alta, riesgo de defectos | 0 | 0 % |
| **E** (21–25) | Muy alta | 0 | 0 % |
| **F** (> 25) | Inaceptable | 0 | 0 % |

El 94.39 % de las funciones está en rangos A–B, lo cual es positivo. No obstante, las **12 funciones en rango C** concentran el riesgo de mantenibilidad.

### Funciones prioritarias a refactorizar (rango C)

| Prioridad | Archivo | Función | Línea | Complejidad | Acción sugerida |
|---|---|---|---|---|---|
| 🔴 1 | `skills/apps_instaladas.py` | `intentar` | 213 | **15** | Extraer sub-funciones por tipo de acción |
| 🔴 2 | `skills/recordatorios.py` | `intentar` | 96 | **14** | Aplicar patrón Strategy o tabla de despacho |
| 🔴 3 | `skills/apps_instaladas.py` | `resolver` | 169 | **13** | Dividir en funciones de resolución específicas |
| 🔴 4 | `skills/multimedia.py` | `intentar` | 31 | **13** | Separar manejo de audio/video/imagen |
| 🔴 5 | `skills/pestanas.py` | `intentar` | 33 | **13** | Reducir anidamiento con early returns |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 205 | **12** | Delegar lógica condicional a funciones auxiliares |
| 🟡 7 | `skills/memoria.py` | `intentar` | 61 | **12** | Aplicar tabla de despacho por intención |
| 🟡 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | **12** | Separar revisión de notificación |
| 🟡 9 | `skills/web.py` | `intentar` | 53 | **12** | Extraer por tipo de búsqueda/navegación |
| 🟡 10 | `cerebro.py` | `preguntar` | 104 | **11** | Simplificar lógica de selección de respuesta |

> **Nota:** El patrón recurrente `intentar` en múltiples skills sugiere que la interfaz de skills necesita una abstracción común que reduzca la lógica de despacho dentro de cada implementación.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| DRE bajo (44.44 %): defectos graves escapan a producción | **Alta** | **Crítico** | Implementar pruebas de integración end-to-end y revisiones de código estructuradas con checklist; establecer umbral mínimo de DRE = 75 % como gate de release |
| `app_desktop.py` sin cobertura (0 %) | **Alta** | **Alto** | Añadir suite de pruebas de UI (p. ej. con `pytest-qt` o automatización de escritorio); bloquear merge si cobertura del archivo < 50 % |
| MTTD elevado (9.71 días) | **Alta** | **Alto** | Ampliar monitoreo en producción con alertas automáticas (logging estructurado + Sentry o equivalente) |
| `voice.py` y `skills/multimedia.py` con cobertura < 75 % | **Media** | **Alto** | Crear mocks de dispositivos de audio/vídeo para pruebas unitarias de estos módulos |
| Funciones C en `cerebro.py` | **Media** | **Medio** | Refactorizar `actualizar_perfil_si_toca` y `preguntar` antes del siguiente sprint; añadir pruebas de regresión específicas |
| Densidad de defectos alta en Sprint 1 (13.74/KLOC) y Sprint 5 (9.42/KLOC) | **Media** | **Medio** | Aplicar revisión de código más exhaustiva en módulos de voz e interfaz; incrementar cobertura de `main.py` (actualmente 90.81 % con 4 defectos históricos) |
| Desviación de estimación del 19.61 % (20 h extra) | **Baja** | **Medio** | Usar estimación por tres puntos (PERT) como técnica principal en proyectos futuros; incorporar buffer de contingencia del 15 % |
| Dependencias externas (Claude API, ElevenLabs) sin pruebas de contrato | **Media** | **Alto** | Implementar pruebas de contrato con mocks de API; definir timeouts y circuit breakers |

---

## Plan de mejora

Las siguientes acciones se presentan en orden de prioridad descendente, considerando el riesgo mitigado y el esfuerzo requerido.

---

### 🔴 Acción 1 — Elevar la eficacia de detección de defectos (DRE)
**Prioridad: Crítica | Esfuerzo estimado: 8–10 h**

Diseñar e implementar pruebas de integración que simulen flujos de usuario completos (voz → skill → respuesta), cubriendo los 4 defectos graves que actualmente no se detectan antes de producción. Establecer en el pipeline de CI un gate que bloquee el merge si `DRE < 75 %` (calculado mediante comparación de defectos en rama vs. producción histórica).

- **Métrica que mejora:** DRE: de 44.44 % → objetivo ≥ 75 %
- **Métrica secundaria:** `defectos_por_fase.produccion`: reducir de 10 a ≤ 4 en el siguiente ciclo

---

### 🔴 Acción 2 — Cubrir `app_desktop.py`, `voice.py` y `skills/multimedia.py`
**Prioridad: Alta | Esfuerzo estimado: 6–8 h**

Crear mocks de dispositivos de audio, síntesis de voz y ventana de escritorio para hacer testeable estos módulos sin hardware real. Añadir suite mínima de 15 casos de prueba distribuidos entre los tres archivos.

- **Métrica que mejora:** Cobertura global: de 86.58 % → objetivo ≥ 90 %; cobertura de `app_desktop.py`: de 0 % → ≥ 60 %
- **Métrica secundaria:** MTTD reducido al detectar defectos en CI antes de producción

---

### 🟠 Acción 3 — Refactorizar las 5 funciones de mayor complejidad ciclomática
**Prioridad: Alta | Esfuerzo estimado: 5–7 h**

Aplicar el patrón **tabla de despacho** (diccionario de intención → función) en las funciones `intentar` de `apps_instaladas.py`, `recordatorios.py`, `multimedia.py`, `pestanas.py` y `web.py`. Cada función debe quedar con complejidad ≤ 7 (rango B).

- **Métrica que mejora:** Complejidad máxima: de 15 → ≤ 7; `porcentaje_A_B`: de 94.39 % → ≥ 97 %
- **Métrica secundaria:** Índice de mantenibilidad promedio: de 72.02 → objetivo ≥ 80

---

### 🟠 Acción 4 — Reducir MTTD con monitoreo y alertas en producción
**Prioridad: Media-Alta | Esfuerzo estimado: 4–5 h**

Integrar logging estructurado (JSON) y conectar con una herramienta de monitoreo de errores (Sentry OSS o equivalente). Definir alertas automáticas para excepciones no controladas en el módulo de voz y en las integraciones con APIs externas (Claude, ElevenLabs).

- **Métrica que mejora:** MTTD: de 9.71 días → objetivo ≤ 3 días
- **Métrica secundaria:** Tiempo de respuesta ante fallos de API externa (actualmente sin medición)

---

### 🟡 Acción 5 — Fortalecer el proceso de revisión de código
**Prioridad: Media | Esfuerzo estimado: 2–3 h (setup) + práctica continua**

Crear un **checklist de revisión estructurada** en el repositorio (PR template) que incluya verificación de: manejo de excepciones, cobertura de la función modificada, complejidad ciclomática y validación de entradas de voz. Fijar como política que todo PR requiere al menos una revisión de par antes del merge.

- **Métrica que mejora:** Eficacia de revisión: de 16.67 % → objetivo ≥ 30 %
- **Métrica secundaria:** DRE global (revisión + pruebas) acumulado

---

## Estimación (juicio experto de la IA)

### Comparativa frente a las horas reales (122 h)

| Técnica | Total estimado | Error absoluto | Error relativo |
|---|---|---|---|
| Juicio de expertos (promedio) | 112.66 h | 9.34 h | 7.66 % |
| Tres puntos / PERT | 114.68 h | 7.32 h | 6.00 % |
| Puntos de función | 146.38 h | 24.38 h | 19.98 % |
| Analogía | 152.53 h | 30.53 h | 25.02 % |
| Estimación del alumno desarrollador | 102.00 h | 20.00 h | 16.39 % |

### Técnica más acertada: **Tres puntos / PERT**

La estimación PERT (114.68 h) fue la que más se acercó a las 122 horas reales, con un error del **6.00 %** y, significativamente, las horas reales cayeron **dentro del rango del 95 %** calculado (104.03 h – 125.33 h). Esto no es casualidad: PERT obliga al estimador a razonar explícitamente sobre el escenario optimista, el más probable y el pesimista, lo que captura la incertidumbre real del proyecto. En el caso de Azmuth, los sprints de "Interfaz y servidor" (60 % de desviación) y "Núcleo de voz" (40 %) habrían sido mapeados al escenario pesimista, moderando la estimación global hacia arriba con respecto a la del alumno (102 h).

El **juicio de expertos promedio** (112.66 h, error 7.66 %) quedó en segundo lugar; su cercanía se explica porque la estimación de la IA (Claude, 119 h) compensó el optimismo del alumno (102 h), jalando el promedio hacia el valor correcto. Esto ilustra una ventaja del juicio experto múltiple: la diversidad de perspectivas reduce el sesgo de optimismo individual.

La **analogía** y los **puntos de función** sobreestimaron significativamente (+25 % y +20 % respectivamente). La analogía usó un factor de ajuste del 10 % que resultó insuficiente para capturar la complejidad real de las integraciones de voz e IA generativa; los puntos de función, por su parte, tienden a sobreponderar los componentes de datos (ILF/EIF) en proyectos donde el valor está en la lógica de comportamiento conversacional, no en el volumen transaccional.

**Recomendación para proyectos futuros:** Usar PERT como técnica principal complementada con juicio de expertos múltiple, e incorporar un **buffer de contingencia explícito del 15 %** sobre la estimación PERT central (en este caso: 114.68 × 1.15 = 131.9 h), lo que habría absorbido cómodamente las 122 h reales.

---

*Auditoría generada con base exclusivamente en los datos del pipeline proporcionados. Ninguna cifra ha sido inferida fuera de los datos disponibles.*
