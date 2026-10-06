## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
*Normas ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-06 18:53*

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **64 / 100**, situándose en un nivel de calidad **condicional**: posee una base técnica sólida (88,5 % de funciones en rango A-B, MTTR de 49 minutos, suite de 112 pruebas sin fallos activos), pero presenta brechas críticas que impiden la liberación a producción en su estado actual. Las condiciones bloqueantes son: cobertura insuficiente en módulos clave (`main.py` 27,95 %, `voice.py` 60 %, `app_desktop.py` 0 %), un DRE del 53,33 % (más de la mitad de los defectos llegan a producción) y dos funciones con complejidad ciclomática en rango **D** que elevan significativamente el riesgo de regresiones. **No se recomienda la liberación hasta subsanar las acciones del Plan de Mejora con prioridad alta.**

---

## Idoneidad funcional

| Subcaracterística | Indicador | Valor | Evaluación |
|---|---|---|---|
| **Completitud funcional** | Pruebas aprobadas / total | 109 / 112 (97,3 %) | ✅ Satisfactoria |
| **Corrección funcional** | Defectos abiertos / KLOC | 2,43 por KLOC | ⚠️ Aceptable con reservas |
| **Pertinencia funcional** | Defectos `xfail` conocidos | 3 | ⚠️ Funcionalidades con comportamiento esperado incompleto |

**Análisis:**

- Con **5 defectos abiertos** de 15 totales (33,3 % sin cerrar) y una concentración de 4 defectos en `main.py` (el orquestador principal), la corrección funcional es el punto más débil de esta característica.
- Los 3 `xfail` registrados representan casos de uso cuya lógica no está completamente validada; deben tener criterios de aceptación documentados y fecha de resolución antes de liberar.
- La pertinencia es adecuada: el conjunto de skills cubre el dominio declarado (voz, IA, recordatorios, multimedia, web, contactos, notas, hábitos, sistema), y las pruebas ejercitan el 97,3 % de los casos registrados.
- `app_desktop.py` y `skills/interfaz.py` tienen **cobertura 0 %**, lo que implica que su corrección funcional es desconocida y no verificada.

---

## Fiabilidad

| Subcaracterística | Métrica | Valor | Referencia industria | Evaluación |
|---|---|---|---|---|
| **Madurez** | DRE (Defect Removal Efficiency) | 53,33 % | ≥ 85 % aceptable | 🔴 Crítico |
| **Madurez** | Defectos graves detectados en pruebas | 0 / 4 | 100 % ideal | 🔴 Crítico |
| **Disponibilidad** | Pruebas sin fallos activos | 109 / 112 | — | ✅ Bueno |
| **Tolerancia a fallos** | Defectos en producción | 7 / 15 (46,7 %) | < 15 % ideal | 🔴 Alto riesgo |
| **Recuperabilidad** | MTTR | 49 min | < 4 h estándar | ✅ Excelente |
| **Detección de fallos** | MTTD | 11,65 días | < 2 días ideal | 🟠 Mejorable |

**Análisis detallado:**

- **DRE = 53,33 %** es el indicador de mayor preocupación: significa que prácticamente la mitad de los defectos evaden el proceso de pruebas y llegan al usuario final. El estándar para proyectos de calidad aceptable es ≥ 85 %.
- Los **4 defectos graves** no fueron interceptados en ninguna fase previa a producción (0 detectados en pruebas), lo que evidencia que las pruebas actuales no ejercitan los caminos de error críticos.
- El **MTTR de 49 minutos** es sobresaliente e indica que el equipo tiene alta capacidad de respuesta una vez detectado un defecto.
- El **MTTD de 11,65 días** es elevado para un asistente de voz interactivo; refleja la baja cobertura en los módulos de entrada (`main.py`, `voice.py`) donde los defectos permanecen latentes.
- La distribución por fase muestra inversión de pirámide: `revisión 3 → pruebas 5 → producción 7`; lo deseable sería la distribución inversa.

---

## Mantenibilidad

**Escala de complejidad ciclomática (McCabe):**

| Rango | CC | Significado |
|---|---|---|
| A | 1 – 5 | Código simple, bajo riesgo |
| B | 6 – 10 | Moderado, manejable |
| C | 11 – 15 | Complejo, revisión recomendada |
| D | 16 – 25 | Alto riesgo, refactorizar |
| E | 26 – 50 | Muy alto riesgo |
| F | > 50 | No mantenible |

**Distribución del proyecto:**

| Rango | Funciones | % |
|---|---|---|
| A | 72 | 75,0 % |
| B | 13 | 13,5 % |
| C | 9 | 9,4 % |
| D | 2 | 2,1 % |
| E | 0 | — |
| F | 0 | — |

- **Promedio CC: 4,46** → Rango A global. El 88,54 % de las funciones está en rango A-B, lo que es un resultado positivo.
- **Índice de mantenibilidad promedio: 72,97 / 100** → Nivel moderado-alto (umbral recomendado ≥ 65).
- **42 advertencias Ruff** (28 autocorregibles): predominan `W292` (sin newline al final de archivo) y `E501` (líneas demasiado largas en `servidor.py`), más 5 importaciones no utilizadas (`F401`).

