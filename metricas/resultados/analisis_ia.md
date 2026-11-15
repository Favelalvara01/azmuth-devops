## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto Azmuth
**ISO/IEC 25010 · ISO/IEC 25023 | Generado: 2026-11-14 03:24**

---

## Dictamen general

El proyecto Azmuth alcanza una calificación de **78 / 100**, sustentada en una cobertura de pruebas del 87,9 %, cero defectos abiertos, análisis estático sin hallazgos (Ruff) y una complejidad ciclomática predominantemente en rangos A-B (94,63 %). El proyecto **puede liberarse condicionalmente**, siempre que se atienda la cobertura crítica de `app_desktop.py` (0 %), se reduzca la complejidad de las diez funciones en rango C y se mejore la eficacia de detección de defectos (DRE = 52,17 %), que revela una brecha significativa de pruebas preventivas antes de producción.

---

## Idoneidad funcional

### Completitud funcional
| Indicador | Valor | Referencia |
|---|---|---|
| Pruebas totales ejecutadas | 576 | — |
| Pruebas aprobadas | 567 (98,44 %) | Umbral recomendado ≥ 95 % ✅ |
| Defectos conocidos (xfail) | 9 | Documentados, no bloqueantes |
| Defectos abiertos | 0 | ✅ |
| Cobertura global | 87,9 % | Umbral recomendado ≥ 80 % ✅ |

La funcionalidad declarada está cubierta en un nivel aceptable. Los 9 casos `xfail` representan comportamientos conocidos y controlados, no funciones faltantes. El único módulo sin cobertura es `app_desktop.py` (0 %), lo que implica que su funcionalidad **no está verificada** en absoluto.

### Corrección funcional
De los 23 defectos históricos, **todos fueron corregidos** (0 abiertos). Sin embargo, 10 defectos llegaron a producción antes de ser detectados, lo que indica que la corrección ocurrió de forma reactiva en varios casos. La distribución por archivo muestra concentración en `main.py` (4), `servidor.py` (3) y `estado.py` (3).

### Pertinencia funcional
Las skills implementadas (tiempo, recordatorios, multimedia, pestañas, web, apps, contactos, hábitos, notas, idiomas) corresponden a un asistente de voz funcional y completo para Windows. La integración con Deepseek, Gemini y Groq amplía la pertinencia del producto para su propósito declarado.

---

## Fiabilidad

### Métricas clave
| Métrica | Valor | Interpretación |
|---|---|---|
| MTTD | 334,65 h (13,94 días) | Los defectos tardan ~2 semanas en detectarse; refleja que 10/23 llegaron a producción |
| MTTR | 3,08 h (185 min) | Excelente capacidad de corrección una vez detectado el defecto ✅ |
| DRE (Defect Removal Efficiency) | 52,17 % | **Crítico** ⚠️ — menos de la mitad de los defectos se eliminaron antes de producción |
| Defectos graves detectados en pruebas | 3 de 7 (42,86 %) | Solo 4 defectos graves llegaron a producción, pero es un riesgo real |

### Madurez
Con 0 defectos abiertos y 576 pruebas ejecutadas sin fallas, el producto muestra señales de madurez al momento del cierre. No obstante, el MTTD elevado sugiere que los ciclos de retroalimentación de pruebas son lentos o que la observabilidad en etapas tempranas es insuficiente.

### Disponibilidad y tolerancia a fallos
El pipeline de GitHub Actions y la contenedorización con Docker proveen una base de disponibilidad y aislamiento aceptable. La presencia del módulo `monitoreo.py` (88,89 % cobertura) es positiva. No se reportan métricas de uptime en los datos, por lo que no es posible calcular disponibilidad operacional.

### Recuperabilidad
El MTTR de 3,08 h es un indicador sólido de recuperabilidad del proceso de desarrollo. Para el sistema en ejecución, `confirmaciones.py` y `nucleo.py` tienen cobertura del 100 %, lo que refuerza la confianza en los flujos críticos de recuperación de estado.

---

## Mantenibilidad

### Índice de mantenibilidad
El índice promedio es **68,56 / 100**, ubicándose en la categoría **moderada** (rango típico aceptable: 65–85). No es preocupante, pero tampoco holgado; el margen de degradación antes de volverse difícil de mantener es reducido.

### Complejidad ciclomática — Distribución
| Rango | Significado | Cantidad | % |
|---|---|---|---|
| **A** (1–5) | Excelente, bajo riesgo | 245 | 82,21 % |
| **B** (6–10) | Moderada, manejable | 37 | 12,42 % |
| **C** (11–15) | Alta, refactorización recomendada | 16 | 5,37 % |
| **D** (16–20) | Muy alta, refactorización urgente | 0 | 0 % |
| **E** (21–25) | Crítica | 0 | 0 % |
| **F** (> 25) | Inmanejable | 0 | 0 % |

