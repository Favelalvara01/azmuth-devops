## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Norma:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha del reporte:** 2026-11-15

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **76 / 100**, posicionándose en un nivel de calidad **aceptable con reservas**. Sus fortalezas son la cobertura de pruebas (87,87 %), la ausencia de defectos abiertos y un análisis estático limpio (Ruff sin hallazgos); sin embargo, la DRE del 52,17 % y un MTTD de ~14 días revelan que el proceso de detección temprana es insuficiente para una liberación sin riesgo residual. **Se recomienda liberación condicionada** a la resolución de los cinco puntos del plan de mejora, con especial atención a la DRE antes del siguiente ciclo de producción.

---

## Idoneidad funcional

### Completitud funcional
| Indicador | Valor | Referencia |
|---|---|---|
| Pruebas totales | 576 | — |
| Pruebas aprobadas | 567 | — |
| Defectos `xfail` conocidos | 9 | Funcionalidad pendiente/limitada |
| Defectos abiertos | **0** | ✅ |
| Cobertura global | **87,87 %** | Umbral recomendado ≥ 85 % ✅ |

La suite cubre 567 escenarios exitosamente. Los 9 `xfail` representan comportamientos conocidos que el equipo decidió diferir; no constituyen fallos bloqueantes pero sí indican funcionalidad **incompleta en bordes del sistema**.

### Corrección funcional
- **23 defectos históricos, 0 abiertos**: toda la deuda técnica de defectos está saldada al momento de la auditoría.
- Densidad histórica de **5,74 defectos/KLOC**; en módulos tempranos como "Núcleo de voz" y "Skills básicas" la densidad fue de 12,5 y 10,68/KLOC respectivamente, lo que indica que la corrección se realizó de forma reactiva.
- Los archivos `app_desktop.py` (0 % cobertura), `voice.py` (72,88 %), `skills/multimedia.py` (74,55 %), `skills/web.py` (75 %) y `deepseek_ia.py` (75 %) presentan zonas funcionales **sin validación automatizada**, lo que compromete la certeza de corrección en esos módulos.

### Pertinencia funcional
El sistema cubre los dominios esperados para un asistente de voz con IA: reconocimiento de voz, skills de sistema, integración con múltiples LLM (Gemini, Groq, DeepSeek), persistencia SQLite, servidor remoto y modo escritorio. La arquitectura de skills desacopladas es pertinente al dominio. Sin embargo, la ausencia total de pruebas en `app_desktop.py` deja una superficie funcional sin verificar.

---

## Fiabilidad

### Madurez y disponibilidad
| Métrica | Valor | Interpretación |
|---|---|---|
| MTTD | **334,65 h (≈ 13,94 días)** | ⚠️ Muy alto: los defectos tardan ~2 semanas en detectarse |
| MTTR | **3,08 h (185 min)** | ✅ Excelente: una vez detectado, se corrige con rapidez |
| Defectos reparados | 23 / 23 | ✅ 100 % de cierre |
| DRE (Defect Removal Efficiency) | **52,17 %** | 🔴 Crítico: menos de la mitad de los defectos graves se detectaron antes de producción |

**Cálculo DRE aplicado:**
```
DRE = Defectos detectados en pruebas / (Defectos en pruebas + Defectos en producción)
    = 9 / (9 + 10) × 100 = 47,37 %

DRE (graves) = Graves detectados en pruebas / Graves totales
             = 3 / 7 × 100 = 42,86 %

DRE reportado (incluye revisión) = (3 + 9) / 23 × 100 = 52,17 %
```

La DRE del 52,17 % es el indicador más preocupante del proyecto: **casi la mitad de los defectos (10/23) llegaron a producción**, incluyendo 4 defectos graves que escaparon a las pruebas. La industria considera aceptable ≥ 85 % y excelente ≥ 95 %.

### Tolerancia a fallos y recuperabilidad
- El MTTR de 3,08 h sugiere buena capacidad de recuperación operativa, apoyada por el pipeline CI/CD (GitHub Actions + Docker).
- La eficacia de revisión del 13,04 % (3/23 defectos detectados en revisión) indica que las revisiones de código son poco sistemáticas: se recomienda fortalecer el proceso de code review antes de merge.
- Los 9 `xfail` actúan como registro controlado de comportamientos no resueltos; es positivo que estén documentados en lugar de ignorados.

---

## Mantenibilidad

### Índice de mantenibilidad
El **índice de mantenibilidad promedio de 68,56** (escala 0–100) se clasifica como **moderado**, justo por encima del umbral de alerta (< 65). Proyectos orientados a larga vida útil deberían aspirar a ≥ 75.

### Complejidad ciclomática
| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Excelente | 245 | 82,21 % |
| **B** (6–10) | Buena | 37 | 12,42 % |
| **C** (11–15) | Moderada — refactorizar | 16 | 5,37 % |
| **D** (16–20) | Alta — refactorizar urgente | 0 | 0 % |
| **E** (21–25) | Muy alta | 0 | 0 % |
| **F** (> 25) | Extrema | 0 | 0 % |

