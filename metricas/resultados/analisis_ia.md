## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-09 01:37

---

## Dictamen general

El proyecto Azmuth obtiene una calificación de **79 / 100**: posee una base técnica sólida (cobertura 88 %, 392/392 pruebas en verde, complejidad ciclomática predominantemente en rango A-B y análisis estático Ruff sin hallazgos), pero presenta dos brechas críticas que impiden una liberación sin condiciones: el **DRE del 44 %** expone que más de la mitad de los defectos llegaron a producción sin ser detectados en pruebas, y el **MTTD de 9,7 días** evidencia que el monitoreo reactivo es lento. **Se recomienda liberación condicionada** a la implementación de las acciones de fiabilidad y detección temprana descritas en el plan de mejora.

---

## Idoneidad funcional

| Sub-característica | Evidencia | Valoración |
|---|---|---|
| **Completitud funcional** | 392 casos de prueba, todos aprobados; 11 módulos/skills cubiertos incluyendo voz, IA, recordatorios, multimedia, sistema y persistencia | ✅ Alta |
| **Corrección funcional** | 18 defectos históricos, **0 abiertos** al cierre; densidad global de 4,82 def/KLOC (aceptable para un proyecto 1.ª versión) | ✅ Aceptable |
| **Pertinencia funcional** | El conjunto de skills (tiempo, apps, pestañas, contactos, hábitos, notas, web, idiomas, multimedia) responde al caso de uso declarado de asistente de voz IA en Windows | ✅ Alta |

