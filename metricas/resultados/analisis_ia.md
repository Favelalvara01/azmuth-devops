## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Informe de Auditoría de Calidad — Proyecto **Azmuth**
> ISO/IEC 25010 · ISO/IEC 25023 | Generado con datos de: 2026-10-08 04:19

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **78 / 100**. Sus fortalezas son una cobertura de pruebas del 86,58 %, cero defectos abiertos, suite verde de 315/315 casos y análisis estático sin hallazgos (Ruff). Sin embargo, la baja Eficacia de Detección en Pruebas (DRE = 44,44 %) —que dejó 10 de 18 defectos escapar a producción— y la cobertura crítica de módulos clave (`voice.py` 72,88 %, `app_desktop.py` 0 %, `cerebro.py` 75 %) representan riesgos residuales que deben subsanarse antes de considerarse **listo para liberación en producción sin restricciones**; se recomienda una **liberación controlada (beta/piloto)** con monitoreo activo mientras se ejecuta el plan de mejora.

---

## Idoneidad funcional

### Completitud funcional
| Indicador | Valor |
|---|---|
| Casos de prueba totales | 315 |
| Casos aprobados | 315 (100 %) |
| Defectos abiertos | **0** |
| Defectos conocidos pendientes (`xfail`) | 0 |

Las 315 pruebas cubren la totalidad de los módulos declarados. La ausencia de defectos abiertos y de `xfail` indica que todas las funcionalidades comprometidas para esta versión están implementadas y verificadas.

### Corrección funcional
- **Densidad de defectos total:** 5,77 defectos/KLOC — valor aceptable para un proyecto de esta naturaleza, pero el sprint 1 ("Núcleo de voz") alcanzó 13,74/KLOC, lo que señala debilidad histórica en el módulo más crítico.
- La distribución de defectos por fase muestra que **10 de 18 (55,6 %)** llegaron a producción, lo que compromete la corrección percibida por el usuario final durante el desarrollo.

### Pertinencia funcional
- Los puntos de función ajustados (325,28 PF) con factores de **comunicación de datos (4)**, **eficiencia del usuario final (4)** y **facilidad de cambio (4)** confirman que el alcance es coherente con un asistente de voz con IA integrada.
- `app_desktop.py` tiene **cobertura 0 %**, lo que significa que su comportamiento en producción no está validado por las pruebas automatizadas actuales — brecha funcional directa.

---

## Fiabilidad

### Métricas clave del proceso

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** | 233,09 h (9,71 días) | Tiempo promedio para detectar un defecto. Alto: los defectos tardan casi dos semanas en detectarse. |
| **MTTR** | 3,9 h (234 min) | Una vez detectado, la corrección es ágil. Indica capacidad de respuesta buena. |
| **DRE** | **44,44 %** | Solo 4 de 9 defectos pre-producción fueron capturados por las pruebas. Por debajo del umbral recomendado (≥ 85 %). |
| Defectos en producción | 10 / 18 (55,6 %) | Más de la mitad escaparon al entorno productivo. |
| Defectos graves en pruebas | 0 / 4 | **Los 4 defectos graves no fueron detectados en pruebas.** Riesgo de fiabilidad severo. |

### Madurez
- Con 0 defectos abiertos y MTTR de ~4 h el código está **estabilizado** al momento del cierre del sprint.
- El DRE de 44,44 % indica que el proceso de pruebas **no es suficientemente maduro** para garantizar fiabilidad en versiones futuras sin refuerzo.

### Disponibilidad / Tolerancia a fallos / Recuperabilidad
- El pipeline DevOps (GitHub Actions + Docker) da soporte a la recuperación automatizada, pero no se reportan métricas de uptime ni circuit-breakers para las APIs externas (Claude, ElevenLabs).
- La cobertura del 72,88 % en `voice.py` deja caminos de fallo sin probar en el motor central del asistente.

---

## Mantenibilidad

### Índice de mantenibilidad promedio: **72,02 / 100**
> Rango aceptable (≥ 65), pero con margen de mejora antes de considerarse "bueno" (≥ 85).

### Complejidad ciclomática — Escala de rangos

| Rango | CC | Significado | Funciones |
|---|---|---|---|
| **A** | 1 – 5 | Simple, bajo riesgo | 180 (84,1 %) |
| **B** | 6 – 10 | Moderada, manejable | 22 (10,3 %) |
| **C** | 11 – 15 | Compleja, requiere atención | 12 (5,6 %) |
| **D** | 16 – 20 | Alta complejidad | 0 |
| **E** | 21 – 25 | Muy alta | 0 |
| **F** | > 25 | Crítica / inaceptable | 0 |

