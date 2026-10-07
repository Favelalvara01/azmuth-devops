## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**Normas ISO/IEC 25010 · ISO/IEC 25023 | Fecha de datos: 2026-10-07**

---

## Dictamen general

El proyecto Azmuth obtiene una calificación de **71 / 100**, apoyada en una cobertura de pruebas del 76,62 %, un DRE del 50 % y un único defecto abierto de baja criticidad. **El proyecto puede liberarse de forma condicionada**: se requiere cerrar el defecto abierto, elevar el DRE por encima del 75 % y refactorizar las dos funciones de rango D antes de la siguiente iteración productiva.

---

## Idoneidad funcional

| Subcaracterística | Métrica clave | Valor | Interpretación |
|---|---|---|---|
| **Completitud funcional** | Pruebas aprobadas / total | 167 / 167 (100 %) | Todas las rutas de prueba declaradas pasan |
| **Corrección funcional** | Defectos abiertos | 1 | Riesgo residual bajo; debe resolverse antes del despliegue |
| **Pertinencia funcional** | Densidad de defectos total | 6,17 / kloc | Aceptable para un proyecto de 2,6 kloc en etapa formativa |

**Hallazgos relevantes:**

- `main.py` concentra **4 defectos** con solo 26,01 % de cobertura; es el archivo con mayor riesgo de regresión no detectada.
- `app_desktop.py` y `skills/interfaz.py` tienen **0 % de cobertura**, lo que impide verificar su corrección funcional.
- Los 5 defectos que llegaron a producción (frente a 5 detectados en pruebas) indican que aproximadamente la mitad del flujo funcional no estaba validado antes de la entrega.

---

## Fiabilidad

| Indicador | Valor | Benchmark referencial | Evaluación |
|---|---|---|---|
| MTTD | 262,18 h (10,92 días) | < 72 h (crítico) | ⚠️ Alto — los defectos tardan demasiado en detectarse |
| MTTR | 2,52 h (151 min) | < 4 h (aceptable) | ✅ Muy bueno — la corrección es ágil |
| DRE | 50,0 % | ≥ 75 % (liberación) | ⚠️ Bajo — la mitad de los defectos llegan a producción |
| Defectos en producción vs. total | 8 / 16 (50 %) | < 20 % | ❌ Crítico |

**Interpretación por subcaracterística (ISO/IEC 25010):**

- **Madurez:** Con 15/16 defectos resueltos y 0 *xfail*, la base de código es estable en lo conocido; sin embargo, el MTTD alto sugiere defectos latentes aún no descubiertos.
- **Disponibilidad:** El pipeline CI ejecuta 167 pruebas en 3,18 s, lo que garantiza ciclos de retroalimentación rápidos.
- **Tolerancia a fallos:** No existen métricas explícitas de manejo de excepciones, pero la alta complejidad ciclomática en `ejecutar_accion` (CC=27) y `intentar` de aplicaciones (CC=24) eleva el riesgo de ramas no controladas.
- **Recuperabilidad:** El MTTR de 2,52 h indica buena capacidad de respuesta del equipo una vez detectado el fallo.

---

## Mantenibilidad

### Escala de referencia (McCabe)

| Rango | CC | Significado |
|---|---|---|
| A | 1–5 | Bajo riesgo |
| B | 6–10 | Moderado |
| C | 11–15 | Alto — revisión recomendada |
| D | 16–25 | Muy alto — refactorización prioritaria |
| E | 26–50 | Crítico |
| F | > 50 | No mantenible |

### Distribución actual

| Rango | Funciones | % |
|---|---|---|
| A | 118 | 79,2 % |
| B | 17 | 11,4 % |
| C | 12 | 8,1 % |
| D | 2 | 1,3 % |
| E | 0 | — |
| F | 0 | — |

- **Índice de mantenibilidad promedio:** 71,83 / 100 — aceptable, con margen de mejora.
- **90,6 % de funciones en rango A–B** es un resultado sólido para un proyecto de esta escala.
- **14 infracciones E501** en `servidor.py` y `skills/aplicaciones.py` degradan la legibilidad de las funciones ya complejas.

### Funciones prioritarias a refactorizar

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 161 | 27 | D | Descomponer por tipo de acción (patrón Strategy o tabla de despacho) |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | D | Extraer casos en métodos privados especializados |
| 🟠 3 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | C | Separar lógica de búsqueda y ejecución |
| 🟠 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Extraer validación de fecha/hora |
| 🟠 5 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | C | Reducir anidamiento con retorno temprano |
| 🟡 6 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Separar reproducción de control |
| 🟡 7 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Tabla de despacho por comando |
| 🟡 8 | `cerebro.py` | `actualizar_perfil_si_toca` | 136 | 12 | C | Extraer condiciones de temporización |
| 🟡 9 | `main.py` | `escuchar` | 102 | 12 | C | Separar captura de audio y procesamiento |
| 🟡 10 | `skills/memoria.py` | `intentar` | 61 | 12 | C | Extraer casos CRUD individuales |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defecto abierto en producción sin resolver | Alta | Alto | Bloquear el merge a `main` hasta cierre; añadir issue como *blocker* en el tablero |
| DRE del 50 % permite que defectos graves lleguen a producción | Alta | Alto | Ampliar pruebas de integración de `main.py` y archivos con 0 % de cobertura antes del siguiente sprint |
| `ejecutar_accion` (CC=27) y `intentar` (CC=24) generan ramas no testeadas | Media | Alto | Refactorizar en el siguiente sprint; agregar pruebas parametrizadas por rama |
| `app_desktop.py` y `skills/interfaz.py` con 0 % de cobertura | Media | Medio | Crear pruebas unitarias con mocks de UI; meta mínima 60 % por archivo |
| MTTD de ~11 días indica detección tardía de defectos | Media | Medio | Implementar alertas automáticas de errores en runtime (p. ej. Sentry o logging estructurado) |
| Desviación del 25 % en estimación total (72 h estimadas vs. 90 h reales) | Alta | Medio | Aplicar factor de corrección de 1,25× en próximas estimaciones; usar velocidad histórica (7,86 pts/sprint) |
| 14 infracciones de líneas largas en archivos críticos | Baja | Bajo | Configurar `ruff --fix` como *pre-commit hook* para impedir que se acumulen |

