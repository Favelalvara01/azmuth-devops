## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-10-09 06:16**

---

## Dictamen general

El proyecto **Azmuth** alcanza una calificación de **76 / 100**, sustentada en una cobertura de pruebas del 88,16 %, cero defectos abiertos, análisis estático limpio (Ruff) y una complejidad ciclomática promedio de 3,62 (rango A predominante). Sin embargo, la baja eficacia de detección de defectos en pruebas (DRE = 44,44 %), el alto MTTD de 9,71 días y la cobertura nula de `app_desktop.py` representan riesgos que deben mitigarse antes de la liberación. **El proyecto está condicionalmente apto para liberarse**, sujeto a la corrección de las brechas de cobertura críticas y al refuerzo del proceso de revisión temprana.

---

## Idoneidad funcional

| Subcaracterística | Métrica clave | Valor | Interpretación |
|---|---|---|---|
| **Completitud funcional** | Pruebas aprobadas / total | 415 / 415 (100 %) | Todos los casos de prueba definidos pasan; no hay falla registrada. |
| **Corrección funcional** | Defectos abiertos | 0 / 18 | Los 18 defectos históricos están resueltos; densidad residual = 0,0 / KLOC. |
| **Pertinencia funcional** | Cobertura global | 88,16 % | Cubre la mayoría del comportamiento esperado, pero `app_desktop.py` (0 %) y `voice.py` (72,88 %) constituyen zonas sin verificación formal de pertinencia. |

**Observaciones:**

- Los 10 defectos detectados **en producción** (55,56 % del total) sugieren que el conjunto de pruebas no modela suficientemente los flujos de usuario real, lo que afecta la pertinencia funcional percibida.
- Los módulos `main.py` (4 defectos) y `estado.py` (3 defectos) concentraron la mayor cantidad de fallos históricos; aunque corregidos, deben mantenerse bajo vigilancia regresiva.
- La densidad de defectos global de **4,67 / KLOC** es aceptable para un proyecto de esta naturaleza (asistente de voz con integración de múltiples APIs externas), pero el Sprint 1 "Núcleo de voz" exhibió **13,05 / KLOC**, la cifra más alta del proyecto.

---

## Fiabilidad

### Métricas de proceso

| Métrica | Valor | Referencia de industria* | Estado |
|---|---|---|---|
| **MTTD** (Mean Time To Detect) | 9,71 días (233,09 h) | < 3 días ideal | ⚠️ Alto |
| **MTTR** (Mean Time To Repair) | 3,90 horas (234 min) | < 8 h aceptable | ✅ Bueno |
| **DRE** (Defect Removal Efficiency) | 44,44 % | ≥ 85 % recomendado | 🔴 Crítico |
| **Defectos en producción** | 10 de 18 (55,56 %) | < 20 % deseable | 🔴 Alto |

> *Referencia orientativa basada en estándares IEEE 1633 y literatura de Capers Jones.

### Subcaracterísticas ISO/IEC 25010

- **Madurez:** Con 415/415 pruebas aprobadas y 0 defectos abiertos, el software es estable en su estado actual. La densidad histórica de 4,67/KLOC indica madurez moderada.
- **Disponibilidad:** No se dispone de métricas de uptime/downtime en los datos; la arquitectura con Docker y GitHub Actions sugiere un despliegue reproducible, pero `app_desktop.py` sin cobertura representa una incógnita de disponibilidad en el componente de UI.
- **Tolerancia a fallos:** El DRE del 44,44 % revela que más de la mitad de los defectos eludieron las pruebas formales. El sistema no demostró capacidad suficiente para que el proceso de pruebas actuara como red de contención antes de producción.
- **Recuperabilidad:** El MTTR de 3,90 h es el indicador más positivo en fiabilidad: los defectos, una vez detectados, se resolvieron con rapidez, lo que indica buena capacidad de recuperación del equipo y del código.

---

## Mantenibilidad

### Escala de rangos ciclomáticos aplicada

| Rango | CC | Interpretación |
|---|---|---|
| **A** | 1–5 | Bajo riesgo, fácil de mantener |
| **B** | 6–10 | Riesgo moderado |
| **C** | 11–15 | Riesgo alto, refactorización recomendada |
| **D** | 16–20 | Muy alto, difícil de probar |
| **E** | 21–25 | Extremo |
| **F** | > 25 | Inmanejable |

### Distribución del proyecto

| Rango | Funciones | % |
|---|---|---|
| A | 231 | 82,21 % |
| B | 34 | 12,10 % |
| **C** | **16** | **5,69 %** |
| D–F | 0 | 0,00 % |

