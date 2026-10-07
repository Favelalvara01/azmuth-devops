## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Norma de referencia:** ISO/IEC 25010 · ISO/IEC 25023
**Fecha del informe:** 2026-10-07 · Auditor: IA QA

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **67 / 100**. La base de código muestra solidez en fiabilidad técnica inmediata (MTTR de 49 min, 109/112 pruebas en verde) y una complejidad ciclomática aceptable en su mayoría, pero presenta brechas críticas en la eficacia de detección temprana de defectos (DRE 53 %), cobertura insuficiente en módulos clave (`main.py` 27,95 %, `voice.py` 60 %) y dos funciones en rango D que concentran riesgo estructural. **No se recomienda la liberación a producción en el estado actual**; se requiere cerrar los 5 defectos abiertos y elevar la cobertura antes de un *go-live* formal.

---

## Idoneidad funcional

### Completitud funcional
De las 112 pruebas definidas, **109 aprueban** (97,32 %) y 3 están marcadas como `xfail` (defectos conocidos aceptados temporalmente). Esto indica que la funcionalidad especificada está mayoritariamente implementada. No obstante, `app_desktop.py` y `skills/interfaz.py` tienen cobertura **0 %**, lo que significa que sus rutas de ejecución no están validadas por ninguna prueba automatizada; la completitud funcional de esos módulos es **no verificable**.

### Corrección funcional
Hay **5 defectos abiertos** (2,43 por KLOC) distribuidos en archivos de alta actividad del usuario (`main.py` concentra 4 defectos totales). La tasa de defectos totales de **7,29 / KLOC** supera el umbral de referencia industrial típico para software de calidad media (≤ 5 / KLOC), siendo el Sprint 1 "Núcleo de voz" el más defectuoso con **17,48 / KLOC**.

### Pertinencia funcional
El análisis estático Ruff detecta **42 hallazgos**: 6 importaciones no utilizadas (`F401`), 1 f-string sin interpolación (`F541`) y 35 advertencias de estilo (`W292`, `E501`). Ninguno de estos es un error de ejecución crítico, pero las importaciones fantasma en `main.py`, `skills/web.py` y `voice.py` indican código de scaffolding no depurado que puede generar confusión funcional.

| Indicador | Valor | Umbral saludable | Estado |
|---|---|---|---|
| Pruebas aprobadas | 109 / 112 (97,32 %) | ≥ 95 % | ✅ |
| Defectos totales / KLOC | 7,29 | ≤ 5,0 | ⚠️ |
| Defectos abiertos / KLOC | 2,43 | ≤ 1,0 | ❌ |
| Cobertura global | 72,52 % | ≥ 80 % | ⚠️ |
| Módulos sin cobertura | 2 (0 %) | 0 | ❌ |

---

## Fiabilidad

### Madurez
El **DRE (Defect Removal Effectiveness)** es de **53,33 %**, lo que significa que sólo la mitad de los defectos fue detectada antes de llegar a producción. El estándar industrial para liberación controlada exige DRE ≥ 85 %. De los **4 defectos graves totales**, **ninguno fue detectado en pruebas** (0 / 4); todos escaparon a producción, lo cual es el indicador de fiabilidad más preocupante del proyecto.

### Disponibilidad
No se reportan tiempos de caída de servicio medibles en el pipeline, y los 109 casos de prueba pasan con un tiempo de ejecución de **2,69 segundos**, lo que refleja un sistema ligero y con buena disponibilidad durante prueba. Sin embargo, la cobertura baja de `main.py` (27,95 %) deja sin validar la lógica principal del bucle de escucha.

### Tolerancia a fallos
Los 3 casos `xfail` indican que hay defectos conocidos con comportamiento esperado documentado, lo que es una práctica positiva. Sin embargo, la ausencia de pruebas para `app_desktop.py` y `skills/interfaz.py` implica que las rutas de manejo de errores en la capa de interfaz gráfica no están validadas.

### Recuperabilidad

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** | 279,62 h (11,65 días) | Detección muy lenta; los defectos viven ~12 días antes de descubrirse |
| **MTTR** | 0,82 h (49 min) | Excelente; una vez detectado, la corrección es rápida |
| **DRE** | 53,33 % | Crítico; más de la mitad escapa a producción |
| Defectos en producción | 7 de 15 (46,67 %) | Inaceptable para liberación |

El MTTR de 49 minutos es destacable y refleja buena capacidad de respuesta del equipo. El problema no es la corrección, sino la **detección tardía**: un MTTD de casi 12 días combinado con 7 defectos en producción sugiere que el pipeline de pruebas no cubre los flujos de usuario real.

