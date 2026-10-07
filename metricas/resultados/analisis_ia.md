## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Norma:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-07 06:26 | **Auditor:** IA QA

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **67 / 100**. La base de pruebas automatizadas es sólida (147/150 pasando en 6,67 s) y el MTTR es excelente (49 min), pero el **DRE del 53,33 %** indica que más de la mitad de los defectos escapan a la fase de pruebas y llegan a producción, el **MTTD supera los 11 días**, la cobertura de dos módulos críticos es **0 %**, y quedan **5 defectos abiertos** con concentración en `main.py`. **El proyecto _no_ cumple los criterios mínimos para una liberación a producción** sin antes cerrar los defectos abiertos y elevar la cobertura de los módulos sin instrumentación.

---

## Idoneidad funcional

| Sub-característica | Indicador | Valor | Valoración |
|---|---|---|---|
| **Completitud funcional** | Pruebas aprobadas / total | 147 / 150 (98 %) | ✅ Aceptable |
| **Completitud funcional** | Defectos abiertos | 5 (1,95 / KLOC) | ⚠️ Requiere atención |
| **Corrección funcional** | Cobertura global de pruebas | 76,28 % | ⚠️ Por debajo del umbral recomendado (≥ 80 %) |
| **Corrección funcional** | Módulos con cobertura 0 % | `app_desktop.py`, `skills/interfaz.py` | ❌ Crítico |
| **Corrección funcional** | `main.py` cobertura | 26,67 % con 4 defectos abiertos | ❌ Crítico |
| **Pertinencia funcional** | Defectos en producción | 7 de 15 (46,67 %) | ⚠️ Alto |
| **Pertinencia funcional** | Defectos reparados | 10 / 15 (66,67 %) | ⚠️ Pendiente |

**Observaciones:**
- Los 3 defectos marcados como `xfail` reflejan comportamientos conocidos que deben documentarse formalmente como limitaciones o convertirse en ítems de backlog priorizados.
- La concentración de 4 defectos abiertos en `main.py` (punto de entrada de la aplicación) es el riesgo funcional más inmediato.
- El análisis estático de Ruff detectó **43 errores**, de los cuales 4 son importaciones sin uso (`F401`) — código muerto que reduce la confiabilidad de las dependencias declaradas — y 1 f-string vacío (`F541`) en `skills/aplicaciones.py` que puede generar salida incorrecta al usuario.

---

## Fiabilidad

| Sub-característica | Métrica | Valor | Interpretación |
|---|---|---|---|
| **Madurez** | Densidad de defectos totales | 5,84 / KLOC | ⚠️ Elevado (umbral recomendado ≤ 3 / KLOC) |
| **Madurez** | Densidad de defectos abiertos | 1,95 / KLOC | ⚠️ Requiere reducción antes de release |
| **Madurez** | Sprint con mayor densidad | Sprint 1 — Núcleo de voz: 16,72 / KLOC | ❌ Muy alto |
| **Disponibilidad** | Pruebas fallidas en CI | 0 / 150 | ✅ Pipeline estable |
| **Tolerancia a fallos** | DRE (Defect Removal Effectiveness) | 53,33 % | ❌ Crítico (≥ 85 % recomendado) |
| **Tolerancia a fallos** | Defectos graves detectados en pruebas | 0 de 4 | ❌ Todos los graves escaparon |
| **Recuperabilidad** | MTTR | 0,82 h (49 min) | ✅ Excelente capacidad de corrección |
| **Recuperabilidad** | MTTD | 279,62 h (11,65 días) | ❌ Detección muy tardía |

**Análisis DRE:**

```
DRE = Defectos detectados en pruebas / (Defectos en pruebas + Defectos en producción)
    = 5 / (5 + 7) × 100 = 41,67 %   [fórmula estricta pre-release]
    = 53,33 %                          [fórmula con base en totales, según datos]
```

Ambos valores están muy por debajo del estándar de industria (≥ 85 %). El hecho de que **los 4 defectos graves hayan escapado todos a producción** es la señal de fiabilidad más crítica del proyecto.

El MTTD de casi 12 días indica ausencia de monitoreo activo o alertas automatizadas en el entorno de ejecución, lo que contrasta favorablemente con el MTTR de 49 min (el equipo resuelve rápido una vez detectado el problema).

---

## Mantenibilidad

### Interpretación de rangos de complejidad ciclomática

| Rango | CC | Significado | Funciones | % |
|---|---|---|---|---|
| **A** | 1–5 | Bajo riesgo, fácil de probar | 117 | 79,05 % |
| **B** | 6–10 | Riesgo moderado | 17 | 11,49 % |
| **C** | 11–15 | Riesgo alto, refactorización recomendada | 12 | 8,11 % |
| **D** | 16–25 | Riesgo muy alto, refactorización urgente | 2 | 1,35 % |
| **E** | 26–50 | Crítico | 0 | 0 % |
| **F** | > 50 | Inmanejable | 0 | 0 % |

