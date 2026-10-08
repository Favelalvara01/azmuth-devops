## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-08 13:27**

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **74 / 100**, situándose en un nivel de calidad aceptable pero con brechas críticas que deben cerrarse antes de la liberación a producción. La cobertura de pruebas (86.58 %), la ausencia de defectos abiertos y el análisis estático limpio (Ruff: *All checks passed*) son fortalezas sólidas; sin embargo, el DRE del 44.44 % y un MTTD de 9.71 días revelan que el pipeline de detección temprana no es suficientemente eficaz. **No se recomienda la liberación inmediata**; se requiere elevar el DRE por encima del 75 % y cubrir los módulos con cobertura crítica (`voice.py` 72.88 %, `app_desktop.py` 0.0 %) antes del *go-live*.

---

## Idoneidad funcional

### Completitud funcional
- **315 pruebas ejecutadas, 315 aprobadas (100 % de aprobación)** y **0 defectos abiertos** indican que todas las funciones especificadas están implementadas y verificadas en el estado actual del repositorio.
- Los 11 módulos de skills cubren las dimensiones funcionales declaradas (voz, recordatorios, multimedia, web, sistema, memoria, etc.).

### Corrección funcional
- Densidad de defectos histórica: **5.77 defectos / KLOC**. El módulo con mayor densidad fue "Núcleo de voz" (Sprint 1) con **13.74 def/KLOC**, lo que sugiere que la lógica de reconocimiento/síntesis fue la más propensa a errores durante el desarrollo.
- Densidad actual (defectos abiertos): **0.0 def/KLOC** — todos los 18 defectos reportados han sido corregidos.
- La cobertura de `app_desktop.py` es **0.0 %**: no existe evidencia de prueba automatizada de esta unidad; su corrección funcional no puede garantizarse.

### Pertinencia funcional
- Los **304 puntos de función no ajustados** (VAF = 1.07) distribuidos en EI, EO, EQ, ILF y EIF reflejan un sistema con integración de APIs externas (Claude, ElevenLabs), persistencia SQLite e interfaz de escritorio, coherente con los requisitos de un asistente de voz con IA.
- La funcionalidad es pertinente con el dominio; sin embargo, `skills/multimedia.py` (cobertura 74.07 %) y `cerebro.py` (75.0 %) representan núcleos funcionales cuya pertinencia operativa no está completamente validada.

---

## Fiabilidad

### Madurez
| Indicador | Valor | Evaluación |
|---|---|---|
| Defectos abiertos | 0 | ✅ Excelente |
| Defectos totales cerrados | 18 / 18 | ✅ 100 % resueltos |
| Densidad defectos abiertos | 0.0 / KLOC | ✅ |
| DRE (Defect Removal Efficiency) | **44.44 %** | ⚠️ Bajo |
| % defectos detectados en pruebas vs. producción | 33.33 % | 🔴 Crítico |

El DRE del **44.44 %** significa que solo 4 de 9 defectos que debieron detectarse antes de producción fueron capturados en fases tempranas. Los estándares de industria recomiendan un DRE ≥ 75 % para productos de software en producción activa. De los 4 defectos graves registrados, **ninguno fue detectado durante las pruebas**, lo cual representa el riesgo de fiabilidad más importante del proyecto.

### Disponibilidad
- No se reportan métricas de *uptime* explícitas en los datos. El pipeline de CI/CD con GitHub Actions y Docker provee una base de despliegue reproducible que contribuye positivamente a la disponibilidad.
- La cobertura de `servidor.py` en **95.57 %** y `nucleo.py` en **100 %** son indicadores favorables para los componentes de mayor criticidad en tiempo de ejecución.

### Tolerancia a fallos
- La distribución de defectos por fase muestra **10 defectos en producción** (55.6 % del total), lo que indica que el sistema ha operado bajo condiciones reales con fallos activos. La ausencia de mecanismos de *graceful degradation* documentados en las métricas es una brecha.
- `voice.py` con cobertura **72.88 %** es el componente de entrada principal del asistente; su baja cobertura implica rutas de manejo de errores no probadas.

### Recuperabilidad
| Indicador | Valor | Evaluación |
|---|---|---|
| MTTD | **233.09 h (9.71 días)** | 🔴 Muy alto |
| MTTR | **3.9 h (234 min)** | ✅ Aceptable |
| Ratio MTTD/MTTR | **59.8 x** | ⚠️ El tiempo de detección supera 59 veces al de reparación |

El MTTR de **3.9 horas** es notable y refleja un equipo ágil en la corrección. El problema central es el MTTD: casi **10 días para detectar un defecto** indica dependencia excesiva del feedback de producción sobre el monitoreo proactivo y las pruebas automatizadas.

---

## Mantenibilidad

### Índice de mantenibilidad
- **Promedio general: 72.02 / 100** — Umbral aceptable (>65), pero con margen de mejora hacia el rango óptimo (>85).

### Complejidad ciclomática — Rangos A-F (McCabe)

