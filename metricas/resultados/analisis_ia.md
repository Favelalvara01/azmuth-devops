## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Generado:** 2026-10-08 03:31

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **74 / 100**. Presenta fortalezas sólidas en cobertura de pruebas (85.83 %), cero defectos abiertos y análisis estático limpio (Ruff sin hallazgos), lo que lo acerca a un estado liberable. Sin embargo, la baja eficacia de detección de defectos antes de producción (DRE 44.44 %) y la cobertura nula en dos módulos críticos de interfaz representan riesgos que deben mitigarse **antes de la liberación formal** en un entorno de usuarios reales.

---

## Idoneidad funcional

### Completitud funcional
- **315 pruebas ejecutadas, 315 aprobadas (100 % de tasa de éxito)** y **0 defectos abiertos**.
- Los 18 defectos históricos fueron todos corregidos; la densidad residual es **0.0 defectos/KLOC abiertos**.
- Cobertura global del **85.83 %** sobre 2 060 líneas ejecutables (1 768 cubiertas).

### Corrección funcional
- Dos archivos con **cobertura 0 %**: `app_desktop.py` y `skills/interfaz.py`. Cualquier función en ellos podría contener defectos latentes sin detectar; esto compromete la corrección declarada del producto.
- `cerebro.py` (75 %) y `voice.py` (72.88 %) son módulos centrales con cobertura inferior al umbral recomendado (80 %), elevando el riesgo de regresiones silenciosas.
- La distribución de defectos por fase muestra que **10 de 18 (55.6 %) fueron detectados en producción**, señal de insuficiencia en las pruebas de sistema previas al despliegue.

### Pertinencia funcional
- Las habilidades (*skills*) cubren un amplio espectro funcional (voz, sistema, IA, recordatorios, multimedia, contactos, hábitos, etc.) alineado con el propósito declarado de asistente de voz.
- La eficacia de revisión estática capturó solo **3/18 defectos (16.67 %)**, indicando que las revisiones de código no están integradas sistemáticamente en el flujo de trabajo.

---

## Fiabilidad

### Indicadores clave

| Métrica | Valor | Interpretación |
|---|---|---|
| MTTD | 233.09 h (≈ 9.71 días) | Tiempo elevado; los defectos tardan casi 10 días en detectarse |
| MTTR | 3.9 h (234 min) | Excelente; la corrección es ágil una vez detectado el problema |
| DRE | **44.44 %** | Crítico: menos de la mitad de los defectos se capturan antes de producción |
| Defectos en producción | 10 / 18 (55.56 %) | La mayoría escapa al proceso de pruebas |
| Pruebas aprobadas | 315 / 315 (100 %) | Sin fallos en suite actual |
| Defectos conocidos (xfail) | 0 | No hay deuda técnica reconocida en pruebas |

### Madurez
Con 0 defectos abiertos y 315/315 pruebas en verde, la suite actual es estable. No obstante, el DRE del 44.44 % indica que la suite **no cubre los escenarios que causan defectos en producción** — la madurez real es menor de lo que el 100 % de pruebas aprobadas sugiere.

### Disponibilidad y tolerancia a fallos
No se reportan métricas de uptime ni pruebas de caos en el pipeline. La ausencia de pruebas para `app_desktop.py` y `skills/interfaz.py` implica que la capa de presentación no tiene ningún nivel de garantía de disponibilidad verificable.

### Recuperabilidad
El MTTR de **3.9 h** es favorable; el equipo tiene capacidad de respuesta rápida ante incidentes. La existencia de Docker en el pipeline facilita la recuperación por redespliegue, aunque no se documentan pruebas de rollback.

---

## Mantenibilidad

### Complejidad ciclomática

| Rango | Complejidad | Funciones | % |
|---|---|---|---|
| **A** | 1 – 5 | 183 | 84.33 % |
| **B** | 6 – 10 | 22 | 10.14 % |
| **C** | 11 – 15 | 12 | 5.53 % |
| D | 16 – 20 | 0 | 0 % |
| E | 21 – 25 | 0 | 0 % |
| F | > 25 | 0 | 0 % |

- **94.47 % en rangos A-B**: la base de código es, en general, bien estructurada y fácil de mantener.
- **Índice de mantenibilidad promedio: 72.54 / 100** — aceptable pero mejorable (el umbral de excelencia suele situarse en ≥ 80).
- Sin funciones en rangos D, E o F: no existen "puntos de riesgo extremo".