---

## Mantenibilidad

### Índice de mantenibilidad
El **índice promedio de mantenibilidad es 72,97 / 100**, que se clasifica como **moderado-bueno** pero por debajo del umbral recomendado de 80 para sistemas en evolución activa.

### Distribución de complejidad ciclomática

| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Trivial, sin riesgo | 72 | 75,0 % |
| **B** (6–10) | Baja complejidad | 13 | 13,54 % |
| **C** (11–15) | Complejidad moderada, revisar | 9 | 9,37 % |
| **D** (16–25) | Alta complejidad, refactorizar | 2 | 2,08 % |
| **E** (26–50) | Muy alta, riesgo elevado | 0 | — |
| **F** (> 50) | Crítica, reescribir | 0 | — |

El **88,54 % de las funciones está en rango A-B**, lo cual es positivo. Sin embargo, la concentración de complejidad en pocas funciones crea puntos únicos de fragilidad.

### Funciones a refactorizar (priorizadas)

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 44 | 27 | **D** | Descomponer en un dispatcher por tipo de acción usando diccionario de handlers |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | **D** | Extraer cada bloque de intención en su propia función; aplicar patrón Command |
| 🟠 3 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Separar lógica de parsing de la de persistencia |
| 🟠 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Reducir anidamiento con guardas (*early return*) |
| 🟠 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Ídem patrón *early return* |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 115 | 12 | C | Extraer condiciones compuestas a funciones con nombre semántico |
| 🟡 7 | `main.py` | `escuchar` | 103 | 12 | C | Separar lógica de reconocimiento de la de despacho |
| 🟡 8 | `skills/memoria.py` | `intentar` | 61 | 12 | C | Refactorizar ramas de if/elif a tabla de comandos |
| 🟡 9 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 | C | Extraer sub-funciones de notificación |
| 🟡 10 | `skills/web.py` | `intentar` | 54 | 12 | C | Aplicar misma estrategia que otras skills |

> **Nota transversal:** el patrón `intentar` repetido con alta complejidad en múltiples skills sugiere una abstracción base deficiente. Se recomienda revisar si la interfaz `Skill` podría dividir la función en `parsear()`, `validar()` y `ejecutar()`.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos graves escapan a producción (DRE 53 %, 0/4 graves detectados en pruebas) | **Alta** | **Crítico** | Añadir casos de prueba para los 4 defectos graves; implementar smoke tests de integración en el pipeline de CI |
| `main.py` con 27,95 % de cobertura falla en flujos de usuario reales | **Alta** | **Alto** | Crear pruebas de integración end-to-end para el bucle `escuchar`; usar mocks de `voice.py` |
| Funciones `ejecutar_accion` (CC=27) y `intentar` de aplicaciones (CC=24) introducen regresiones al modificarse | **Media** | **Alto** | Refactorizar antes de añadir nuevas funcionalidades; cubrir con pruebas de caracterización previas al refactor |
| `app_desktop.py` y `skills/interfaz.py` con cobertura 0 % ocultan fallos de UI | **Media** | **Medio** | Implementar pruebas con `pytest-qt` o similares; al menos incluir pruebas de humo de la interfaz |
| MTTD de 11,65 días permite acumulación silenciosa de defectos | **Media** | **Alto** | Activar alertas automáticas en GitHub Issues por fallos de pipeline; revisar logs diariamente en período de estabilización |
| 42 hallazgos Ruff sin corregir degradan la legibilidad y ocultan bugs | **Alta** | **Bajo** | Integrar `ruff --fix` como paso bloqueante en el pipeline CI; 28 son autocorregibles |
| Desviación del 25 % en esfuerzo total (Sprint 5 con 60 % de desviación) | **Media** | **Medio** | Usar velocidad histórica (7,86 pts/sprint) para replanning; revisar estimaciones de módulos con APIs externas |
| Importaciones no usadas en `voice.py`, `main.py`, `skills/web.py` indican código no consolidado | **Baja** | **Bajo** | Ejecutar `ruff --fix` y revisar si las dependencias eliminadas afectan funcionalidad latente |

---

## Plan de mejora

Las acciones están ordenadas por impacto inmediato en la calidad liberada.

### Acción 1 — Cerrar los 5 defectos abiertos y cubrir los 4 defectos graves (Prioridad: 🔴 Crítica)
**Qué hacer:** Identificar y crear casos de prueba que reproduzcan los 4 defectos graves que escaparon a producción; resolver los 5 issues abiertos antes de cualquier tag de release.
**Métrica que mejora:** DRE (53,33 % → meta ≥ 85 %) · Defectos abiertos/KLOC (2,43 → 0).

