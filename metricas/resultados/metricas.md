## 📊 Métricas de calidad — Azmuth

_Generado: 2026-10-06 18:53_

### Métricas de producto

| Métrica | Valor |
|---|---|
| Complejidad ciclomática promedio | 4.46 (96 funciones) |
| Complejidad máxima | 27 |
| Funciones en rango A-B (simples) | 88.54 % |
| Cobertura de código | 72.52 % |
| Tamaño | 2059 SLOC (2.06 KLOC) |
| Densidad de defectos | 7.29 defectos/KLOC |
| Defectos abiertos | 5 (2.43/KLOC) |
| Índice de mantenibilidad promedio | 72.97 |

**Funciones más complejas**

| Archivo | Función | CC | Rango |
|---|---|---|---|
| servidor.py | ejecutar_accion | 27 | D |
| skills/aplicaciones.py | intentar | 24 | D |
| skills/recordatorios.py | intentar | 14 | C |
| skills/multimedia.py | intentar | 13 | C |
| skills/pestanas.py | intentar | 13 | C |
| cerebro.py | actualizar_perfil_si_toca | 12 | C |
| main.py | escuchar | 12 | C |
| skills/memoria.py | intentar | 12 | C |
| skills/recordatorios.py | revisar_pendientes | 12 | C |
| skills/web.py | intentar | 12 | C |

### Métricas de proceso

| Métrica | Valor |
|---|---|
| Tiempo medio de detección (MTTD) | 279.62 h (11.65 días) |
| Tiempo medio de reparación (MTTR) | 0.82 h (49 min) |
| Defectos detectados en pruebas | 5 |
| Eficiencia de remoción antes de producción (DRE) | 53.33 % |
| Defectos por fase | {'revision': 3, 'pruebas': 5, 'produccion': 7} |
| Pruebas automatizadas | 109/112 aprobadas, 0 fallidas, 3 defectos conocidos (xfail) |

### Métricas de proyecto

| Métrica | Valor |
|---|---|
| Eficacia de la revisión | 20.0 % (3/15) |
| Desviación total de tiempo | 25.0 % (90.0 h reales vs 72.0 h) |
| Velocidad promedio | 7.86 puntos/sprint |

| Sprint | Módulo | Est. (h) | Real (h) | Desv. % | SLOC | Defectos | Def/KLOC |
|---|---|---|---|---|---|---|---|
| 1 | Nucleo de voz | 10.0 | 14.0 | 40.0 | 286 | 5 | 17.48 |
| 2 | Skills basicas | 12.0 | 15.0 | 25.0 | 275 | 1 | 3.64 |
| 3 | Control del sistema | 14.0 | 18.0 | 28.57 | 335 | 2 | 5.97 |
| 4 | IA y memoria | 12.0 | 13.0 | 8.33 | 396 | 1 | 2.53 |
| 5 | Interfaz y servidor | 10.0 | 16.0 | 60.0 | 562 | 5 | 8.9 |
| 6 | Persistencia SQLite | 6.0 | 5.0 | -16.67 | 197 | 0 | 0.0 |
| 7 | DevOps | 8.0 | 9.0 | 12.5 | 0 | 0 | N/A |