> **94,63 % en rangos A-B** es un resultado muy positivo. El riesgo se concentra en el 5,37 % restante (rango C).

### Funciones prioritarias a refactorizar (rango C)

| # | Archivo | Función | Línea | CC | Acción sugerida |
|---|---|---|---|---|---|
| 1 | `tematicas.py` | `_sintetizar` | 238 | 16 | Extraer ramas de síntesis en métodos especializados por tipo de tema |
| 2 | `skills/tiempo.py` | `_pronostico` | 100 | 16 | Separar lógica de parsing, formateo y condiciones climáticas |
| 3 | `skills/apps_instaladas.py` | `intentar` | 210 | 15 | Aplicar patrón *Command* o tabla de despacho para reducir condicionales |
| 4 | `skills/recordatorios.py` | `intentar` | 96 | 14 | Extraer validaciones de fecha/hora a funciones auxiliares |
| 5 | `skills/apps_instaladas.py` | `resolver` | 166 | 13 | Dividir resolución por categoría de aplicación |
| 6 | `skills/multimedia.py` | `intentar` | 34 | 13 | Separar control de reproducción, volumen y búsqueda |
| 7 | `skills/pestanas.py` | `intentar` | 36 | 13 | Descomponer por acción de pestaña (abrir, cerrar, navegar) |
| 8 | `skills/tiempo.py` | `_recomendaciones` | 71 | 13 | Externalizar reglas de recomendación a estructura de datos |
| 9 | `skills/web.py` | `intentar` | 93 | 13 | Aplicar despacho por intención detectada |
| 10 | `deepseek_ia.py` | `completar` | 82 | 12 | Separar construcción de prompt, llamada HTTP y manejo de errores |

### Archivos con baja cobertura y alta deuda técnica

| Archivo | Cobertura | Riesgo |
|---|---|---|
| `app_desktop.py` | 0,0 % | 🔴 Crítico — ninguna prueba |
| `voice.py` | 72,88 % | 🟡 Moderado |
| `skills/multimedia.py` | 74,55 % | 🟡 Moderado — también alta CC |
| `skills/web.py` | 75,0 % | 🟡 Moderado — también alta CC |
| `deepseek_ia.py` | 75,0 % | 🟡 Moderado — también alta CC |
| `skills/_compat.py` | 53,85 % | 🟠 Alto |

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| `app_desktop.py` sin cobertura (0 %) puede ocultar defectos críticos en la GUI | Alta | Alto | Crear suite de pruebas con `pytest-qt` o mocks de la interfaz; meta mínima: 70 % antes del próximo sprint |
| DRE del 52,17 % implica que ~48 % de defectos escapan a producción | Alta | Alto | Implementar revisiones de código obligatorias (PR reviews) y ampliar pruebas de integración para skills con lógica compleja |
| MTTD de ~14 días indica detección tardía de defectos | Media | Alto | Habilitar alertas automáticas en el pipeline (fallos de smoke tests en cada merge a `main`) y añadir pruebas de regresión |
| 10 funciones en rango C incrementan el costo de cambio futuro | Media | Medio | Incluir refactorización de las top-10 funciones como tarea técnica en el backlog del próximo sprint |
| Baja cobertura en `skills/_compat.py` (53,85 %) puede afectar compatibilidad en distintas versiones de Windows | Media | Medio | Añadir pruebas parametrizadas que simulen distintos entornos; usar `tox` para matrices de versión |
| Desviación de estimación del 19,61 % (20 h extra) puede generar déficit en proyectos futuros | Media | Medio | Adoptar estimación de tres puntos (PERT) como estándar, que acotó el real dentro de su intervalo del 95 % |
| Sprint 5 (Interfaz y servidor) con desviación del 60 % y 7 defectos concentra la mayor deuda | Media | Alto | Realizar retrospectiva de estimación y asignar spike técnico en futuros módulos de interfaz |
| `deepseek_ia.py` con CC=12 y cobertura del 75 % expone fallos silenciosos en el modelo de IA | Baja | Alto | Implementar pruebas de contrato (mocks de API) y manejo explícito de errores HTTP 4xx/5xx |

---

## Plan de mejora

> Las acciones están ordenadas por **prioridad descendente** (impacto en calidad × urgencia).

