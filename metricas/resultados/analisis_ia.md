## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-08**

---

## Dictamen general

El proyecto **Azmuth** obtiene una calificación de **74 / 100**. La cobertura de pruebas (85,56 %), la ausencia de defectos abiertos y el análisis estático limpio (Ruff sin hallazgos) son fortalezas sólidas; sin embargo, el **DRE del 47,06 %** indica que más de la mitad de los defectos escaparon a la fase de pruebas y llegaron a producción, y la cobertura de dos archivos críticos es nula (`app_desktop.py`, `skills/interfaz.py`). El proyecto **puede liberarse condicionalmente**, siempre que se instrumenten pruebas para los módulos sin cobertura y se refactoren las funciones de mayor complejidad ciclomática antes del siguiente ciclo de mantenimiento.

---

## Idoneidad funcional

| Subcaracterística | Evidencia | Valoración |
|---|---|---|
| **Completitud funcional** | 252/252 pruebas aprobadas; 0 defectos abiertos; 7 módulos entregados de 7 planificados | ✅ Alta |
| **Corrección funcional** | 17 defectos totales, todos resueltos; densidad 5,87 defectos/KLOC (aceptable para un primer release con APIs externas) | ✅ Aceptable |
| **Pertinencia funcional** | Los sprints cubren voz, skills, sistema, IA, interfaz, persistencia y DevOps; el scope no muestra funciones no solicitadas | ✅ Alta |

**Observaciones:**
- La concentración de defectos en **`main.py` (4)**, **`estado.py` (3)** y **`servidor.py` (2)** sugiere que la lógica de arranque y gestión de estado es el área de mayor riesgo funcional.
- `app_desktop.py` y `skills/interfaz.py` tienen **0 % de cobertura**, lo que deja funcionalidad verificada sólo en tiempo de ejecución manual, comprometiendo la corrección demostrable.

---

## Fiabilidad

| Métrica | Valor | Interpretación |
|---|---|---|
| **MTTD** | 246,79 h (≈ 10,3 días) | Detección muy tardía; los defectos permanecen latentes ~10 días antes de ser descubiertos |
| **MTTR** | 4,12 h (≈ 247 min) | Reparación ágil; el equipo resuelve defectos en menos de un turno de trabajo |
| **DRE** | 47,06 % | Crítico: solo 5 de 17 defectos se detectaron en pruebas; 9 llegaron a producción |
| **Defectos en producción** | 9 / 17 (52,94 %) | Supera el umbral recomendado (<20 % para productos de calidad) |
| **Suite de pruebas** | 252 pruebas, 0 fallidas, 5,56 s | Ejecución rápida y estable; buena madurez de la suite |

**Madurez:** Media-baja. Aunque la suite es verde, el DRE refleja que el proceso de pruebas no ejercita suficientemente los caminos de fallo reales.

**Tolerancia a fallos / Recuperabilidad:** El MTTR de 4,12 h es positivo, indicando que el equipo cuenta con procedimientos claros de corrección. No se registran defectos de tipo `xfail`, lo que sugiere ausencia de fallos conocidos no atendidos.

**Disponibilidad estimada** (proxy): con MTTD 246,79 h y MTTR 4,12 h → disponibilidad ≈ 246,79 / (246,79 + 4,12) = **98,4 %**, aceptable para una aplicación de escritorio.

---

## Mantenibilidad

**Índice de mantenibilidad promedio: 72,75 / 100** — rango *Moderado* (umbral recomendado ≥ 80).

**Complejidad ciclomática — distribución:**

| Rango | Descripción | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Simple, bajo riesgo | 170 | 84,6 % |
| **B** (6–10) | Moderada | 20 | 10,0 % |
| **C** (11–15) | Compleja, refactorizar | 11 | 5,5 % |
| **D–F** (>15) | Muy compleja / caótica | 0 | 0,0 % |