✅ El **94,63 % de las funciones** están en rango A o B, lo que es un resultado muy positivo para un proyecto de 4 KLOC.

### Funciones a refactorizar (Rango C — complejidad ≥ 11)

| Prioridad | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 🔴 1 | `tematicas.py` | `_sintetizar` | 238 | **16** | Extraer ramas de síntesis en métodos especializados por tipo |
| 🔴 2 | `skills/tiempo.py` | `_pronostico` | 100 | **16** | Separar lógica de parsing, cálculo y formato de respuesta |
| 🟠 3 | `skills/apps_instaladas.py` | `intentar` | 210 | 15 | Tabla de despacho (`dict`) en lugar de cadena if/elif |
| 🟠 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Extraer validación de fecha/hora y persistencia |
| 🟠 5 | `skills/apps_instaladas.py` | `resolver` | 166 | 13 | Separar resolución por tipo de aplicación |
| 🟡 6 | `skills/multimedia.py` | `intentar` | 34 | 13 | Dividir por acción (play/pause/stop/volumen) |
| 🟡 7 | `skills/pestanas.py` | `intentar` | 36 | 13 | Mismo patrón: tabla de despacho |
| 🟡 8 | `skills/tiempo.py` | `_recomendaciones` | 71 | 13 | Extraer lógica por condición meteorológica |
| 🟡 9 | `skills/web.py` | `intentar` | 93 | 13 | Separar por tipo de búsqueda/acción web |
| 🟢 10 | `deepseek_ia.py` | `completar` | 82 | 12 | Extraer manejo de errores HTTP y reintentos |

> **Nota:** El patrón dominante en las funciones `intentar` de múltiples skills sugiere que el diseño base del dispatcher de intenciones debería revisarse arquitectónicamente para reducir la complejidad estructural de forma sistémica, en lugar de refactorizar skill por skill.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE baja (52,17 %)**: defectos graves escapan a producción | Alta | Alto | Implementar pruebas de regresión específicas para los 7 defectos graves; añadir pruebas de integración end-to-end para flujos críticos de voz e IA |
| **MTTD elevado (~14 días)**: la detección tardía incrementa el costo de corrección | Alta | Medio | Activar alertas automáticas en el pipeline CI/CD y monitoreo de errores en runtime (p. ej. Sentry) para reducir el tiempo de detección |
| **Cobertura cero en `app_desktop.py`** y baja en `voice.py`, `multimedia.py`, `web.py` | Media | Alto | Crear suite de pruebas dedicada para la interfaz de escritorio (mocking de GUI) y los módulos con cobertura < 80 % antes del siguiente release |
| **MTTD largo + sprints tempranos con alta densidad de defectos** (12,5/KLOC en Sprint 1): riesgo de deuda técnica encubierta en módulo de voz | Media | Alto | Auditoría de código enfocada en `nucleo.py`, `voice.py` y `main.py`; incrementar cobertura de esos módulos al 95 % |
| **Eficacia de revisión baja (13,04 %)**: las revisiones de código no filtran defectos eficazmente | Alta | Medio | Formalizar checklist de code review (seguridad, manejo de excepciones, tipos de retorno); exigir ≥ 1 revisor externo por PR |
| **Desviación de estimación del 19,61 %** (20 h extra): riesgo de subestimación en próximos proyectos con APIs externas | Media | Medio | Usar Three-Point / PERT como técnica estándar; añadir factor de ajuste ≥ 1,2 para módulos con integraciones de terceros |
| **Funciones con CC ≥ 13** sin pruebas suficientes (`multimedia.py` 74,55 %, `web.py` 75 %) | Media | Medio | Exigir cobertura de rama (branch coverage) ≥ 85 % en funciones Rango C antes de merge a main |

---

## Plan de mejora

> Las acciones están ordenadas por **impacto en calidad / urgencia**.

### Acción 1 — Elevar la DRE mediante pruebas de integración para defectos graves 🔴
**Prioridad:** Crítica | **Sprint objetivo:** Inmediato

- Crear casos de prueba específicos que reproduzcan los 7 defectos graves identificados (4 que escaparon a producción).
- Integrar pruebas de flujo completo voz → procesamiento → respuesta en el pipeline CI.
- **Métrica que mejora:** `DRE` (objetivo: de 52,17 % → ≥ 80 %) y `defectos_por_fase.produccion` (objetivo: reducir de 10 a ≤ 3 en el próximo ciclo).

---

### Acción 2 — Cubrir módulos críticos sin pruebas (`app_desktop.py`, `voice.py`, `multimedia.py`) 🔴
**Prioridad:** Alta | **Sprint objetivo:** Próximo sprint

- `app_desktop.py`: diseñar pruebas con mocking de la interfaz gráfica (p. ej. `pytest-qt` o mocks de `tkinter`).
- `voice.py` (72,88 %), `skills/multimedia.py` (74,55 %), `skills/web.py` (75 %), `deepseek_ia.py` (75 %): añadir pruebas unitarias hasta alcanzar ≥ 85 % en cada archivo.
- **Métrica que mejora:** `cobertura.total` (objetivo: de 87,87 % → ≥ 92 %) y `cobertura.por_archivo` para los 5 archivos críticos.