### Funciones prioritarias para refactorizar (rango C)

| # | Archivo | Función | Línea | CC |
|---|---|---|---|---|
| 1 | `skills/apps_instaladas.py` | `intentar` | 213 | **15** |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | **14** |
| 3 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 |
| 4 | `skills/multimedia.py` | `intentar` | 31 | 13 |
| 5 | `skills/pestanas.py` | `intentar` | 33 | 13 |
| 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 205 | 12 |
| 7 | `skills/memoria.py` | `intentar` | 61 | 12 |
| 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 |
| 9 | `skills/web.py` | `intentar` | 53 | 12 |
| 10 | `cerebro.py` | `preguntar` | 104 | 11 |

> **Patrón detectado:** el nombre `intentar` aparece en 5 de los 10 casos. Esto sugiere que existe un patrón arquitectónico repetido donde la lógica de despacho/retry se acumula sin descomposición adecuada. Una refactorización del patrón base de *skill* reduciría la CC de forma transversal.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos en producción no detectados por pruebas (DRE 44.44 %) | **Alta** | **Alto** | Ampliar suite con pruebas de integración end-to-end y pruebas de escenarios negativos; implementar fuzzing en entradas de voz |
| Módulos `app_desktop.py` y `skills/interfaz.py` sin cobertura (0 %) | **Alta** | **Alto** | Crear pruebas unitarias/de integración mínimas; usar mocks de la GUI (pytest-qt o similar) |
| MTTD alto (≈ 9.71 días): detección lenta en producción | **Media** | **Alto** | Instrumentar logging estructurado y alertas automáticas (Sentry o equivalente) en el pipeline |
| Desviación de estimación del 25 % (72 h estimadas vs 90 h reales) con picos en Sprint 5 (60 %) | **Media** | **Medio** | Adoptar estimación por tres puntos como estándar; añadir buffer del 15-20 % en sprints con integración de UI |
| Complejidad ciclomática C en 12 funciones clave (patrón `intentar`) | **Media** | **Medio** | Refactorizar las 5 funciones CC > 12 antes del siguiente sprint; introducir umbral de CC ≤ 10 como *quality gate* en CI |
| Eficacia de revisión baja (16.67 %; solo 3/18 defectos en revisión) | **Media** | **Medio** | Implementar checklist de revisión estructurada (code review con criterios documentados) y pair programming en módulos críticos |
| Densidad de defectos en Sprint 1 "Núcleo de voz" (13.74/KLOC) y Sprint 5 "Interfaz" (9.09/KLOC) | **Baja** | **Alto** | Priorizar pruebas de regresión en estos módulos; agregar pruebas de contrato para APIs de voz (ElevenLabs, Claude) |

---

## Plan de mejora

Las siguientes 5 acciones están ordenadas por **prioridad decreciente** (impacto × urgencia):

---

### 1. 🔴 Elevar el DRE mediante pruebas de sistema pre-producción
**Métrica que mejora:** DRE (actualmente 44.44 % → objetivo ≥ 75 %)

- Diseñar al menos **20 casos de prueba de integración** que simulen flujos completos de usuario (entrada de voz → procesamiento → respuesta).
- Incluir escenarios de error controlado: comandos ambiguos, API externa no disponible, timeout.
- Integrar estas pruebas en el gate de CI/CD para que un build no pase a producción con DRE < 70 %.
- **Responsable:** equipo de QA + desarrollador principal. **Plazo sugerido:** antes del siguiente release.

---

### 2. 🔴 Cubrir los módulos de interfaz con pruebas automatizadas
**Métrica que mejora:** Cobertura de `app_desktop.py` y `skills/interfaz.py` (0 % → ≥ 70 %)

- Usar **mocks** o frameworks de prueba de GUI (ej. `pytest-qt`, `unittest.mock` para componentes Tkinter/Qt) para evitar dependencia del entorno gráfico en CI.
- Definir como *quality gate*: **ningún archivo con cobertura < 60 %** puede existir en el proyecto.
- Incremento esperado en cobertura global: de 85.83 % a ≈ 88-90 %.

---