✅ El 94,53 % de funciones está en rango A-B — buena base.
⚠️ Las 11 funciones en rango **C** concentran el mayor riesgo de mantenimiento.

**Funciones prioritarias a refactorizar** (rango C, ordenadas por complejidad descendente):

| Prioridad | Archivo | Función | Línea | CC |
|---|---|---|---|---|
| 1 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | 14 |
| 3 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 |
| 4 | `skills/multimedia.py` | `intentar` | 31 | 13 |
| 5 | `skills/pestanas.py` | `intentar` | 33 | 13 |
| 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 165 | 12 |
| 7 | `skills/memoria.py` | `intentar` | 61 | 12 |
| 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 |
| 9 | `skills/web.py` | `intentar` | 53 | 12 |
| 10 | `cerebro.py` | `preguntar` | 93 | 11 |

**Patrón detectado:** La recurrencia del nombre `intentar` en múltiples skills con complejidad alta sugiere que este método actúa como "dios del flujo" dentro de cada skill; se recomienda descomponer por responsabilidad única (SRP).

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos en producción por DRE bajo (47 %) | **Alta** | **Alto** | Ampliar pruebas de integración y escenarios negativos; meta DRE ≥ 75 % en próximo sprint |
| Archivos sin cobertura (`app_desktop.py`, `skills/interfaz.py`) | **Alta** | **Alto** | Implementar pruebas unitarias/mocking de UI antes del siguiente release |
| Regresiones en funciones `intentar` de alta CC (13–15) | **Media** | **Alto** | Refactorizar con Extract Method + añadir pruebas de contrato por rama |
| MTTD de ~10 días (detección tardía) | **Media** | **Medio** | Introducir pruebas de mutación (p. ej., `mutmut`) y revisiones de código obligatorias en PRs |
| Desviación de esfuerzo acumulada del 25 % (72 h estimadas → 90 h reales) | **Media** | **Medio** | Adoptar estimación por tres puntos (PERT) en futuros proyectos; ajustar velocidad histórica (7,86 pts/sprint) |
| Alta densidad de defectos en Sprint 5 — Interfaz y servidor (9,3/KLOC) | **Media** | **Alto** | Añadir pruebas de integración para `servidor.py`; aplicar revisión de código pre-merge |
| Dependencia de APIs externas (Claude, ElevenLabs) sin mocks completos | **Media** | **Medio** | Crear fixtures/mocks estables en pytest para todas las llamadas externas; añadir pruebas de fallback |

---

## Plan de mejora

Las acciones están ordenadas de mayor a menor urgencia para el próximo ciclo.

---

**Acción 1 — Cobertura de módulos críticos sin pruebas** 🔴 Urgente

- **Qué:** Implementar pruebas unitarias con mocking de GUI para `app_desktop.py` (0 %) y `skills/interfaz.py` (0 %). Elevar `cerebro.py` de 72,29 % y `voice.py` de 73,33 %.
- **Cómo:** Usar `pytest-mock` y `unittest.mock` para simular dependencias de sistema y voz.
- **Métrica que mejora:** Cobertura total (85,56 % → meta ≥ 92 %) y DRE (47,06 % → meta ≥ 70 %).

---

**Acción 2 — Incrementar el DRE mediante pruebas de escenarios negativos** 🔴 Urgente

- **Qué:** Diseñar casos de prueba orientados a fallos: entradas inválidas, timeouts de API, comandos de voz ambiguos. Los 9 defectos de producción deben convertirse en pruebas de regresión.
- **Cómo:** Aplicar técnica de partición de equivalencia y análisis de valores límite sobre los módulos con mayor densidad de defectos (`main.py`, `estado.py`, `servidor.py`).
- **Métrica que mejora:** DRE (47,06 % → ≥ 75 %) y defectos en producción (9 → ≤ 3).

---

**Acción 3 — Refactorizar las 5 funciones `intentar` de mayor complejidad** 🟠 Alta