---

### Acción 3 — Refactorizar las 10 funciones Rango C para mejorar mantenibilidad 🟠
**Prioridad:** Alta | **Sprint objetivo:** Próximos 2 sprints

- Comenzar por `_sintetizar` (CC=16) y `_pronostico` (CC=16) aplicando el principio de responsabilidad única.
- Para las funciones `intentar` repetidas en múltiples skills: diseñar un patrón de despacho centralizado (p. ej. diccionario de handlers) reutilizable.
- Verificar que la cobertura no retroceda tras la refactorización (gate en CI: cobertura ≥ 87 %).
- **Métrica que mejora:** `complejidad.maxima` (objetivo: de 16 → ≤ 10), `mantenibilidad_promedio` (objetivo: de 68,56 → ≥ 75) y `porcentaje_A_B` (objetivo: de 94,63 % → ≥ 98 %).

---

### Acción 4 — Formalizar el proceso de revisión de código para elevar la eficacia de revisión 🟠
**Prioridad:** Media-Alta | **Sprint objetivo:** Implementar como proceso permanente desde ya

- Crear un checklist de PR obligatorio: manejo de excepciones, tipado estático (`mypy`), cobertura de ramas, ausencia de lógica de negocio en la capa de presentación.
- Exigir al menos un revisor diferente al autor para todo PR que toque módulos con CC ≥ 10 o cobertura < 85 %.
- Registrar defectos encontrados en revisión para medir la mejora.
- **Métrica que mejora:** `eficacia_revision.porcentaje` (objetivo: de 13,04 % → ≥ 30 %) y `defectos_por_fase.revision` (objetivo: capturar ≥ 7/23 defectos en revisión en el próximo ciclo).

---

### Acción 5 — Reducir el MTTD con monitoreo activo en runtime 🟡
**Prioridad:** Media | **Sprint objetivo:** Próximos 2 sprints

- Integrar una herramienta de observabilidad (p. ej. Sentry, OpenTelemetry + Grafana) para capturar excepciones no controladas en producción en tiempo real.
- Configurar alertas automáticas en GitHub Actions ante fallos de cualquier paso del pipeline.
- Revisar los 9 `xfail` y convertir en issues con criterio de aceptación para el siguiente ciclo.
- **Métrica que mejora:** `mttd_horas` (objetivo: de 334,65 h → ≤ 48 h), lo que a su vez mejorará el costo de corrección al detectar antes.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas

| Técnica | Estimado (h) | Real (h) | Error absoluto | Error % |
|---|---|---|---|---|
| Juicio de expertos — Alumno | 102,0 | 122,0 | 20,0 h | 16,39 % |
| Juicio de expertos — IA (Claude) | 119,0 | 122,0 | 3,0 h | 2,46 % |
| **Juicio de expertos — Promedio** | **110,5** | **122,0** | **11,5 h** | **9,43 %** |
| **Tres puntos (PERT)** | **114,68** | **122,0** | **7,32 h** | **6,00 %** |
| Puntos de función | 146,38 | 122,0 | 24,38 h | 19,98 % |
| Análoga | 195,8 | 122,0 | 73,8 h | 60,49 % |

### Técnica más cercana: **Tres Puntos / PERT** (error 6,00 %)

La estimación por **Tres Puntos PERT** fue la más precisa, con solo **7,32 horas de desviación** sobre las 122 reales. Esto se explica por varias razones:

1. **Captura la asimetría del esfuerzo real**: al incorporar escenarios optimista (O), más probable (M) y pesimista (P), el PERT modela naturalmente la tendencia de los proyectos de software a desviarse hacia el exceso (todos los sprints se desviaron positivamente excepto los de corrección y calidad, que son más predecibles). La fórmula `(O + 4M + P) / 6` pondera el caso más probable sin ignorar los extremos.

2. **El rango del 95 % (104–125 h) contenía el valor real (122 h)**: esto valida estadísticamente el modelo; el valor real cayó en el percentil ~86 del intervalo estimado, coherente con un proyecto que sistemáticamente subestimó en sus sprints tempranos.

3. **Contraste con la estimación análoga**: la técnica análoga sobreestimó un 60 % porque el factor de ajuste (+10 %) aplicado sobre el proyecto de referencia Easy Learning fue insuficiente para capturar la diferencia cualitativa real entre un CRUD C#/MySQL y un sistema de voz con múltiples LLMs externos; el factor real habría sido cercado a 1,7× en SLOC y complejidad.

4. **El juicio de la IA (Claude) fue excepcionalmente preciso** (2,46 % de error), pero se trata de un único experto con visibilidad del código fuente; en contextos reales sin esa visibilidad, el PERT es la técnica reproducible y robusta recomendada para proyectos con integraciones externas de alta incertidumbre como Azmuth.

> **Recomendación para futuros proyectos:** usar Three-Point PERT como técnica base, complementada con juicio experto para validar los valores M y P de módulos con APIs de terceros, donde la incertidumbre tiende a ser subestimada sistemáticamente.
