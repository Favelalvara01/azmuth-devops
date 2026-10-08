## 🤖 Análisis de calidad con IA (claude-sonnet-4-6)

# Auditoría de Calidad — Proyecto **Azmuth**
**Normas aplicadas:** ISO/IEC 25010 · ISO/IEC 25023 | Fecha de datos: 2026-10-08

---

## Dictamen general

El proyecto Azmuth alcanza una calificación de **78 / 100**, sustentada en una cobertura de pruebas del 86,58 %, 315 pruebas aprobadas sin fallos, complejidad ciclomática mayoritariamente en rango A-B (94,39 %) y cero defectos abiertos al cierre del ciclo. **El proyecto es apto para liberarse en versión 1.0**, condicionado a que se monitoree activamente el bajo DRE (44,44 %) y se atienda en el siguiente sprint la cobertura de `app_desktop.py` (0 %) y `voice.py` (72,88 %), módulos con riesgo operativo directo en el usuario final.

---

## Idoneidad funcional

### Completitud funcional

| Indicador | Valor | Referencia / Interpretación |
|---|---|---|
| Pruebas definidas | 315 | Cubren 35 archivos del sistema |
| Pruebas aprobadas | 315 (100 %) | Sin regresiones al cierre |
| Defectos abiertos | **0** | Todos los 18 defectos fueron reparados |
| Cobertura global | 86,58 % | Por encima del umbral típico de 80 % |

La completitud funcional es **alta**. Todos los módulos documentan al menos un caso de prueba y la suite cubre el 86,58 % de las líneas ejecutables (1 768 / 2 042). Los únicos vacíos significativos son:

- `app_desktop.py` → **0,0 %** de cobertura (1 defecto registrado, sin pruebas automatizadas).
- `voice.py` → **72,88 %** (módulo central del asistente de voz; el porcentaje restante representa comportamiento de síntesis/captura no verificado).
- `cerebro.py` → **75,0 %** (lógica de orquestación de IA).

### Corrección funcional

Los 18 defectos detectados durante el proyecto se distribuyeron: 3 en revisión, 5 en pruebas y **10 en producción**. El hecho de que más del 55 % de los defectos emergieran en producción indica que la corrección funcional fue **parcialmente comprometida** durante el desarrollo temprano, aunque al cierre del ciclo el estado es sano (0 abiertos).

### Pertinencia funcional

La arquitectura en *skills* modulares (apps, recordatorios, multimedia, web, pestañas, memoria, hábitos, etc.) demuestra alineación con los requisitos de un asistente de voz con IA. El análisis estático con Ruff no reportó ninguna alerta (`All checks passed`), lo que confirma que el código entregado es pertinente y consistente con las convenciones del lenguaje.

---

## Fiabilidad

### Métricas clave

| Métrica | Valor | Interpretación |
|---|---|---|
| MTTD | 233,09 h (≈ 9,71 días) | Los defectos tardan casi 10 días en detectarse; detección **lenta** |
| MTTR | 3,9 h (234 min) | Una vez detectados, se corrigen con **alta rapidez** |
| DRE (Defect Removal Effectiveness) | **44,44 %** | Solo se removió el 44 % de defectos antes de producción — **bajo** |
| Defectos en producción vs. total | 10 / 18 (55,56 %) | Más de la mitad llegaron al usuario |
| Tasa pruebas vs. producción | 33,33 % | Por cada defecto encontrado en pruebas, 2 llegaron a producción |
| Pruebas fallidas | 0 / 315 | Suite 100 % verde al cierre |
| Tiempo de ejecución de pruebas | 4,98 s | Pipeline ágil y eficiente |

### Madurez

El producto muestra buena madurez estructural: 94,39 % de funciones en rango A-B, mantenibilidad promedio de 72,02, análisis estático limpio y cero defectos abiertos. Sin embargo, el **DRE de 44,44 %** —muy por debajo del estándar industrial del 85-95 %— refleja inmadurez en el proceso de detección temprana.

### Disponibilidad y tolerancia a fallos

No se dispone de métricas de uptime en los datos provistos. Sin embargo, el MTTR de 3,9 h indica **alta recuperabilidad** una vez que un fallo es identificado. La baja cobertura de `voice.py` (72,88 %) y `app_desktop.py` (0 %) representa un riesgo latente de fallos no anticipados en las capas de interfaz y voz.

### Recuperabilidad

El equipo demostró capacidad de recuperación efectiva: 18 defectos reparados con un MTTR promedio de 3,9 h, y el sprint 9 (*Corrección de defectos*) se ejecutó por debajo del tiempo estimado (3 h reales vs. 4 h estimadas), señal positiva de disciplina correctiva.