- **Promedio CC = 3,62** → Rango A global. Excelente.
- **94,31 % de funciones en A o B** → La base del código es altamente mantenible.
- **Índice de mantenibilidad promedio = 68,32** → Zona "moderada" (escala 0–100); aceptable pero con margen de mejora.
- El análisis estático con Ruff no reportó ningún hallazgo (`All checks passed!`), lo que refuerza la calidad estilística.

### Funciones a refactorizar (rango C)

Las siguientes 10 funciones superan CC = 11 y deben priorizarse:

| Prioridad | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 1 | `tematicas.py` | `_sintetizar` | 238 | 16 | Extraer ramas de síntesis en métodos auxiliares por tipo de tema |
| 1 | `skills/tiempo.py` | `_pronostico` | 100 | 16 | Separar lógica de condiciones meteorológicas en un mapa de estrategias |
| 2 | `skills/apps_instaladas.py` | `intentar` | 210 | 15 | Delegar casos de intención en funciones especializadas por categoría |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Dividir por tipo de recordatorio (crear/listar/eliminar) |
| 3 | `skills/apps_instaladas.py` | `resolver` | 166 | 13 | Aplicar patrón Command para cada resolución de app |
| 3 | `skills/multimedia.py` | `intentar` | 31 | 13 | Separar acciones (play/pause/stop/volumen) en métodos propios |
| 3 | `skills/pestanas.py` | `intentar` | 33 | 13 | Factorizar acciones de pestaña en dispatcher |
| 3 | `skills/tiempo.py` | `_recomendaciones` | 71 | 13 | Extraer reglas de recomendación a estructura de datos declarativa |
| 4 | `deepseek_ia.py` | `completar` | 82 | 12 | Unificar manejo de errores de API en decorador o clase base |
| 4 | `groq_ia.py` | `completar` | 85 | 12 | Ídem; considerar clase base `IACompletador` compartida con DeepSeek |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **DRE bajo (44,44 %): defectos escapan a producción** | Alta | Crítico | Ampliar escenarios de prueba de integración y E2E; implementar pruebas de contrato para APIs externas (Claude, ElevenLabs, Groq) |
| **`app_desktop.py` con 0 % de cobertura** | Alta | Alto | Crear suite de pruebas de UI con `pytest-qt` o mocking de componentes de escritorio; objetivo mínimo 70 % |
| **MTTD de 9,71 días: detección tardía de defectos** | Alta | Alto | Establecer alertas automáticas en pipeline CI para cobertura decreciente y nuevos patrones de error en logs |
| **`voice.py` con cobertura 72,88 % en módulo crítico** | Media | Alto | Agregar pruebas unitarias con mocks de STT/TTS; cubrir casos de silencio, ruido y timeout de audio |
| **Concentración de defectos históricos en Sprint 1 (Núcleo de voz, 13,05/KLOC)** | Media | Alto | Ejecutar análisis de regresión focalizado en `cerebro.py` y `main.py` en cada release |
| **Desviación de esfuerzo en Sprint 5 "Interfaz y servidor" (+60 %)** | Media | Medio | Aplicar estimación por tres puntos con P más conservador para módulos con integración de red; incluir spike técnico previo |
| **Funciones con CC = 13–16 sin cobertura completa** | Media | Medio | Exigir cobertura ≥ 90 % específicamente en funciones rango C como gate de merge en GitHub Actions |
| **Dependencia de múltiples APIs externas de IA (DeepSeek, Groq, Gemini)** | Baja | Alto | Implementar patrón Circuit Breaker y fallback entre proveedores; mockear en pruebas de CI |
| **Eficacia de revisión solo 16,67 %** | Alta | Medio | Adoptar checklists de revisión de código estructuradas (basadas en los patrones de defecto históricos de `main.py` y `estado.py`) |

---

## Plan de mejora

Las acciones están priorizadas de mayor a menor urgencia para habilitar la liberación segura:

### Acción 1 — Elevar el DRE mediante pruebas de integración E2E *(Prioridad: Crítica)*
**Qué hacer:** Diseñar al menos 15 casos de prueba de integración que simulen flujos completos de usuario (entrada de voz → procesamiento IA → respuesta → efecto en sistema), especialmente para los módulos con defectos históricos en producción (`main.py`, `estado.py`, `servidor.py`).
**Métrica que mejora:** DRE → objetivo ≥ 75 % en el siguiente ciclo; reducción de defectos en producción de 55,56 % a < 25 %.

---

### Acción 2 — Cubrir `app_desktop.py` y elevar `voice.py` *(Prioridad: Alta)*
**Qué hacer:** Implementar pruebas unitarias con mocking para `app_desktop.py` (actualmente 0 %) utilizando `unittest.mock` o `pytest-mock`; agregar casos de borde de audio a `voice.py` (silencio, timeout, audio corrupto) para alcanzar ≥ 80 %.
**Métrica que mejora:** Cobertura global: de 88,16 % → objetivo ≥ 92 %; cobertura de `app_desktop.py`: de 0 % → ≥ 70 %.

