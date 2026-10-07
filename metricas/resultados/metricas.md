## 📊 Métricas de calidad — Azmuth

_Generado: 2026-10-07 07:05_

### Métricas de producto

| Métrica | Valor |
|---|---|
| Complejidad ciclomática promedio | 4.06 (149 funciones) |
| Complejidad máxima | 27 |
| Funciones en rango A-B (simples) | 90.6 % |
| Cobertura de código | 76.62 % |
| Tamaño | 2595 SLOC (2.6 KLOC) |
| Densidad de defectos | 6.17 defectos/KLOC |
| Defectos abiertos | 1 (0.39/KLOC) |
| Índice de mantenibilidad promedio | 71.83 |

**Funciones más complejas**

| Archivo | Función | CC | Rango |
|---|---|---|---|
| servidor.py | ejecutar_accion | 27 | D |
| skills/aplicaciones.py | intentar | 24 | D |
| skills/apps_instaladas.py | intentar | 15 | C |
| skills/recordatorios.py | intentar | 14 | C |
| skills/apps_instaladas.py | resolver | 13 | C |
| skills/multimedia.py | intentar | 13 | C |
| skills/pestanas.py | intentar | 13 | C |
| cerebro.py | actualizar_perfil_si_toca | 12 | C |
| main.py | escuchar | 12 | C |
| skills/memoria.py | intentar | 12 | C |

### Métricas de proceso

| Métrica | Valor |
|---|---|
| Tiempo medio de detección (MTTD) | 262.18 h (10.92 días) |
| Tiempo medio de reparación (MTTR) | 2.52 h (151 min) |
| Defectos detectados en pruebas | 5 |
| Eficiencia de remoción antes de producción (DRE) | 50.0 % |
| Defectos por fase | {'revision': 3, 'pruebas': 5, 'produccion': 8} |
| Pruebas automatizadas | 167/167 aprobadas, 0 fallidas, 0 defectos conocidos (xfail) |

### Métricas de proyecto

| Métrica | Valor |
|---|---|
| Eficacia de la revisión | 18.75 % (3/16) |
| Desviación total de tiempo | 25.0 % (90.0 h reales vs 72.0 h) |
| Velocidad promedio | 7.86 puntos/sprint |

| Sprint | Módulo | Est. (h) | Real (h) | Desv. % | SLOC | Defectos | Def/KLOC |
|---|---|---|---|---|---|---|---|
| 1 | Nucleo de voz | 10.0 | 14.0 | 40.0 | 296 | 5 | 16.89 |
| 2 | Skills basicas | 12.0 | 15.0 | 25.0 | 283 | 1 | 3.53 |
| 3 | Control del sistema | 14.0 | 18.0 | 28.57 | 335 | 2 | 5.97 |
| 4 | IA y memoria | 12.0 | 13.0 | 8.33 | 408 | 1 | 2.45 |
| 5 | Interfaz y servidor | 10.0 | 16.0 | 60.0 | 683 | 5 | 7.32 |
| 6 | Persistencia SQLite | 6.0 | 5.0 | -16.67 | 230 | 0 | 0.0 |
| 7 | DevOps | 8.0 | 9.0 | 12.5 | 0 | 0 | N/A |