**Funciones prioritarias a refactorizar:**

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción sugerida |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 44 | 27 | **D** | Descomponer con patrón Command o tabla de despacho; extraer handlers por tipo de acción |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | **D** | Dividir en subfunciones por intención (abrir, cerrar, listar); reducir ramas condicionales |
| 🟠 3 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Separar la lógica de parsing de la de persistencia |
| 🟠 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Extraer casos de reproducción/pausa/volumen a métodos privados |
| 🟠 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Aplicar estrategia de tabla de acciones por comando |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 115 | 12 | C | Simplificar condiciones compuestas; extraer evaluadores de condición |
| 🟡 7 | `main.py` | `escuchar` | 103 | 12 | C | Separar la lógica de reconocimiento de voz del enrutamiento de comandos |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos graves en producción no detectados por pruebas (DRE 53,33 %, 4 graves no interceptados) | **Alta** | **Crítico** | Añadir pruebas de integración y de caminos de error para los 4 defectos graves; elevar DRE ≥ 85 % antes de liberar |
| Fallo no controlado en `ejecutar_accion` (CC=27) ante comandos de voz inesperados | **Alta** | **Alto** | Refactorizar con patrón Command; añadir manejo de excepciones exhaustivo y pruebas de frontera |
| Módulos sin cobertura (`app_desktop.py` 0 %, `skills/interfaz.py` 0 %) ocultan defectos | **Alta** | **Alto** | Implementar pruebas unitarias/integración con mocks de UI antes de la siguiente release |
| Cobertura baja en `main.py` (27,95 %) y `voice.py` (60 %) — puntos de entrada principales | **Alta** | **Alto** | Priorizar pruebas en el módulo de escucha y orquestación; objetivo ≥ 80 % en ambos |
| MTTD de 11,65 días: los defectos permanecen latentes más de 2 semanas | **Media** | **Alto** | Activar alertas automatizadas de errores en producción (Sentry/logging estructurado); revisar criterios de `xfail` |
| Deuda técnica en `servidor.py` (11 líneas E501, CC=27) dificulta revisiones de código | **Media** | **Medio** | Ejecutar `ruff --fix` en CI como paso bloqueante; establecer límite de 140 caracteres en pre-commit |
| Desviación del 25 % en horas (estimadas 72 h, reales 90 h); sprint 5 con 60 % de desviación | **Media** | **Medio** | Adoptar estimación por tres puntos o juicio experto promediado en sprints futuros; hacer refinamiento previo a cada sprint |
| Importaciones no utilizadas (`difflib`, `sys`, `subprocess`, `unicodedata`, `re`) aumentan superficie de error | **Baja** | **Bajo** | Integrar `ruff` como gate de calidad en GitHub Actions con fallo de pipeline si hay errores `F401` |

---

## Plan de mejora

Las acciones están ordenadas de mayor a menor urgencia. Cada una incluye la métrica objetivo que mejorará.

---

**Acción 1 — [CRÍTICA] Elevar el DRE mediante pruebas dirigidas a defectos graves**

- **Qué hacer:** Identificar los 4 defectos graves no interceptados en pruebas y escribir casos de prueba que los reproduzcan explícitamente. Incluir pruebas de caminos de error, excepciones y entradas inválidas en `main.py`, `voice.py` y `servidor.py`.
- **Cómo:** Sesión de revisión de los 7 defectos llegados a producción para construir casos de regresión. Añadir marcadores `@pytest.mark.regression` para trazabilidad.
- **Métrica que mejora:** **DRE** de 53,33 % → objetivo ≥ 85 %; **defectos en producción** de 7 → objetivo ≤ 3 en el siguiente ciclo.

---

**Acción 2 — [ALTA] Aumentar cobertura en módulos sin pruebas o con cobertura crítica**

- **Qué hacer:** Implementar pruebas para `app_desktop.py` (0 %), `skills/interfaz.py` (0 %), `main.py` (27,95 %) y `voice.py` (60 %) usando mocks para dependencias de audio y UI (e.g., `unittest.mock.patch` sobre llamadas a ElevenLabs y `speech_recognition`).
- **Cómo:** Establecer en `pytest.ini` un umbral mínimo de cobertura (`--cov-fail-under=75`) que bloquee el pipeline de GitHub Actions si no se alcanza.
- **Métrica que mejora:** **Cobertura total** de 72,52 % → objetivo ≥ 80 %; **MTTD** esperado reducirse de 11,65 días al detectar defectos antes en CI.

---

**Acción 3 — [ALTA] Refactorizar las dos funciones en rango D**