El **90,54 % del código está en rangos A–B**, lo cual es positivo. Sin embargo, los rangos C y D concentran las funciones de mayor volumen lógico y mayor exposición a defectos.

### Funciones a refactorizar (priorizadas)

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción sugerida |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 161 | 27 | **D** | Aplicar patrón *Command* o tabla de despacho; descomponer en handlers por tipo de acción |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | **D** | Extraer estrategias de intento en subclases o funciones auxiliares; reducir anidamiento |
| 🟠 3 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | C | Separar lógica de búsqueda y lanzamiento |
| 🟠 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Extraer validaciones de fecha/hora a funciones puras |
| 🟠 5 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | C | Simplificar ramificación de resolución de rutas |
| 🟡 6 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Separar control de reproducción y búsqueda de media |
| 🟡 7 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Tabla de despacho para acciones de pestaña |
| 🟡 8 | `cerebro.py` | `actualizar_perfil_si_toca` | 136 | 12 | C | Extraer condiciones de actualización a predicados |
| 🟡 9 | `main.py` | `escuchar` | 104 | 12 | C | Descomponer bucle de escucha (también tiene 4 defectos abiertos) |
| 🟡 10 | `skills/memoria.py` | `intentar` | 61 | 12 | C | Separar consulta, formateo y respuesta |

**Índice de mantenibilidad promedio: 71,37 / 100** — clasificado como **"Moderado"** (umbral recomendado ≥ 80). El patrón recurrente de funciones llamadas `intentar` con alta CC sugiere que la convención de skill no impone límites de responsabilidad.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Los 4 defectos graves no detectados en pruebas provocan fallo en producción | **Alta** | **Crítico** | Crear casos de prueba específicos para los 4 defectos graves; bloquear release hasta DRE ≥ 80 % |
| `main.py` con 26,67 % de cobertura y 4 defectos abiertos falla en el flujo principal | **Alta** | **Alto** | Añadir pruebas de integración del ciclo `escuchar → procesar → responder`; refactorizar `escuchar` (CC=12) |
| `app_desktop.py` y `skills/interfaz.py` sin cobertura ocultan defectos de UI/interacción | **Media** | **Alto** | Implementar pruebas con mocking de la interfaz gráfica (p. ej. `pytest-qt` o headless); meta: ≥ 60 % |
| MTTD de 11,65 días: defectos llegan a usuarios antes de ser detectados | **Alta** | **Medio** | Implementar logging estructurado + alertas automáticas en producción (Sentry o similar integrado en el pipeline) |
| `ejecutar_accion` (CC=27) y `intentar` (CC=24) generan defectos de regresión al modificarse | **Media** | **Alto** | Refactorizar antes del siguiente sprint; exigir cobertura ≥ 90 % en estas funciones post-refactor |
| 43 advertencias de Ruff no corregidas generan deuda técnica acumulada | **Alta** | **Bajo** | Activar `ruff --fix` como paso obligatorio del pipeline de CI; fallar build si hay errores no corregibles automáticamente |
| Desviación del 25 % en estimación global (y 60 % en Sprint 5) afecta planificación futura | **Media** | **Medio** | Usar PERT como técnica base en próximos proyectos; revisar velocidad real por sprint (7,86 pt/sprint) |
| Importaciones sin uso (`difflib`, `sys`, `subprocess`, `unicodedata`) en módulos críticos | **Baja** | **Bajo** | Eliminar en siguiente commit; añadir regla `F401` como error bloqueante en Ruff CI |

---

## Plan de mejora

Las siguientes acciones están ordenadas por **impacto inmediato en la calidad liberada**:

---

**Acción 1 — Prioridad CRÍTICA: Cerrar los 5 defectos abiertos antes del release**
- **Qué hacer:** Asignar los 5 defectos abiertos (4 en `main.py`, 1 en `app_desktop.py`) a resolución inmediata; los 3 `xfail` deben convertirse en bugs formales o documentarse como limitaciones conocidas con workaround.
- **Métrica que mejora:** `abiertos_por_kloc` de 1,95 → 0; DRE hacia ≥ 80 %; condición de entrada al release.

---