### Acción 2 — Elevar la cobertura de `main.py` y `voice.py` (Prioridad: 🔴 Crítica)
**Qué hacer:** Desarrollar pruebas unitarias con mocks de `speech_recognition` y `elevenlabs` para las rutas de `escuchar()` en `main.py`; añadir pruebas de integración para `voice.py`. Apuntar a ≥ 70 % en ambos.
**Métrica que mejora:** Cobertura global (72,52 % → meta ≥ 80 %) · MTTD (reducción esperada al detectar en CI antes de producción).

### Acción 3 — Refactorizar `ejecutar_accion` y `intentar` de aplicaciones (Prioridad: 🟠 Alta)
**Qué hacer:** Antes de refactorizar, generar pruebas de caracterización (*golden tests*). Luego aplicar el patrón dispatcher/Command para reducir CC < 10 en ambas funciones. Verificar que las pruebas existentes siguen en verde.
**Métrica que mejora:** Complejidad ciclomática máxima (27 → < 10) · Índice de mantenibilidad (72,97 → meta ≥ 80) · Porcentaje A-B (88,54 % → meta ≥ 95 %).

### Acción 4 — Integrar Ruff como gate bloqueante en GitHub Actions (Prioridad: 🟠 Alta)
**Qué hacer:** Añadir el paso `ruff check . --fix` al workflow de CI; ejecutar `ruff --fix` local para resolver los 28 errores autocorregibles; revisar manualmente los 14 restantes. Configurar que cualquier fallo de Ruff bloquee el merge.
**Métrica que mejora:** Hallazgos de análisis estático (42 → 0) · Mantenibilidad (elimina deuda técnica superficial sin cambios funcionales).

### Acción 5 — Implementar pruebas de humo para `app_desktop.py` y `skills/interfaz.py` (Prioridad: 🟡 Media)
**Qué hacer:** Usar `pytest-qt` o `unittest.mock` para simular el ciclo de vida de la ventana de escritorio y los métodos de `skills/interfaz.py`; al menos 5 casos de prueba de humo que validen inicialización, respuesta a comandos básicos y cierre limpio.
**Métrica que mejora:** Cobertura de `app_desktop.py` y `skills/interfaz.py` (0 % → meta ≥ 50 %) · Completitud funcional verificable.

---

## Estimación (juicio experto de la IA)

**Técnica más cercana a las 90 horas reales: Tres Puntos (PERT)**

El método de **Tres Puntos** estimó **81,85 h** con un rango al 95 % de confianza de **[72,26 – 91,44 h]**. Las **90 horas reales quedan dentro de ese intervalo**, a menos de 2 horas del límite superior, lo que lo convierte en el estimado con mayor precisión predictiva de todos los métodos evaluados.

**Por qué fue el más preciso:**

1. **Capturó la incertidumbre asimétrica:** Al definir escenarios optimista (O), más probable (M) y pesimista (P) por módulo, el método absorbió la variabilidad real del proyecto —especialmente en los módulos con APIs externas (Interfaz y servidor, Núcleo de voz) donde el pesimista era significativamente mayor que el más probable, reflejando el riesgo de integración que efectivamente materializó su impacto (Sprint 5 con 60 % de desviación).

2. **La desviación estándar total de 4,79 h** era una señal explícita de que el proyecto tenía incertidumbre real; el intervalo de confianza del 95 % fue honesto con esa varianza, algo que el juicio de expertos promedio (80,33 h) y la estimación análoga (100,66 h) no expresaron con la misma claridad.

3. El **juicio del alumno (72 h)** subestimó en 18 h porque tendió al optimismo —patrón clásico del desarrollador que conoce el dominio pero no calibra los tiempos de integración y depuración. La **estimación análoga (100,66 h)** sobreestimó porque el factor de ajuste del 10 % quizás fue conservador pero la productividad base de Easy Learning (22,5 SLOC/h) no reflejó bien la complejidad de las APIs de voz.

4. El método de **Puntos de función (101,12 h)** sobreestimó porque el VAF de 1,07 y la tasa de 0,45 h/PF son parámetros calibrados para equipos con más experiencia en el dominio; para un alumno, la curva de aprendizaje en APIs de IA eleva la productividad aparentemente menor.

> **Recomendación para proyectos futuros:** usar Tres Puntos como método base y refinarlo con la velocidad histórica medida (7,86 pts/sprint, ~1,38–2,0 h/punto según el módulo) para generar rangos de sprint más confiables.

---

*Informe generado con base exclusivamente en los datos del pipeline proporcionados. Ninguna cifra ha sido inferida fuera del conjunto de datos.*