### 3. 🟠 Refactorizar las 5 funciones con CC ≥ 12 (patrón `intentar`)
**Métrica que mejora:** Complejidad ciclomática máxima (15 → ≤ 10) e índice de mantenibilidad (72.54 → objetivo ≥ 80)

- Extraer la lógica de despacho de cada `intentar` en funciones auxiliares especializadas (una por rama de decisión principal).
- Crear una clase base `Skill` con un método `intentar` que gestione el flujo general (patrón *Template Method*), delegando el comportamiento específico a subclases.
- Verificar que CC ≤ 10 se mantenga como regla en Ruff/flake8-complexity en CI.

---

### 4. 🟠 Instrumentar monitoreo y alertas en producción para reducir el MTTD
**Métrica que mejora:** MTTD (233 h → objetivo < 48 h)

- Integrar una solución de **logging estructurado** (ej. `loguru` + Sentry o Grafana Loki) que genere alertas automáticas ante excepciones no controladas.
- Definir umbrales de alerta: tasa de errores > 5 % en cualquier skill → notificación inmediata al equipo.
- Documentar un runbook de respuesta a incidentes que aproveche el buen MTTR (3.9 h) ya existente.

---

### 5. 🟡 Institucionalizar la estimación por tres puntos con buffer explícito
**Métrica que mejora:** Desviación de estimación (25 % → objetivo < 10 %)

- Adoptar **PERT (tres puntos)** como técnica estándar de estimación, dado que su rango 95 % (72.26 – 91.44 h) captura perfectamente las 90 h reales.
- Añadir un **buffer explícito del 15 %** para sprints con integración de componentes de UI o APIs externas (basado en la desviación de Sprint 5: 60 %).
- Realizar retrospectivas de estimación al cierre de cada sprint para calibrar los valores O/M/P del equipo.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas

| Técnica | Horas estimadas | Error absoluto vs. 90 h reales | Error % |
|---|---|---|---|
| Juicio de expertos (promedio) | 80.33 h | 9.67 h | 10.74 % |
| Tres puntos – PERT | 81.85 h | 8.15 h | **9.06 %** ✅ |
| Tres puntos – Rango 95 % | [72.26 – 91.44] | *90 h dentro del rango* | — |
| Puntos de función | 101.12 h | 11.12 h | 12.36 % |
| Análoga | 153.66 h | 63.66 h | 70.73 % |

### Técnica más acertada: **Tres Puntos (PERT)**

La técnica de **tres puntos con distribución PERT** fue la que mejor aproximó las horas reales, con un error de solo **8.15 horas (9.06 %)**. Más significativo aún: el **intervalo de confianza al 95 % (72.26 – 91.44 h) contiene las 90 h reales**, lo que valida la calibración de los valores optimista/modal/pesimista del equipo.

**¿Por qué funcionó mejor?**
1. **Captura la asimetría real del desarrollo de software**: al ponderar el escenario pesimista, PERT amortigua el optimismo natural de los desarrolladores (visible en el Alumno: 72 h, el más bajo de todos).
2. **Granularidad por módulo**: al estimar sprint por sprint, el error en módulos simples (SQLite: -1 h) compensó parcialmente el error en módulos complejos (Interfaz: +6 h), algo que la estimación análoga no puede hacer porque trabaja con el proyecto como un todo.
3. La **estimación análoga falló drásticamente (+63.66 h)** porque el factor de ajuste de 1.1 fue insuficiente: el proyecto de referencia (Easy Learning, CRUD C#) tiene una naturaleza fundamentalmente distinta — integración de APIs de voz e IA generativa implica complejidad no lineal que un ajuste porcentual simple no captura.
4. Los **puntos de función** (101.12 h, error 12.36 %) sobreestimaron porque la tasa de productividad de 0.45 h/PF puede no reflejar las eficiencias obtenidas con Python y el ecosistema de librerías de terceros ya maduras.

> **Recomendación:** Para proyectos futuros de similar naturaleza (IA + integraciones externas + voz), usar **PERT por módulo como técnica base**, complementado con **juicio de expertos para validar el escenario pesimista** de cada sprint, que es donde se concentra el mayor riesgo de subestimación.

---

*Auditoría generada conforme a ISO/IEC 25010:2023 (características de calidad del producto) e ISO/IEC 25023:2016 (métricas de medición). Los valores calculados se derivan exclusivamente de los datos del pipeline proporcionados.*