- **Qué hacer:** Refactorizar `ejecutar_accion` (CC=27) en `servidor.py` aplicando un patrón de despacho por diccionario o Command. Refactorizar `intentar` (CC=24) en `skills/aplicaciones.py` extrayendo submétodos por intención semántica (`_abrir_aplicacion`, `_cerrar_aplicacion`, `_listar_aplicaciones`).
- **Cómo:** Hacer la refactorización bajo la suite de pruebas existente para garantizar no regresión; actualizar o añadir pruebas unitarias después de cada extracción.
- **Métrica que mejora:** **Complejidad ciclomática máxima** de 27 → objetivo ≤ 15 (rango C o superior); **índice de mantenibilidad** de 72,97 → objetivo ≥ 78.

---

**Acción 4 — [MEDIA] Integrar análisis estático como gate bloqueante en CI**

- **Qué hacer:** Añadir un paso en el workflow de GitHub Actions que ejecute `ruff check .` y falle el pipeline si hay errores `F401` (importaciones no usadas), `F541` (f-strings vacíos) o `E501` (líneas largas). Ejecutar `ruff --fix` sobre los 28 errores autocorregibles en una PR dedicada.
- **Cómo:** Agregar al `pyproject.toml` o `.ruff.toml` las reglas seleccionadas; incluir `ruff` como dependencia de desarrollo en `requirements-dev.txt` y añadir hook de pre-commit.
- **Métrica que mejora:** **Advertencias Ruff** de 42 → objetivo 0 errores F/E bloqueantes; **densidad de defectos** reducida en módulos afectados (`main.py`, `voice.py`, `skills/web.py`).

---

**Acción 5 — [MEDIA] Cerrar los 5 defectos abiertos y los 3 `xfail` con criterio de aceptación**

- **Qué hacer:** Priorizar el cierre de los 4 defectos en `main.py` (mayor concentración) y el defecto en `estado.py` (3 issues). Para los 3 `xfail`, documentar en cada marcador la condición de resolución y la fecha límite, o reclasificarlos como `skip` con justificación si son dependencias externas.
- **Cómo:** Crear issues en GitHub con etiqueta `blocker` para los defectos en `main.py`; incluir su resolución como criterio de Definition of Done del siguiente sprint.
- **Métrica que mejora:** **Defectos abiertos por KLOC** de 2,43 → objetivo ≤ 1,0; **completitud funcional** verificada sube al eliminar comportamientos indefinidos en pruebas.

---

## Estimación (juicio experto de la IA)

**La técnica que más se acercó a las horas reales (90 h) fue el Juicio Experto Promediado**, con un total de **80,33 horas** (desviación de −9,67 h, −10,7 %). La estimación por Tres Puntos (PERT) obtuvo 81,85 h (−8,15 h, −9,1 %), siendo técnicamente la más cercana en valor absoluto, pero ambas se encuentran dentro del mismo orden de magnitud de error.

**Análisis por técnica:**

| Técnica | Estimado (h) | Real (h) | Desviación absoluta | Desviación % |
|---|---|---|---|---|
| Juicio experto — Alumno desarrollador | 72,0 | 90,0 | −18,0 h | −20,0 % |
| **Juicio experto — Promedio tres expertos** | **80,33** | **90,0** | **−9,67 h** | **−10,7 %** |
| **Tres Puntos (PERT)** | **81,85** | **90,0** | **−8,15 h** | **−9,1 %** |
| Análoga | 100,66 | 90,0 | +10,66 h | +11,8 % |
| Puntos de Función | 101,12 | 90,0 | +11,12 h | +12,4 % |

**Razones por las que el Juicio Experto promediado y PERT convergieron mejor:**

1. **El juicio del compañero con experiencia (83 h) y el de la IA/Claude (86 h)** compensaron la subestimación del alumno desarrollador (72 h), que es el sesgo de optimismo clásico del autor del código. El promedio diluyó ese sesgo.

2. **PERT incorporó explícitamente la incertidumbre** mediante los escenarios optimista/más probable/pesimista. El rango del 95 % (72,26 h – 91,44 h) **contenía las 90 horas reales**, lo que demuestra que el modelo capturó correctamente la variabilidad del proyecto.

3. La **estimación análoga sobreestimó** porque el factor de ajuste de +10 % sobre un proyecto de referencia de 1 800 SLOC resultó conservador en exceso para las 2 059 SLOC reales; la diferencia de productividad en integración con APIs de voz/IA fue mayor de lo esperado en comparación con un CRUD.

4. Los **Puntos de Función** sobreestimaron porque la productividad base (0,45 h/PF) no fue calibrada con datos históricos del propio equipo, sino con referencias genéricas, lo que introduce error sistemático hacia arriba.

**Recomendación:** Para proyectos futuros con tecnologías emergentes (IA conversacional, APIs de voz), usar **PERT como técnica principal** —por su manejo explícito de incertidumbre— y validarlo con juicio experto de al menos dos perfiles (uno externo al proyecto). Calibrar la productividad base de Puntos de Función con datos históricos propios antes de utilizarla como referencia de planificación.