> **Notas de riesgo residual:** `app_desktop.py` tiene cobertura **0 %** y 1 defecto histórico; `voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %) están por debajo del umbral recomendado de 80 %. El módulo "Núcleo de voz" (Sprint 1) concentró la mayor densidad de defectos: **13,37 def/KLOC**, cinco veces la media global.

---

## Fiabilidad

### Indicadores clave de proceso

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** | 233,09 h (9,71 días) | Detección muy lenta; los defectos permanecen ocultos casi 10 días en promedio antes de ser identificados |
| **MTTR** | 3,9 h (234 min) | Excelente capacidad de corrección una vez detectado el problema |
| **DRE (Defect Removal Efficiency)** | 44,44 % | Crítico: sólo 5 de los 11 defectos detectables en pruebas fueron capturados antes de producción; el umbral de referencia industrial es ≥ 85 % |
| **Defectos en producción** | 10 / 18 (55,6 %) | Mayoría de defectos escaparon al ambiente productivo |
| **Defectos graves detectados en pruebas** | 0 / 4 (0 %) | Los 4 defectos graves **no** fueron capturados por el suite de pruebas |

### Sub-características ISO/IEC 25010

| Sub-característica | Valoración | Fundamento |
|---|---|---|
| **Madurez** | ⚠️ Media | DRE 44 % y 10 defectos en producción reducen la confianza en la estabilidad |
| **Disponibilidad** | ✅ Alta | MTTR de 3,9 h indica recuperación rápida; 0 defectos abiertos |
| **Tolerancia a fallos** | ⚠️ Media-baja | Los 4 defectos graves escaparon a las pruebas; se desconoce cobertura de escenarios de fallo en `app_desktop.py` (0 % cobertura) |
| **Recuperabilidad** | ✅ Alta | Pipeline CI/CD con Docker facilita rollback; MTTR corto lo confirma |

---

## Mantenibilidad

### Resumen de complejidad ciclomática (268 funciones)

| Rango | Descripción | Cantidad | % |
|---|---|---|---|
| **A** (1–5) | Simple, bajo riesgo | 219 | 81,7 % |
| **B** (6–10) | Moderada, manejable | 35 | 13,1 % |
| **C** (11–15) | Compleja, refactorización recomendada | 14 | 5,2 % |
| **D** (16–20) | Alta, refactorización urgente | 0 | 0 % |
| **E/F** (> 20) | Muy alta / No mantenible | 0 | 0 % |
| **Total A+B** | | **254** | **94,78 %** |

> El **índice de mantenibilidad promedio es 68,83 / 100** — zona amarilla (referencia: < 65 preocupante, > 85 excelente). La buena distribución A-B compensa parcialmente la caída causada por las 14 funciones en rango C.

### Funciones prioritarias a refactorizar (todas rango C)

| Prioridad | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 🔴 1 | `skills/tiempo.py` | `_pronostico` | 100 | 16 | Extraer ramas de condición meteorológica a funciones auxiliares |
| 🔴 2 | `skills/apps_instaladas.py` | `intentar` | 210 | 15 | Aplicar patrón Command o tabla de despacho para reducir if-else |
| 🔴 3 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Separar lógica de parsing, validación y persistencia |
| 🟠 4 | `skills/apps_instaladas.py` | `resolver` | 166 | 13 | Delegar resolución de cada tipo de app a métodos independientes |
| 🟠 5 | `skills/multimedia.py` | `intentar` | 31 | 13 | Tabla de despacho por intención de voz |
| 🟠 6 | `skills/pestanas.py` | `intentar` | 33 | 13 | Separar por acción (abrir, cerrar, navegar) |
| 🟠 7 | `skills/tiempo.py` | `_recomendaciones` | 71 | 13 | Extraer lógica de recomendación a diccionario/estrategia |
| 🟡 8 | `groq_ia.py` | `completar` | 85 | 12 | Desacoplar reintentos, manejo de errores y construcción del prompt |
| 🟡 9 | `tematicas.py` | `_sintetizar` | 233 | 12 | Separar síntesis de cada temática en métodos propios |
| 🟡 10 | `skills/memoria.py` | `intentar` | 62 | 12 | Segregar operaciones CRUD de la lógica de intención |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE crítico (44 %):** defectos graves llegan a producción sin detección | Alta | Crítico | Añadir pruebas de integración y pruebas negativas dirigidas a los 4 defectos graves; establecer gate de DRE ≥ 75 % en CI |
| **Cobertura nula en `app_desktop.py`** | Alta | Alto | Crear suite mínima con mocking de UI antes del próximo sprint; bloquear merge si cobertura < 70 % |
| **MTTD de 9,7 días:** monitoreo reactivo insuficiente | Media | Alto | Integrar alertas proactivas (Sentry / logging estructurado + umbral automático) para reducir MTTD a < 48 h |
| **Concentración de defectos en Sprint 1 "Núcleo de voz" (13,37 def/KLOC):** módulo central con mayor fragilidad histórica | Media | Alto | Incrementar cobertura de `voice.py` al ≥ 85 %; añadir pruebas de regresión específicas del pipeline de reconocimiento |
| **14 funciones en rango C:** deuda técnica que eleva el costo de cambio | Media | Medio | Refactorizar al menos las 3 funciones con CC ≥ 14 antes de la próxima iteración; incluir revisión de CC en checklist de PR |
| **Desviación de estimación +19,6 % (20 h extra):** dos sprints superaron el 40-60 %** | Alta | Medio | Adoptar planning poker con límite de spike en sprints con integración de APIs externas; usar rango 95 % de tres puntos como presupuesto |
| **Dependencia de APIs externas (Groq, ElevenLabs, Gemini):** fallos de terceros sin circuit breaker evidente | Media | Alto | Implementar patrón Circuit Breaker y modo degradado (texto-a-texto) cuando la API de voz no esté disponible |

---

## Plan de mejora

> Ordenado por **impacto en calidad + urgencia**; cada acción lleva la métrica ISO/IEC 25023 que mejorará directamente.

### ① Elevar la eficacia de detección — DRE ≥ 75 % *(Prioridad: Crítica)*
**Acciones:**
- Crear 20+ casos de prueba negativos y de frontera enfocados en los escenarios donde fallaron los 4 defectos graves.
- Añadir en GitHub Actions un job que calcule el DRE estimado por fase y bloquee el merge si cae por debajo del umbral.

**Métrica mejorada:** `DRE` (actualmente 44,44 % → objetivo ≥ 75 %) · Sub-característica: **Madurez**.

---

### ② Cubrir `app_desktop.py` y elevar `voice.py` / `skills/multimedia.py` *(Prioridad: Alta)*
**Acciones:**
- Implementar pruebas unitarias con mocking de tkinter/wxPython para `app_desktop.py` hasta ≥ 70 %.
- Agregar pruebas de integración para `voice.py` (72,88 %) y `skills/multimedia.py` (74,07 %) hasta ≥ 85 %.
- Configurar umbral de cobertura mínima por archivo en pytest-cov (`--cov-fail-under=80`).

**Métrica mejorada:** `Cobertura de código por archivo` (0 % / 72-74 % → ≥ 80 %) · Sub-característica: **Completitud funcional / Tolerancia a fallos**.

---

### ③ Reducir MTTD mediante monitoreo proactivo *(Prioridad: Alta)*
**Acciones:**
- Integrar Sentry (o logging estructurado con alertas en Slack/email) en `main.py`, `cerebro.py` y `servidor.py`.
- Definir SLA de alerta: cualquier excepción no controlada debe generar notificación en ≤ 1 h.
- Revisar y ampliar `monitoreo.py` (actualmente 88,89 % cobertura) con escenarios de fallo de API externa.

**Métrica mejorada:** `MTTD` (9,71 días → objetivo ≤ 2 días) · Sub-característica: **Disponibilidad / Tolerancia a fallos**.

---

### ④ Refactorizar las 3 funciones con CC ≥ 14 *(Prioridad: Media-Alta)*
**Acciones:**
- `_pronostico` (CC 16): extraer cada condición climática a función pura, verificar con pruebas parametrizadas.
- `intentar` en `apps_instaladas.py` (CC 15): reemplazar cadena if-elif por diccionario de despacho.
- `intentar` en `recordatorios.py` (CC 14): separar en tres funciones: `_parsear_recordatorio`, `_validar_recordatorio`, `_persistir_recordatorio`.
- Añadir comprobación de CC máxima (≤ 10) como gate en el pipeline CI.

**Métrica mejorada:** `Complejidad ciclomática máxima` (16 → ≤ 10) · `Índice de mantenibilidad` (68,83 → ≥ 75) · Sub-característica: **Modificabilidad / Analizabilidad**.

---

### ⑤ Implementar Circuit Breaker y modo degradado para APIs externas *(Prioridad: Media)*
**Acciones:**
- Envolver las llamadas a Groq, ElevenLabs y Gemini con la librería `tenacity` (reintentos) + patrón Circuit Breaker.
- Definir respuesta degradada: si la API de síntesis de voz falla, el asistente responde en texto (notificación desktop).
- Añadir prueba de integración que simule timeout de API y verifique que el sistema no se cuelga.

**Métrica mejorada:** `Tolerancia a fallos` · `Recuperabilidad` (MTTR sostenido ≤ 4 h ante fallos de terceros) · Sub-característica: **Fiabilidad**.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas

| Técnica | Total estimado (h) | Horas reales | Error absoluto | Error % |
|---|---|---|---|---|
| **Juicio de expertos** (promedio) | 110,5 | 122,0 | 11,5 | 9,4 % |
| **Tres puntos — PERT** | **114,68** | **122,0** | **7,32** | **6,0 %** |
| Puntos de función | 146,38 | 122,0 | 24,38 | 20,0 % |
| Análoga | 182,45 | 122,0 | 60,45 | 49,5 % |

### Técnica más cercana: **Tres puntos (PERT)** — error del 6 %

La estimación de **tres puntos con distribución PERT** resultó ser la más precisa (114,68 h vs. 122 h reales, error de 7,32 h / 6 %). Hay tres razones que explican este resultado:

1. **Captura de incertidumbre por módulo:** al definir escenarios optimista, probable y pesimista para cada sprint, se internalizaron los riesgos de integración de APIs externas y la complejidad del núcleo de voz —exactamente los módulos que más se desviaron (Sprints 1, 3 y 5 con 40 %, 28 % y 60 % de sobrecosto).

2. **El rango 95 % (104–125 h) contenía las horas reales:** las 122 h reales cayeron dentro del intervalo de confianza calculado, lo que valida el modelo probabilístico como adecuado para proyectos con dependencias externas volátiles.

3. **Contrapunto del juicio de expertos:** el alumno subestimó consistentemente (estimó 102 h), mientras que la IA estimó 119 h —más cercano a la realidad—, pero el **promedio** de ambos (110,5 h) perdió ese ajuste al suavizar la señal más conservadora. PERT, al ponderar el pesimista, compensó esa tendencia optimista del desarrollador.

> **Lección aprendida:** para proyectos con integraciones de terceros (LLMs, síntesis de voz, APIs REST), la estimación análoga sobreestima si el proyecto de referencia no tiene ese tipo de dependencias, y el juicio individual subestima por sesgo de optimismo. **Tres puntos PERT con revisión por experto externo** es la técnica más robusta para este perfil de proyecto.

---

*Auditoría generada con base exclusiva en los datos del pipeline proporcionados. Ninguna cifra ha sido extrapolada sin sustento en los datos fuente.*