**Promedio:** 3,44 (rango A) · **Mediana:** 2,0 · **Máxima:** 15

El 94,39 % de las funciones caen en A–B. No existen funciones en D, E o F. Sin embargo, las **12 funciones en rango C** son candidatas prioritarias a refactorizar:

### Funciones a refactorizar (Top 10 por complejidad)

| Archivo | Función | Línea | CC | Riesgo |
|---|---|---|---|---|
| `skills/apps_instaladas.py` | `intentar` | 213 | **15** | Alto — duplicado de nombre, lógica ramificada |
| `skills/recordatorios.py` | `intentar` | 96 | **14** | Alto — gestión de recordatorios compleja |
| `skills/apps_instaladas.py` | `resolver` | 169 | **13** | Alto — resolución de apps instaladas |
| `skills/multimedia.py` | `intentar` | 31 | **13** | Alto — control multimedia |
| `skills/pestanas.py` | `intentar` | 33 | **13** | Alto — gestión de pestañas |
| `cerebro.py` | `actualizar_perfil_si_toca` | 205 | **12** | Medio-alto — lógica de perfil de usuario |
| `skills/memoria.py` | `intentar` | 61 | **12** | Medio-alto — sistema de memoria |
| `skills/recordatorios.py` | `revisar_pendientes` | 170 | **12** | Medio-alto — revisión de pendientes |
| `skills/web.py` | `intentar` | 53 | **12** | Medio-alto — acceso web |
| `cerebro.py` | `preguntar` | 104 | **11** | Medio — interacción con IA |

> **Patrón detectado:** El nombre de función `intentar` aparece en múltiples skills con CC elevada. Se recomienda revisar si existe una abstracción común que pueda extraerse a una clase base o decorador.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (44,44 %): defectos graves escapan a producción** | Alta | Crítico | Diseñar pruebas de integración y de casos límite específicas para los 4 defectos graves; establecer meta DRE ≥ 85 % para el próximo ciclo |
| **`app_desktop.py` con cobertura 0 %** | Alta | Alto | Agregar pruebas unitarias y de humo para el módulo de escritorio antes del siguiente release |
| **MTTD de 9,71 días: detección tardía de defectos** | Alta | Alto | Implementar monitoreo continuo con alertas automáticas (logs estructurados + Sentry o equivalente) |
| **`voice.py` y `cerebro.py` con cobertura < 80 %** | Media | Alto | Incrementar cobertura a ≥ 90 % con mocks de APIs externas (Claude, ElevenLabs) |
| **Dependencia de APIs externas sin circuit-breaker** | Media | Alto | Implementar patrón circuit-breaker y fallback local cuando las APIs de IA/voz no respondan |
| **12 funciones en rango C sin pruebas exhaustivas** | Media | Medio | Refactorizar las 5 funciones con CC ≥ 13 en el próximo sprint; verificar cobertura de ramas |
| **Desviación del 19,61 % en horas totales (Sprint 5: 60 %)** | Media | Medio | Incorporar buffer de riesgo del 20 % en sprints con integración de UI/servidor; revisión de estimación tras sprint 3 |
| **Densidad de defectos en Sprint 1 (13,74/KLOC)** | Baja | Medio | Aplicar revisión de código (code review) obligatoria en el núcleo de voz para versiones futuras |

---

## Plan de mejora

Las siguientes 5 acciones están ordenadas por **prioridad descendente** con enfoque preventivo:

### 1. 🔴 Elevar el DRE al ≥ 85 % mediante pruebas de integración y de defectos graves
**Métrica que mejora:** `dre_porcentaje` (actualmente 44,44 % → meta ≥ 85 %)

- Crear casos de prueba que repliquen los 4 defectos graves históricamente detectados en producción.
- Añadir pruebas de integración end-to-end para el flujo completo: entrada de voz → cerebro → skill → respuesta.
- Establecer un **gate de calidad** en GitHub Actions que bloquee el merge si el DRE del sprint cae por debajo del umbral.

### 2. 🔴 Cubrir `app_desktop.py` y elevar `voice.py` / `cerebro.py` por encima del 85 %
**Métrica que mejora:** `cobertura.total` (86,58 % → meta ≥ 90 %) y `cobertura.por_archivo` en los tres módulos críticos

