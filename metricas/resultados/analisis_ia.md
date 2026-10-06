## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
**Normas:** ISO/IEC 25010 · ISO/IEC 25023 | **Fecha de datos:** 2026-10-06 18:34

---

## Dictamen general

El proyecto Azmuth alcanza una calificación estimada de **61 / 100**, apoyada en una cobertura de pruebas del 72,52 %, un índice de mantenibilidad promedio de 72,97/100 y un pipeline DevOps funcional; sin embargo, la baja eficacia de detección de defectos en pruebas (DRE 53,33 %), los cinco defectos abiertos, la cobertura nula en dos archivos críticos (`app_desktop.py`, `skills/interfaz.py`) y las dos funciones con complejidad ciclomática en rango D representan riesgos que deben mitigarse antes de la liberación. **El producto NO se recomienda para liberación en su estado actual**; se estima que con dos a tres semanas de trabajo correctivo y preventivo podría alcanzar el umbral mínimo de liberación (≥ 75/100).

---

## Idoneidad funcional

### Completitud funcional
- **112 pruebas** ejecutadas; 109 aprobadas, 0 fallidas, 3 marcadas como `xfail` (defectos conocidos y aceptados). Esto indica que el conjunto de funcionalidades comprometidas está mayoritariamente implementado.
- Sin embargo, **`app_desktop.py` (0 % cobertura)** y **`skills/interfaz.py` (0 % cobertura)** no tienen ninguna prueba asociada; su completitud funcional es opaca y no verificable.
- **`main.py` solo alcanza el 27,95 % de cobertura** — módulo de punto de entrada crítico para el flujo de escucha de voz.

### Corrección funcional
- **15 defectos totales**, 10 reparados, **5 abiertos**. Con 2,43 defectos abiertos por KLOC el nivel es moderado-alto para un asistente de voz (umbral aceptable recomendado: < 1,5/KLOC antes de liberación).
- El módulo con mayor densidad de defectos es **"Núcleo de voz" (Sprint 1): 17,48 defectos/KLOC** — el componente más expuesto al usuario final.
- 7 de los 15 defectos se detectaron **en producción**, señal de que las pruebas no capturan escenarios reales suficientemente.
- El análisis estático Ruff reporta **42 errores** (5 importaciones sin uso — F401, 1 f-string vacío — F541, múltiples líneas largas — E501, y ausencia de nueva línea final — W292); 28 son autocorregibles, lo que indica descuido en la higiene de código.

### Pertinencia funcional
- Las skills cubiertas (recordatorios, multimedia, pestañas, web, contactos, memoria, notas, hábitos, sistema, tiempo) son pertinentes para un asistente de voz doméstico en Windows.
- La integración con APIs externas (Claude, ElevenLabs) eleva la pertinencia del producto, aunque también incrementa la superficie de fallo fuera del control del equipo.

---

## Fiabilidad

### Métricas clave

| Indicador | Valor | Interpretación |
|---|---|---|
| **MTTD** | 279,62 h (≈ 11,65 días) | Tiempo elevado; los defectos tardan casi dos semanas en ser detectados |
| **MTTR** | 0,82 h (49 min) | Excelente; una vez identificado el defecto, la corrección es muy ágil |
| **DRE** | 53,33 % | Crítico: solo la mitad de los defectos se detectan antes de producción (meta recomendada ≥ 85 %) |
| **Defectos en producción** | 7 / 15 (46,67 %) | Más defectos escapan a producción de los que se capturan en pruebas |
| **Graves detectados en pruebas** | 0 / 4 | Los 4 defectos graves llegaron a producción sin ser interceptados |

### Madurez
Con 10 defectos reparados sobre 15 totales, la tasa de reparación es del 66,67 %. Los 3 `xfail` registrados formalmente muestran madurez de proceso, aunque los 5 defectos abiertos deben cerrarse antes de la liberación.

### Disponibilidad y tolerancia a fallos
No se dispone de métricas de uptime en los datos, pero la cobertura nula en `app_desktop.py` y `skills/interfaz.py` implica que las rutas de interfaz gráfica y de interacción visual no tienen pruebas de tolerancia a fallos verificadas. El MTTD de casi 12 días sugiere una capacidad de monitoreo reactivo, no proactivo.

### Recuperabilidad
El MTTR de 49 minutos es el punto más positivo de la dimensión de fiabilidad: el equipo recupera el sistema ante un defecto en menos de una hora, lo cual es compatible con un entorno de desarrollo ágil con pipeline CI/CD activo.