| Rango | CC | Interpretación | Funciones |
|---|---|---|---|
| **A** | 1–5 | Simple, bajo riesgo | 180 (84.1 %) |
| **B** | 6–10 | Moderada, riesgo manejable | 22 (10.3 %) |
| **C** | 11–15 | Compleja, riesgo elevado | 12 (5.6 %) |
| **D** | 16–20 | Muy compleja, alto riesgo | 0 |
| **E** | 21–25 | Extremadamente compleja | 0 |
| **F** | >25 | Inmanejable | 0 |

- **94.39 % en rangos A+B** es una distribución muy saludable.
- No existen funciones en rangos D, E o F.
- Las **12 funciones en rango C** son las candidatas prioritarias a refactorizar.

### Funciones a refactorizar (Top 10 por complejidad)

| Función | Archivo | Línea | CC | Rango | Acción sugerida |
|---|---|---|---|---|---|
| `intentar` | `skills/apps_instaladas.py` | 213 | 15 | C | Extraer casos de instalación en funciones auxiliares |
| `intentar` | `skills/recordatorios.py` | 96 | 14 | C | Separar lógica de parsing y de persistencia |
| `resolver` | `skills/apps_instaladas.py` | 169 | 13 | C | Aplicar patrón Strategy por tipo de app |
| `intentar` | `skills/multimedia.py` | 31 | 13 | C | Extraer ramas de formato/codec |
| `intentar` | `skills/pestanas.py` | 33 | 13 | C | Descomponer por acción de pestaña |
| `actualizar_perfil_si_toca` | `cerebro.py` | 205 | 12 | C | Separar condiciones de tiempo y de perfil |
| `intentar` | `skills/memoria.py` | 61 | 12 | C | Extraer operaciones CRUD en métodos dedicados |
| `revisar_pendientes` | `skills/recordatorios.py` | 170 | 12 | C | Dividir en sub-revisiones por tipo de pendiente |
| `intentar` | `skills/web.py` | 53 | 12 | C | Separar búsqueda, navegación y scraping |
| `preguntar` | `cerebro.py` | 104 | 11 | C | Extraer manejo de contexto conversacional |

> **Nota:** El patrón recurrente es que las funciones `intentar` concentran demasiada lógica de ramificación. Se recomienda evaluar un **dispatcher pattern** a nivel de skills para que cada skill registre sus intenciones y las ejecute con funciones atómicas.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| DRE crítico (44.44 %): defectos graves llegan a producción sin ser detectados en pruebas | Alta | Crítico | Implementar pruebas de integración para los 4 defectos graves; establecer *quality gates* en GitHub Actions que bloqueen el merge si DRE < 70 % |
| `app_desktop.py` sin cobertura (0.0 %): fallas en la interfaz de escritorio no detectadas | Alta | Alto | Agregar suite de pruebas unitarias/UI para `app_desktop.py` antes del siguiente release |
| MTTD de 9.71 días: detección tardía de defectos en producción | Alta | Alto | Instrumentar logging estructurado y alertas automáticas (Sentry/Datadog); reducir MTTD objetivo a < 24 h |
| Funciones con CC=12–15 sin pruebas dirigidas a sus ramas: deuda técnica creciente | Media | Medio | Aplicar pruebas basadas en caminos (*path-based testing*) para las 12 funciones rango C |
| Desviación de estimación del 19.61 % (20 h sobre lo estimado): riesgo de subestimación en sprints futuros | Media | Medio | Incorporar buffer del 20 % en sprints con módulos de integración de APIs externas; usar velocidad medida (7.45 pts/sprint) como referencia |
| `voice.py` con cobertura 72.88 %: componente crítico de entrada con rutas no probadas | Media | Alto | Agregar pruebas con mocks de audio para cubrir rutas de error de reconocimiento de voz |
| Concentración de defectos en Sprint 5 "Interfaz y servidor" (6 defectos, 9.42/KLOC): módulo frágil | Media | Medio | Realizar sesión de revisión de código en `servidor.py` y `app_desktop.py`; aumentar cobertura de `app_desktop.py` |
| Dependencia de APIs externas (Claude, ElevenLabs) sin pruebas de contrato documentadas | Baja | Alto | Implementar *consumer-driven contract tests* con mocks estables; documentar SLAs de las APIs |

---

## Plan de mejora

Las siguientes 5 acciones están priorizadas de mayor a menor urgencia para la liberación:

---

### 🔴 Acción 1 — Elevar el DRE por encima del 75 % *(Prioridad: Crítica)*
**Qué hacer:** Diseñar y ejecutar pruebas de integración orientadas específicamente a los 4 defectos graves registrados (que actualmente tienen DRE de 0 % en pruebas). Establecer en GitHub Actions un *quality gate* que calcule el DRE incremental y bloquee el merge a `main` si el indicador cae por debajo del 75 %.

**Métrica que mejora:** `DRE` (44.44 % → ≥ 75 %) y `defectos_por_fase.produccion` (reducción).

---