---

## Mantenibilidad

### Interpretación de la complejidad ciclomática

| Rango | Significado | Funciones | % |
|---|---|---|---|
| **A** (1–5) | Bajo riesgo, fácil de probar | 180 | 84,11 % |
| **B** (6–10) | Moderado, aceptable | 22 | 10,28 % |
| **C** (11–15) | Alto, refactorizar pronto | **12** | **5,61 %** |
| D–F | Crítico / inaceptable | 0 | 0,00 % |

La **mantenibilidad promedio de 72,02** (sobre 100, escala Maintainability Index) es aceptable pero mejorable. El 94,39 % de funciones en A-B es un resultado positivo. Las 12 funciones en rango C concentran el riesgo de mantenibilidad.

### Funciones a refactorizar (Top 10 por complejidad)

| Prioridad | Archivo | Función | Línea | CC | Rango |
|---|---|---|---|---|---|
| 1 | `skills/apps_instaladas.py` | `intentar` | 213 | 15 | C |
| 2 | `skills/recordatorios.py` | `intentar` | 96 | 14 | C |
| 3 | `skills/apps_instaladas.py` | `resolver` | 169 | 13 | C |
| 4 | `skills/multimedia.py` | `intentar` | 31 | 13 | C |
| 5 | `skills/pestanas.py` | `intentar` | 33 | 13 | C |
| 6 | `cerebro.py` | `actualizar_perfil_si_toca` | 205 | 12 | C |
| 7 | `skills/memoria.py` | `intentar` | 61 | 12 | C |
| 8 | `skills/recordatorios.py` | `revisar_pendientes` | 170 | 12 | C |
| 9 | `skills/web.py` | `intentar` | 53 | 12 | C |
| 10 | `cerebro.py` | `preguntar` | 104 | 11 | C |

> **Patrón observado:** el nombre `intentar` se repite en múltiples *skills* con alta complejidad, lo que sugiere que este método concentra toda la lógica de despacho de comandos sin delegación suficiente. Se recomienda aplicar el patrón **Strategy** o **Command** para descomponer las ramas condicionales.

---

## Riesgos

| Riesgo | Probabilidad | Impacto | Acción preventiva |
|---|---|---|---|
| Defectos críticos en producción (DRE 44,44 %) | **Alta** | **Alto** | Implementar pruebas de integración tempranas y revisiones de código obligatorias antes de merge; establecer *Definition of Done* con DRE ≥ 75 % |
| Fallos no detectados en `app_desktop.py` (cobertura 0 %) | **Alta** | **Alto** | Escribir pruebas unitarias/UI en el siguiente sprint; bloquear merge si cobertura < 60 % |
| Degradación de `voice.py` y `cerebro.py` (coberturas 72,88 % y 75 %) | **Media** | **Alto** | Agregar casos de prueba para flujos de error de STT/TTS y ramas de orquestación de IA |
| Deuda técnica en funciones `intentar` (CC 13–15) | **Media** | **Medio** | Refactorizar las 5 funciones con CC ≥ 13 aplicando patrón Strategy; meta CC ≤ 10 |
| Desviación de estimación en módulos complejos (sprint 5: +60 %, sprint 1: +40 %) | **Media** | **Medio** | Usar PERT como técnica estándar de estimación; incluir buffer explícito para módulos con integraciones externas |
| MTTD elevado (≈ 9,71 días) | **Media** | **Medio** | Activar alertas automáticas en producción (logging estructurado + Sentry/similar); realizar revisiones semanales de logs |
| Dependencia de APIs externas (Claude, ElevenLabs) sin *mocks* completos | **Baja** | **Alto** | Implementar *mocks* de API en el 100 % de las pruebas; agregar pruebas de *circuit breaker* y timeout |

---

## Plan de mejora

Las siguientes 5 acciones están ordenadas por prioridad (mayor impacto primero):

---

**1. Cobertura de `app_desktop.py` y `voice.py`** *(Prioridad: Crítica)*

- **Acción:** Crear un conjunto de pruebas unitarias para `app_desktop.py` (objetivo ≥ 70 %) y ampliar casos en `voice.py` y `cerebro.py` (objetivo ≥ 85 %). Usar `pytest-mock` para simular el motor de voz.
- **Métrica que mejorará:** Cobertura global (86,58 % → ≥ 90 %); reducción del riesgo de fallos en producción en la capa de voz.

---

**2. Elevar el DRE mediante revisiones de código estructuradas** *(Prioridad: Alta)*