---

### Acción 3 — Refactorizar las 4 funciones de mayor CC *(Prioridad: Alta)*
**Qué hacer:** Aplicar refactorización a `_sintetizar` (CC=16), `_pronostico` (CC=16), `intentar` en `apps_instaladas.py` (CC=15) y `intentar` en `recordatorios.py` (CC=14) usando patrones Strategy o Command. Documentar con docstrings.
**Métrica que mejora:** Complejidad ciclomática máxima: de 16 → ≤ 10 (rango B); índice de mantenibilidad promedio: de 68,32 → objetivo ≥ 75.

---

### Acción 4 — Reducir MTTD con monitoreo proactivo en CI/CD *(Prioridad: Media)*
**Qué hacer:** Configurar en GitHub Actions un paso que analice tendencias de cobertura (fallo si cae > 2 pp respecto al commit anterior), integrar análisis de logs con detección de excepciones no controladas, y activar notificaciones automáticas al equipo ante degradación.
**Métrica que mejora:** MTTD: de 9,71 días → objetivo < 3 días; porcentaje de defectos detectados en pruebas vs. producción: de 33,33 % → objetivo ≥ 60 %.

---

### Acción 5 — Fortalecer el proceso de revisión de código *(Prioridad: Media)*
**Qué hacer:** Implementar un checklist de revisión obligatorio en GitHub (PR template) basado en los patrones de defecto históricos identificados (manejo de estado, concurrencia en servidor, flujos de error en IA). Exigir al menos un revisor antes de merge a `main`.
**Métrica que mejora:** Eficacia de revisión: de 16,67 % → objetivo ≥ 40 %; defectos escapados a producción en el próximo ciclo: objetivo < 4.

---

## Estimación (juicio experto de la IA)

### Comparativo de técnicas

| Técnica | Estimado (h) | Real (h) | Error absoluto | Error % |
|---|---|---|---|---|
| Juicio de expertos — Alumno | 102,0 | 122,0 | 20,0 h | 16,39 % |
| Juicio de expertos — IA (Claude) | 119,0 | 122,0 | 3,0 h | 2,46 % |
| **Juicio de expertos — Promedio** | **110,5** | **122,0** | **11,5 h** | **9,43 %** |
| Tres puntos (PERT) | 114,68 | 122,0 | 7,32 h | 6,00 % |
| Rango 95 % tres puntos | [104,03–125,33] | 122,0 | — | ✅ Dentro del rango |
| Puntos de función | 146,38 | 122,0 | 24,38 h | 19,98 % |
| Análoga | 188,56 | 122,0 | 66,56 h | 54,56 % |

### Técnica más precisa: **Estimación por Tres Puntos (PERT)**

La técnica de tres puntos fue la que más se aproximó al valor real con un error del **6,00 %**, y además el valor real de **122 horas cae cómodamente dentro del intervalo de confianza del 95 % [104,03 – 125,33 h]**, lo que valida estadísticamente la estimación.

**¿Por qué funcionó mejor?** Tres razones son identificables en los datos:

1. **Capturó la asimetría del riesgo.** Al obligar a estimar el escenario pesimista (P), se incorporó la incertidumbre de módulos como "Interfaz y servidor" (que terminó con +60 % de desviación) y "Núcleo de voz" (+40 %), sin distorsionar el total por ser valores extremos puntuales.

2. **La desviación estándar total de 5,32 h refleja un proyecto relativamente acotado.** Con sprints bien definidos y un equipo de desarrollo único (alumno), la varianza entre escenarios fue manejable y los valores M (más probable) resultaron buenos predictores de la realidad en los módulos estables.

3. **El juicio de la IA (Claude) como experto fue el segundo más preciso** (error de solo 2,46 h = 2,46 %), lo que sugiere que el análisis estático del código fuente permitió a la IA percibir la complejidad real mejor que la estimación inicial del alumno. Combinado en el promedio grupal, redujo el error del alumno a la mitad.

La técnica análoga sobreestimó severamente (188,56 h, error 54,56 %) porque el factor de ajuste del 10 % no fue suficiente para capturar la diferencia cualitativa entre un CRUD web y un asistente de voz con múltiples integraciones de IA; el SLOC duplicado no escala linealmente en horas cuando hay deuda de aprendizaje tecnológico por API. Los puntos de función también sobreestimaron (19,98 %), posiblemente porque la productividad base de 0,45 h/PF no fue calibrada con proyectos similares del mismo equipo.

---

*Auditoría generada con base exclusiva en los datos provistos del pipeline DevOps del proyecto Azmuth.*