### 🔴 Acción 2 — Cubrir `app_desktop.py` y `voice.py` con pruebas automatizadas *(Prioridad: Alta)*
**Qué hacer:** Para `app_desktop.py` (0.0 %): implementar pruebas con `pytest-qt` o mocks de widgets. Para `voice.py` (72.88 %): agregar casos de prueba que cubran rutas de error de reconocimiento (silencio, ruido, timeout) usando mocks de los motores de voz.

**Métrica que mejora:** `cobertura.total` (86.58 % → ≥ 90 %), cobertura de `app_desktop.py` (0 % → ≥ 80 %), cobertura de `voice.py` (72.88 % → ≥ 85 %).

---

### 🟠 Acción 3 — Reducir MTTD mediante observabilidad proactiva *(Prioridad: Alta)*
**Qué hacer:** Integrar un sistema de logging estructurado (e.g., `structlog` + Sentry) en `cerebro.py`, `servidor.py` y `voice.py` con alertas automáticas ante excepciones no controladas. Establecer un dashboard de métricas de error con umbral de alerta en < 1 hora.

**Métrica que mejora:** `mttd_horas` (233.09 h → objetivo < 24 h), porcentaje de defectos detectados en producción (actualmente 55.6 %).

---

### 🟡 Acción 4 — Refactorizar las 10 funciones de rango C *(Prioridad: Media)*
**Qué hacer:** Comenzar por las 5 funciones `intentar` de mayor complejidad (apps_instaladas, recordatorios, multimedia, pestanas, web) aplicando el patrón *dispatcher* o extracción de métodos atómicos. Validar refactorización con las pruebas existentes (sin reducir cobertura).

**Métrica que mejora:** `complejidad.maxima` (15 → ≤ 10), `mantenibilidad_promedio` (72.02 → ≥ 80), porcentaje de funciones en rango A+B (94.39 % → 100 %).

---

### 🟡 Acción 5 — Calibrar el modelo de estimación incorporando el factor de APIs externas *(Prioridad: Media)*
**Qué hacer:** Documentar formalmente la velocidad medida de 7.45 pts/sprint y 1.0–2.0 h/punto según módulo. Para sprints con integración de APIs externas (como Sprint 5, con 60 % de desviación), aplicar un factor de riesgo multiplicador de 1.25–1.35 sobre la estimación base. Usar el rango PERT del 95 % (104–125 h) como banda de control en futuros proyectos similares.

**Métrica que mejora:** `desviacion_porcentaje` general (19.61 % → objetivo < 10 %), precisión de estimación por módulo en sprints de integración.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas vs. horas reales (122 h)

| Técnica | Total estimado (h) | Error absoluto (h) | Error relativo |
|---|---|---|---|
| **Juicio de expertos (promedio)** | **112.66** | 9.34 | 7.66 % |
| **Tres puntos PERT** | **114.68** | 7.32 | 6.0 % |
| Rango 95 % PERT | 104.03 – 125.33 | *(contiene 122 h)* | ✅ |
| Puntos de función | 146.38 | 24.38 | 19.98 % |
| Estimación análoga | 152.53 | 30.53 | 25.02 % |
| Alumno desarrollador (JE) | 102.00 | 20.00 | 16.39 % |
| Compañero con experiencia (JE) | 117.00 | 5.00 | 4.10 % |
| **IA (Claude) - JE** | **119.00** | **3.00** | **2.46 %** |

### Técnica más acertada: **Juicio de expertos — estimación de la IA (Claude)**

La estimación individual de la IA con **119 horas** fue la más cercana a las 122 horas reales, con un error de solo **3 horas (2.46 %)**. Sin embargo, desde una perspectiva metodológica, la técnica que mejor se comportó como **método formal** fue **Tres Puntos PERT**, por tres razones:

1. **Contiene el valor real dentro de su intervalo de confianza del 95 % (104.03 – 125.33 h)**, lo que valida su capacidad predictiva como distribución de probabilidad, no solo como punto estimado.
2. Su **error relativo del 6.0 % (7.32 h)** es el menor entre todas las técnicas formales, superando incluso al promedio del juicio de expertos.
3. Al modelar explícitamente la incertidumbre (O, M, P por módulo), la técnica **habría advertido** al equipo que módulos como "Interfaz y servidor" (P=22 h vs. real=16 h) tenían alta dispersión, permitiendo gestión de riesgo proactiva.

La técnica análoga y la de puntos de función sobreestimaron significativamente (+19.98 % y +25.02 % respectivamente), lo cual es esperable: la análoga usó un factor de ajuste de solo 1.1× para compensar la complejidad de integración de APIs con IA generativa, que en la práctica resultó ser moderada (la persistencia SQLite, DevOps y corrección de defectos fueron más rápidas de lo esperado). Los puntos de función, por su parte, asignaron un peso elevado a los ILF de complejidad media, inflando el estimado.

**Recomendación:** Para futuros proyectos de la misma familia (asistentes de voz con IA), usar **Tres Puntos PERT** como técnica principal complementada con el **juicio de la IA** como tercer estimador en la mesa de expertos, dado que demostró ser el estimador individual más preciso en este proyecto.