---

## Mantenibilidad

### Índice de mantenibilidad
- **Promedio:** 72,97 / 100 — nivel **aceptable** (umbral recomendado ≥ 65; óptimo ≥ 85).
- El valor por sí solo es moderado; se deben observar los módulos individuales con complejidad alta.

### Distribución de complejidad ciclomática

| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Simple, bajo riesgo | 72 | 75,0 % |
| **B** (6–10) | Moderada, manejable | 13 | 13,54 % |
| **C** (11–15) | Compleja, candidata a revisión | 9 | 9,38 % |
| **D** (16–25) | Alta complejidad, refactorización necesaria | 2 | 2,08 % |
| **E / F** (> 25) | Muy alta / Crítica | 0 | 0,00 % |

El **88,54 %** de funciones están en rango A-B — positivo. Sin embargo, los dos casos en rango D son prioritarios.

### Funciones a refactorizar (priorizadas)

| Prioridad | Archivo | Función | Línea | CC | Rango | Acción sugerida |
|---|---|---|---|---|---|---|
| 🔴 1 | `servidor.py` | `ejecutar_accion` | 44 | 27 | **D** | Descomponer en funciones por tipo de acción (patrón Strategy o tabla de despacho) |
| 🔴 2 | `skills/aplicaciones.py` | `intentar` | 120 | 24 | **D** | Extraer ramas en métodos especializados (`_abrir_app`, `_cerrar_app`, etc.) |
| 🟠 3 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C | Separar lógica de parsing de la de ejecución |
| 🟠 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | C | Extraer casos en métodos de control de reproducción |
| 🟠 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | C | Mismo patrón: tabla de despacho por intención |
| 🟡 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 115 | 12 | C | Simplificar condiciones con early returns |
| 🟡 7 | `main.py` | `escuchar` | 103 | 12 | C | Separar el bucle de captura de la lógica de procesamiento |
| 🟡 8 | `skills/memoria.py` | `intentar` | 61 | 12 | C | Igual que otras skills: tabla de despacho |
| 🟡 9 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 | C | Extraer evaluación de condiciones a funciones auxiliares |
| 🟡 10 | `skills/web.py` | `intentar` | 54 | 12 | C | Separar apertura de URLs de búsquedas y navegación |

> **Patrón detectado:** la mayoría de las funciones `intentar` de los skills son monolíticas (gran bloque `if/elif`). Una refactorización sistemática con tabla de despacho o patrón Command reduciría la complejidad en todo el módulo de skills simultáneamente.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| **Defectos graves escapan a producción** (DRE 53,33 %; 4 graves sin detectar en pruebas) | Alta | Alto | Añadir casos de prueba específicos para escenarios de fallo de API externa (Claude, ElevenLabs) y rutas de error en `main.py` |
| **Cobertura nula en `app_desktop.py` y `skills/interfaz.py`** | Alta | Alto | Crear suite de pruebas de integración/GUI (pytest-qt o mocks de UI) antes de liberación |
| **MTTD de ~12 días** — defectos latentes no detectados rápidamente | Media | Alto | Implementar monitoreo de errores en runtime (logging estructurado + alertas automáticas) |
| **Funciones con CC ≥ 24 (`ejecutar_accion`, `intentar` en aplicaciones)** generan errores difíciles de depurar | Media | Medio | Refactorizar antes de liberación; agregar pruebas unitarias por rama lógica |
| **Desviación del 25 % en estimación** (72 h estimadas vs 90 h reales); Sprint 5 con 60 % de desviación | Alta | Medio | Incorporar factor de ajuste histórico (≥ 1,25×) en futuros proyectos similares y usar tres puntos como técnica base |
| **42 hallazgos de análisis estático** (importaciones sin uso, líneas largas, f-strings vacíos) sin política de calidad de código obligatoria | Alta | Bajo | Activar `ruff --fix` en el hook pre-commit y como paso bloqueante en el pipeline CI |
| **Dependencia de APIs externas sin circuit breaker** | Media | Alto | Implementar patrón circuit breaker / fallback local para las integraciones con Claude y ElevenLabs |
| **Cobertura de `main.py` al 27,95 %** — módulo orquestador crítico | Alta | Alto | Aislar la lógica de `escuchar()` del I/O de hardware para poder probarla con mocks de micrófono |

---

## Plan de mejora

A continuación, las cinco acciones priorizadas bajo enfoque preventivo:

---

### Acción 1 🔴 — Cerrar los 5 defectos abiertos