- Usar `unittest.mock` / `pytest-mock` para simular el entorno de escritorio Windows sin dependencia de hardware.
- Crear fixtures que emulen respuestas de ElevenLabs y Claude para probar `voice.py` en modo offline.
- Apuntar a cobertura de **ramas** (`--cov-branch`) y no solo de líneas.

### 3. 🟠 Refactorizar las 5 funciones con CC ≥ 13
**Métrica que mejora:** `complejidad.maxima` (15 → meta ≤ 10), `mantenibilidad_promedio` (72,02 → meta ≥ 80)

- Extraer sub-funciones o usar el patrón **Command/Strategy** para cada intención reconocida dentro de `intentar`.
- Crear una clase base `Skill` con método `intentar` abstracto que reduzca la duplicación lógica entre skills.
- Validar que la refactorización no rompa cobertura existente (pruebas de regresión automatizadas).

### 4. 🟠 Reducir el MTTD mediante monitoreo continuo y alertas tempranas
**Métrica que mejora:** `mttd_horas` (233,09 h → meta < 72 h)

- Integrar logging estructurado (JSON) con niveles `WARNING`/`ERROR` capturados por un sistema de observabilidad (Sentry, Datadog Free, o Grafana Loki).
- Configurar alertas automáticas en GitHub Actions para fallos de producción críticos.
- Añadir un healthcheck periódico que verifique la disponibilidad de las APIs externas.

### 5. 🟡 Implementar circuit-breaker y fallback para dependencias externas
**Métrica que mejora:** `disponibilidad` (no reportada actualmente → añadir SLA interno ≥ 99 % en entornos offline)

- Usar la librería `tenacity` (reintentos con backoff exponencial) para llamadas a Claude y ElevenLabs.
- Definir un modo degradado: si la API de voz falla, responder en texto; si la IA falla, usar respuestas en caché o plantillas.
- Documentar el comportamiento esperado en el `README` y añadir pruebas del modo degradado.

---

## Estimación (juicio experto de la IA)

### Resumen comparativo de técnicas

| Técnica | Total estimado (h) | Desviación vs. 122 h reales | Error % |
|---|---|---|---|
| Alumno desarrollador | 102,0 | −20,0 h | −16,4 % |
| Compañero con experiencia | 117,0 | −5,0 h | −4,1 % |
| **IA (Claude) — juicio experto** | **119,0** | **−3,0 h** | **−2,5 %** |
| **Juicio experto promediado** | **112,66** | **−9,34 h** | **−7,7 %** |
| **Tres puntos (PERT)** | **114,68** | **−7,32 h** | **−6,0 %** |
| Análoga | 152,53 | +30,53 h | +25,0 % |
| Puntos de función | 146,38 | +24,38 h | +20,0 % |

### Técnica más cercana y razonamiento

La **estimación del experto individual IA (Claude) con 119 h** fue la más próxima a las 122 h reales, con un error de apenas **2,5 %**. Le sigue muy de cerca el **Compañero con experiencia (117 h, −4,1 %)**.

**¿Por qué el juicio experto de IA fue el más preciso?**

1. **Análisis directo del código:** Al basar la estimación en la lectura del código real (no en analogías o conteo de puntos abstractos), la IA capturó la complejidad inherente de integrar APIs externas, manejo de estado de voz y control del sistema operativo, que los métodos paramétricos subestiman.

2. **Corrección al alza respecto al alumno:** El alumno estimó 102 h (el más bajo), probablemente por sesgo de optimismo típico del desarrollador que creó el sistema. La IA, sin ese sesgo emocional, ajustó hacia arriba en los módulos más inciertos.

3. **Limitaciones de los métodos paramétricos:** La estimación análoga (152 h) y por puntos de función (146 h) sobreestimaron significativamente porque el proyecto de referencia (Easy Learning, CRUD en C#/MySQL) y la tabla de pesos estándar de PF no capturan bien la eficiencia Python ni el reúso de frameworks de IA; además, el factor de ajuste VAF de 1,07 no penalizó suficientemente la complejidad de integración de voz.

4. **Tres puntos PERT (114,68 h, −6 %):** El rango al 95 % de confianza **[104 – 125 h]** sí contenía las 122 h reales, lo que confirma su valor como técnica de gestión de riesgo aunque el punto central subestima ligeramente. Para futuras versiones se recomienda combinar **tres puntos PERT + juicio experto revisado** como técnica híbrida más robusta.

---

*Auditoría realizada sobre datos del pipeline del 2026-10-08. Las métricas no disponibles en los datos (uptime, SLA de APIs) deben instrumentarse en el próximo ciclo de desarrollo.*