- **Qué:** Aplicar el patrón *Extract Method* y *Strategy* para descomponer los métodos `intentar` de `apps_instaladas.py` (CC 15), `recordatorios.py` (CC 14), `multimedia.py` (CC 13), `pestanas.py` (CC 13) y `memoria.py` (CC 12).
- **Cómo:** Cada rama lógica identificada pasa a ser un método privado nombrado semánticamente. Garantizar que la cobertura de cada función refactorizada no descienda.
- **Métrica que mejora:** Complejidad ciclomática máxima (15 → ≤ 10, rango B) e índice de mantenibilidad (72,75 → meta ≥ 80).

---

**Acción 4 — Reducir el MTTD mediante pruebas de mutación y revisiones obligatorias** 🟠 Alta

- **Qué:** Integrar `mutmut` o `cosmic-ray` en el pipeline de GitHub Actions para medir la efectividad real de la suite. Establecer revisión de código (mínimo 1 aprobación) como requisito de merge.
- **Cómo:** Ejecutar mutaciones sobre los archivos con mayor densidad histórica de defectos; generar reporte de mutantes vivos como métrica de calidad de pruebas.
- **Métrica que mejora:** MTTD (246,79 h → meta ≤ 120 h) y eficacia de revisiones (17,65 % → ≥ 30 %).

---

**Acción 5 — Mejorar la estimación de esfuerzo adoptando PERT como estándar** 🟡 Media

- **Qué:** En futuros sprints, usar la estimación por tres puntos (PERT) como método primario de planificación. Calibrar los valores O/M/P con la velocidad histórica medida (7,86 pts/sprint, 1,38–2,0 h/punto según módulo).
- **Cómo:** Documentar la tabla de horas reales por módulo como línea base análoga para el siguiente proyecto. Ajustar el factor de escala al pasar de 2,9 KLOC a proyectos mayores.
- **Métrica que mejora:** Desviación de esfuerzo (25 % → meta ≤ 10 %) y confiabilidad de planificación del equipo.

---

## Estimación (juicio experto de la IA)

**La técnica que más se acercó a las 90 horas reales fue la estimación por Tres Puntos (PERT), con un total de 81,85 h** — una desviación de apenas **8,15 h (–9,1 %)**, y con el dato adicional de que el intervalo de confianza al 95 % calculado fue **[72,26 h – 91,44 h]**, rango dentro del cual cayeron exactamente las 90 horas reales. Esto valida la técnica no solo en su estimación puntual, sino en su capacidad predictiva de incertidumbre.

En segundo lugar, el **juicio de expertos** con promedio de 80,33 h se desvió en 9,67 h (–10,7 %), siendo notable que la estimación del "compañero con experiencia" (83 h) y la de la IA/Claude (86 h) fueron más cercanas a la realidad que la del alumno desarrollador (72 h), quien tendió a subestimar — sesgo común en desarrolladores sin experiencia previa en proyectos similares.

Las técnicas menos precisas fueron:

- **Puntos de función**: 101,12 h (+12,3 % sobre las reales), sobreestimando probablemente porque la productividad referencial de 0,45 h/PF no fue calibrada con datos propios del equipo.
- **Analogía**: 141,63 h (+57,4 %), la más alejada. El factor de ajuste de ×1,1 sobre el proyecto referencial (Easy Learning, 1 800 SLOC → 80 h) no capturó adecuadamente que Azmuth, pese a tener 2 897 SLOC, posee módulos de baja complejidad (Persistencia SQLite: 0 defectos, solo 5 h reales) que diluyen el esfuerzo por línea. La analogía sobreestimó porque asumió una productividad uniforme de 22,5 SLOC/h cuando en realidad varía entre 16 y 46 SLOC/h según el módulo.

**Conclusión:** Para equipos pequeños con alta incertidumbre en proyectos de IA y voz, el método PERT — con puntos O/M/P acordados en sesión conjunta — ofrece el mejor balance entre precisión y gestión explícita del riesgo de estimación.
