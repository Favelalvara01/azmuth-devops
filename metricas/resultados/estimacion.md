## ⏱️ Estimación del proyecto Azmuth

### 1. Juicio de expertos

| Módulo | Alumno desarrollador | IA (Claude) - analisis del codigo | Promedio |
|---|---|---|---|
| Nucleo de voz | 10 | 14 | 12 |
| Skills basicas | 12 | 13 | 12.5 |
| Control del sistema | 14 | 17 | 15.5 |
| IA y memoria | 12 | 13 | 12.5 |
| Interfaz y servidor | 10 | 15 | 12.5 |
| Persistencia SQLite | 6 | 5 | 5.5 |
| DevOps | 8 | 9 | 8.5 |
| Modo escritorio y apps | 10 | 12 | 11 |
| Correccion de defectos | 4 | 4 | 4 |
| Calidad y seguridad | 8 | 8 | 8 |
| Nuevas funciones | 8 | 9 | 8.5 |
| **Total** | 102 | 119 | **110.5** |

### 2. Estimación análoga

Proyecto de referencia: Easy Learning (proyecto integrador DSM31, C#/MySQL) — 1800 SLOC en 80 h → 22.5 SLOC/h. Azmuth: 3120 SLOC × factor 1.1 = **152.53 h**.

### 3. Tres puntos (PERT)

| Módulo | O | M | P | PERT | Triangular | σ |
|---|---|---|---|---|---|---|
| Nucleo de voz | 8 | 12 | 20 | 12.67 | 13.33 | 2.0 |
| Skills basicas | 9 | 13 | 20 | 13.5 | 14.0 | 1.83 |
| Control del sistema | 10 | 15 | 24 | 15.67 | 16.33 | 2.33 |
| IA y memoria | 9 | 12 | 18 | 12.5 | 13.0 | 1.5 |
| Interfaz y servidor | 8 | 13 | 22 | 13.67 | 14.33 | 2.33 |
| Persistencia SQLite | 3 | 5 | 8 | 5.17 | 5.33 | 0.83 |
| DevOps | 6 | 8 | 14 | 8.67 | 9.33 | 1.33 |
| Modo escritorio y apps | 8 | 11 | 16 | 11.33 | 11.67 | 1.33 |
| Correccion de defectos | 2 | 4 | 6 | 4.0 | 4.0 | 0.67 |
| Calidad y seguridad | 5 | 8 | 12 | 8.17 | 8.33 | 1.17 |
| Nuevas funciones | 6 | 9 | 14 | 9.33 | 9.67 | 1.33 |
| **Total** | | | | **114.68** | | 5.32 |

Con 95 % de confianza: entre 104.03 y 125.33 horas.

### 4. Puntos de función

| Tipo | Complejidad | Cantidad | Peso | Subtotal |
|---|---|---|---|---|
| EI | simple | 16 | 3 | 48 |
| EI | media | 5 | 4 | 20 |
| EI | compleja | 1 | 6 | 6 |
| EO | media | 5 | 5 | 25 |
| EO | compleja | 5 | 7 | 35 |
| EQ | simple | 8 | 3 | 24 |
| EQ | media | 5 | 4 | 20 |
| ILF | simple | 5 | 7 | 35 |
| ILF | media | 5 | 10 | 50 |
| EIF | simple | 4 | 5 | 20 |
| EIF | media | 3 | 7 | 21 |
| **PFNA** | | | | **304** |

VAF = 0.65 + 0.01 × 42 = 1.07 → PFA = 325.28 → 325.28 × 0.45 h/PF = **146.38 h**.

### Comparación

| Técnica | Horas estimadas |
|---|---|
| Juicio de expertos | 110.5 |
| Análoga | 152.53 |
| Tres puntos (PERT) | 114.68 |
| Puntos de función | 146.38 |
| **Real (registro de sprints)** | **122.0** |