---

## Plan de mejora

### Acción 1 — Cerrar el defecto abierto y bloquear el merge *(Urgente — esta semana)*
- **Qué:** Resolver el único defecto abierto; configurar GitHub Actions para bloquear PRs mientras existan issues con etiqueta `blocker`.
- **Métrica que mejora:** `defectos_abiertos_por_kloc` → de 0,39 a 0,00; condición de liberación cumplida.

### Acción 2 — Elevar la cobertura de `main.py`, `app_desktop.py` y `skills/interfaz.py` *(Sprint siguiente)*
- **Qué:** Añadir pruebas unitarias con mocks (`unittest.mock`, `pytest-mock`) para los puntos de entrada de voz y la UI de escritorio; meta mínima 60 % en archivos con 0 % y 60 % en `main.py`.
- **Métrica que mejora:** Cobertura total → de 76,62 % a ≥ 82 %; DRE → de 50 % a ≥ 65 %.

### Acción 3 — Refactorizar `ejecutar_accion` y `intentar` de `skills/aplicaciones.py` *(Sprint siguiente)*
- **Qué:** Aplicar patrón de tabla de despacho (`dict[str, Callable]`) en `ejecutar_accion` y extraer métodos privados en `intentar`; objetivo CC ≤ 10 (rango B) en ambas.
- **Métrica que mejora:** Complejidad máxima → de 27 a ≤ 10; índice de mantenibilidad promedio → de 71,83 a ≥ 76.

### Acción 4 — Incorporar detección temprana de errores en runtime *(Próximas 2 semanas)*
- **Qué:** Integrar logging estructurado (p. ej. `structlog`) con alertas automáticas en los módulos de mayor densidad de defectos (`main.py`, `servidor.py`, `estado.py`).
- **Métrica que mejora:** MTTD → de 262 h a meta ≤ 72 h; defectos escapados a producción → de 8 a ≤ 4.

### Acción 5 — Estandarizar el proceso de estimación con factor de corrección histórico *(Antes del próximo proyecto)*
- **Qué:** Documentar la velocidad real (1,38–2,00 h/punto según sprint) y aplicar un factor de ajuste de 1,25× sobre las estimaciones futuras; usar PERT como técnica base con datos históricos del equipo.
- **Métrica que mejora:** Desviación de estimación → de 25 % a ≤ 10 %; precisión de planificación de sprint.

---

## Estimación (juicio experto de la IA)

### Comparativa con las horas reales (90,0 h)

| Técnica | Total estimado (h) | Error absoluto | Error relativo |
|---|---|---|---|
| **PERT (tres puntos)** | **81,85** | **8,15 h** | **9,1 %** |
| Juicio de expertos (promedio) | 80,33 | 9,67 h | 10,7 % |
| Puntos de función ajustados | 101,12 | 11,12 h | 12,4 % |
| Estimación análoga | 126,87 | 36,87 h | 41,0 % |

### Análisis

La técnica que más se acercó a las 90 horas reales fue **PERT/tres puntos** (error del 9,1 %), seguida muy de cerca por el **juicio de expertos** (10,7 %). Esto es coherente con las características del proyecto por las siguientes razones:

1. **PERT capturó la asimetría del riesgo.** Al incluir escenarios optimista, más probable y pesimista por módulo, absorbió parcialmente la incertidumbre de los sprints con mayor variabilidad (Sprint 5: 60 % de desviación real). El rango del 95 % (72,26 – 91,44 h) **contuvo las 90 h reales**, lo que demuestra la validez estadística del método.

2. **El juicio de expertos fue casi igual de preciso** porque la estimación de la IA (Claude, 86 h) compensó hacia arriba la subestimación del alumno desarrollador (72 h), acercando el promedio ponderado a la realidad. Esto ilustra el valor de incluir perspectivas externas en el *planning poker*.

3. **La estimación análoga sobreestimó en 41 %** porque el factor de ajuste (+10 %) fue insuficiente para reflejar la diferencia real de complejidad entre un CRUD (Easy Learning) y un sistema con APIs de voz, reconocimiento y LLM. Para proyectos con componentes de IA/voz se recomienda un factor de ajuste de al menos **+60 %** sobre la línea base CRUD.

4. **Puntos de función subestimó la complejidad de integración** al no modelar explícitamente la latencia y el manejo de errores de APIs externas (Claude, ElevenLabs), que fueron precisamente los módulos con mayor desviación (Núcleo de voz: +40 %; Interfaz y servidor: +60 %).

**Recomendación para proyectos futuros:** usar PERT con los rangos calibrados por velocidad histórica (1,38–2,00 h/punto) como técnica principal, y el juicio de expertos como validación cruzada.