### 🥇 Acción 1 — Cubrir `app_desktop.py` con pruebas
**Prioridad: Crítica**
Crear pruebas unitarias e integración para `app_desktop.py` usando mocks o `pytest-qt`. Establecer una cobertura mínima del 70 % como *quality gate* en el pipeline (GitHub Actions rechaza merge si no se alcanza).
- **Métrica que mejora:** Cobertura global (87,9 % → ~89–90 %) y DRE (reduce defectos que escapan a producción).

### 🥈 Acción 2 — Incrementar el DRE mediante pruebas de integración ampliadas
**Prioridad: Alta**
Diseñar pruebas de integración que simulen flujos completos usuario→skill→respuesta para los módulos con más defectos en producción (`main.py`, `servidor.py`, `estado.py`). Integrar revisiones de pares obligatorias en PRs.
- **Métrica que mejora:** DRE (52,17 % → objetivo ≥ 75 %) y reducción de defectos en producción.

### 🥉 Acción 3 — Refactorizar las 10 funciones en rango C
**Prioridad: Alta**
Iniciar con `_sintetizar` y `_pronostico` (CC=16) aplicando extracción de métodos y tablas de despacho. Añadir como criterio de *done* en el Definition of Done que ninguna función nueva supere CC=10 (rango B).
- **Métrica que mejora:** Complejidad ciclomática máxima (16 → ≤ 10), índice de mantenibilidad (68,56 → objetivo ≥ 75).

### 4️⃣ Acción 4 — Mejorar cobertura de `skills/_compat.py`, `voice.py`, `skills/web.py` y `deepseek_ia.py`
**Prioridad: Media**
Añadir pruebas parametrizadas para `_compat.py` con distintas versiones de dependencias. Para `voice.py` y `deepseek_ia.py`, usar mocks de las APIs externas (ElevenLabs, Deepseek) a fin de cubrir ramas de error actualmente sin prueba.
- **Métrica que mejora:** Cobertura por archivo (todos por encima del 80 %) y fiabilidad ante fallos de APIs externas.

### 5️⃣ Acción 5 — Reducir el MTTD con observabilidad proactiva
**Prioridad: Media**
Configurar *smoke tests* automáticos que se ejecuten en cada push a `main` (no solo en PRs) y agregar logging estructurado con alertas en `monitoreo.py`. Evaluar integrar Sentry o equivalente para captura de excepciones en tiempo real.
- **Métrica que mejora:** MTTD (334,65 h → objetivo ≤ 72 h), disponibilidad percibida del sistema.

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas vs. horas reales (122 h)

| Técnica | Estimación (h) | Error absoluto | Error % |
|---|---|---|---|
| Juicio experto — Alumno desarrollador | 102,0 | 20,0 h | 16,39 % |
| Juicio experto — IA (Claude) | 119,0 | 3,0 h | 2,46 % |
| **Juicio experto — Promedio combinado** | **110,5** | **11,5 h** | **9,43 %** |
| **Tres puntos (PERT)** | **114,68** | **7,32 h** | **6,00 %** |
| Puntos de función | 146,38 | 24,38 h | 19,98 % |
| Analogía | 195,8 | 73,8 h | 60,49 % |

### Técnica más acertada: **Juicio experto de la IA (Claude) — 119 h**

La estimación individual del asistente de IA fue la que más se acercó a las 122 horas reales, con apenas **3 horas de diferencia (2,46 %)**, por delante incluso del PERT (6 %) y del promedio combinado (9,43 %). Esto se explica por varios factores:

1. **Acceso al código fuente real**: La IA analizó el repositorio módulo por módulo, estimando con base en SLOC proyectado, dependencias de APIs externas y complejidad de integración, en lugar de basarse únicamente en la experiencia subjetiva o en analogías de proyectos distintos.
2. **Corrección sistemática al alza**: En todos los módulos donde el alumno subestimó (Núcleo de voz, Control del sistema, Interfaz y servidor), la IA estimó valores superiores y más cercanos al real.
3. **El PERT también fue robusto**: Con un rango del 95 % de [104,03 h – 125,33 h], el valor real de 122 h queda **dentro del intervalo**, lo que confirma que como técnica formal para futuros proyectos, **PERT es la opción más confiable y replicable**, ya que cuantifica la incertidumbre de forma explícita.
4. **La analogía sobrestimó gravemente** (195,8 h, error del 60 %) porque el factor de ajuste del +10 % fue insuficiente para compensar que la referencia (Easy Learning, 1 800 SLOC, CRUD) es cualitativamente muy diferente a Azmuth (4 005 SLOC, voz, IA, APIs externas).

> **Recomendación para proyectos futuros**: combinar el juicio de la IA con la técnica de tres puntos (PERT). El juicio da la ancla más precisa módulo a módulo; el PERT aporta el intervalo de confianza estadístico para negociar plazos y buffers con el equipo.