**Acción 2 — Prioridad ALTA: Elevar cobertura de `main.py`, `app_desktop.py` y `skills/interfaz.py`**
- **Qué hacer:** Añadir pruebas de integración para el bucle principal de `main.py` usando mocking de `voice.py` y `servidor.py`; aplicar mocking de la GUI para `app_desktop.py` y `skills/interfaz.py` con cobertura objetivo ≥ 60 % en módulos de interfaz y ≥ 70 % en `main.py`.
- **Métrica que mejora:** Cobertura global de 76,28 % → ≥ 80 %; DRE de 53,33 % → ≥ 75 %.

---

**Acción 3 — Prioridad ALTA: Refactorizar `ejecutar_accion` (CC=27) e `intentar` en `aplicaciones.py` (CC=24)**
- **Qué hacer:** Aplicar patrón *Command* o diccionario de despacho en `ejecutar_accion`; descomponer `intentar` en funciones auxiliares con responsabilidad única. Exigir cobertura ≥ 90 % post-refactor mediante prueba parametrizada.
- **Métrica que mejora:** Complejidad máxima de 27 → ≤ 10 (rango B); índice de mantenibilidad de 71,37 → objetivo ≥ 78; reducción de riesgo de regresión.

---

**Acción 4 — Prioridad MEDIA: Implementar detección proactiva de defectos en producción**
- **Qué hacer:** Integrar una solución de observabilidad (p. ej. Sentry SDK en `main.py` y `servidor.py`) con alertas automáticas; añadir health-check en el pipeline de Docker que verifique el estado del servicio de voz cada 5 min.
- **Métrica que mejora:** MTTD de 279,62 h → objetivo ≤ 48 h; permitirá calcular disponibilidad real del servicio.

---

**Acción 5 — Prioridad MEDIA: Automatizar corrección de estilo y hacer el pipeline de CI más estricto**
- **Qué hacer:** (a) Ejecutar `ruff --fix` automáticamente en pre-commit hook; (b) configurar GitHub Actions para que falle el build ante cualquier error `F401`, `F541` o `E501` no corregido automáticamente; (c) agregar umbral de cobertura mínima (`--cov-fail-under=80`) en pytest del pipeline.
- **Métrica que mejora:** Errores Ruff de 43 → 0 en cada push; cobertura garantizada ≥ 80 % como gate de merge; reducción de deuda técnica acumulada.

---

## Estimación (juicio experto de la IA)

### Comparativa frente a las 90 horas reales

| Técnica | Total estimado | Error absoluto | Error relativo |
|---|---|---|---|
| Juicio de expertos (promedio) | 80,33 h | 9,67 h | 10,7 % |
| **PERT / Tres puntos** | **81,85 h** | **8,15 h** | **9,1 %** |
| Puntos de función | 101,12 h | 11,12 h | 12,4 % |
| Analogía | 125,64 h | 35,64 h | 39,6 % |

### Técnica más acertada: **PERT (Tres Puntos)**

El método PERT con **81,85 h** fue el que más se aproximó a las 90 h reales, con un error del 9,1 %. Además, su **intervalo de confianza del 95 % (72,26 h – 91,44 h) captura el valor real de 90 h**, lo que lo convierte no solo en el estimado puntual más cercano sino también en el único con rigor estadístico demostrado.

**¿Por qué funcionó mejor?**

1. **Incorporó incertidumbre explícitamente:** Al requerir valores Optimista/Más probable/Pesimista por módulo, el método reconoció la incertidumbre de integración con APIs externas (Claude, ElevenLabs) que la analogía subestimó y el juicio de expertos promedio suavizó.

2. **El módulo más problemático fue anticipado:** Para "Interfaz y servidor" (Sprint 5, desviación real del 60 %), el PERT asignó un pesimista de 22 h y estimó 13,67 h — más cercano a las 16 h reales que las 10 h del alumno.

3. **La analogía sobreestimó** porque el factor de ajuste del +10 % fue insuficiente para compensar la diferencia de SLOC (2 570 vs 1 800) y asumió la misma productividad (22,5 SLOC/h) de un proyecto CRUD, sin considerar que la integración de voz e IA introduce tiempos de depuración no lineales.

4. **El juicio de expertos** fue competitivo (80,33 h, 10,7 % de error), especialmente la estimación de la IA (86 h, la más cercana individualmente), pero al promediar los tres expertos se diluyó hacia la subestimación del alumno. Si se hubiera usado solo la estimación del experto con mayor experiencia o la IA, el resultado habría sido similar al PERT.

> **Recomendación para proyectos futuros:** Usar PERT como técnica base, complementada con la revisión del experto más experimentado como filtro de sanidad. Registrar la velocidad real por sprint (actualmente 7,86 pt/sprint) para calibrar las estimaciones análogas con datos propios del equipo.

---

*Auditoría generada con base exclusiva en los datos del pipeline proporcionados. Ninguna cifra fue inventada fuera de los datos de entrada.*