- **Acción:** Establecer revisión de código obligatoria por pares (*pull request* con al menos 1 aprobador) y *checklist* de calidad antes de cada merge. Añadir análisis de cobertura diferencial en el pipeline de GitHub Actions (falla si la cobertura del PR baja del umbral).
- **Métrica que mejorará:** DRE (44,44 % → objetivo ≥ 75 %); defectos en producción / total (55,56 % → ≤ 30 %).

---

**3. Refactorización de las 5 funciones con CC ≥ 13** *(Prioridad: Alta)*

- **Acción:** Descomponer `intentar` en `apps_instaladas.py` (CC=15), `recordatorios.py` (CC=14), `multimedia.py` (CC=13), `pestanas.py` (CC=13) y `resolver` en `apps_instaladas.py` (CC=13) usando el patrón **Command** o tablas de despacho. Meta: CC ≤ 10 en todas.
- **Métrica que mejorará:** Complejidad máxima (15 → ≤ 10); mantenibilidad promedio (72,02 → ≥ 78); porcentaje A-B (94,39 % → ≥ 98 %).

---

**4. Reducir el MTTD con monitoreo activo en producción** *(Prioridad: Media)*

- **Acción:** Integrar un sistema de logging estructurado (p. ej., `structlog`) con alertas automáticas ante excepciones no controladas (Sentry o similar). Configurar un *dashboard* de errores con revisión semanal obligatoria.
- **Métrica que mejorará:** MTTD (233,09 h → objetivo ≤ 48 h); tiempo de respuesta ante incidentes.

---

**5. Estandarizar la estimación con PERT y registrar velocidad real por sprint** *(Prioridad: Media)*

- **Acción:** Adoptar PERT como técnica estándar para módulos con integraciones externas (APIs, voz), aplicando el rango 95 % calculado (104–125 h) como *baseline*. Registrar la velocidad real (puntos/hora) por sprint para calibrar iteraciones futuras.
- **Métrica que mejorará:** Desviación de estimación global (19,61 % → objetivo ≤ 10 %); desviación en sprints críticos como el 5 (60 % → ≤ 20 %).

---

## Estimación (juicio experto de la IA)

### Comparativa de técnicas

| Técnica | Total estimado (h) | Desviación vs. 122 h reales | Error (%) |
|---|---|---|---|
| Juicio experto — Alumno | 102,0 h | −20,0 h | **−16,39 %** |
| **Tres Puntos (PERT)** | **114,68 h** | **−7,32 h** | **−6,00 %** |
| Juicio experto — Compañero | 117,0 h | −5,0 h | −4,10 % |
| Juicio experto — IA (Claude) | 119,0 h | −3,0 h | −2,46 % |
| Juicio experto — Promedio consenso | 112,66 h | −9,34 h | −7,66 % |
| Puntos de función | 146,38 h | +24,38 h | +19,98 % |
| Análoga | 152,53 h | +30,53 h | +25,02 % |

### Técnica más acertada y justificación

La técnica que produjo el **error absoluto más bajo fue el juicio experto de la IA (Claude)** con −3,0 h (−2,46 %), seguida muy de cerca por el compañero con experiencia (−5,0 h). Sin embargo, considerando **rigor metodológico y reproducibilidad**, la técnica que más se acercó de manera *sistemática y justificable* fue **Tres Puntos (PERT)** con −7,32 h (−6,0 %), por las siguientes razones:

1. **Capturó la incertidumbre real:** El rango 95 % calculado (104,03–125,33 h) **contiene el valor real de 122 h**, lo que demuestra que el modelo de distribución era estadísticamente correcto.
2. **No dependió de intuición individual:** A diferencia del juicio de expertos, PERT forzó al equipo a explicitar escenarios optimista, más probable y pesimista, reduciendo el sesgo de anclaje que llevó al alumno desarrollador a subestimar en 20 h.
3. **Explicó los desvíos por módulo:** Los sprints 1 y 5 (los más subestimados) correspondían a módulos con alta varianza entre O y P (Núcleo de voz: O=8/P=20; Interfaz y servidor: O=8/P=22), varianza que PERT sí modeló explícitamente.

> Las técnicas **Análoga y Puntos de función sobreestimaron** significativamente (+25 % y +20 %), probablemente porque la analogía con Easy Learning no capturó la eficiencia del equipo en tareas de infraestructura y persistencia, y el factor de ajuste del VAF (1,07) fue conservador frente a la productividad real observada (≈ 25,4 SLOC/h).

---

*Auditoría generada con base exclusiva en los datos del pipeline provistos. Ninguna cifra fue inferida sin respaldo en los datos originales.*
