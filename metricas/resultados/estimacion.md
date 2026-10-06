## ⏱️ Estimación del proyecto Azmuth

### 1. Juicio de expertos

| Módulo | Alumno desarrollador | Companero con experiencia | IA (Claude) - analisis del codigo | Promedio |
|---|---|---|---|---|
| Nucleo de voz | 10 | 12 | 14 | 12 |
| Skills basicas | 12 | 14 | 13 | 13 |
| Control del sistema | 14 | 16 | 17 | 15.67 |
| IA y memoria | 12 | 12 | 13 | 12.33 |
| Interfaz y servidor | 10 | 14 | 15 | 13 |
| Persistencia SQLite | 6 | 5 | 5 | 5.33 |
| DevOps | 8 | 10 | 9 | 9 |
| **Total** | 72 | 83 | 86 | **80.33** |

### 2. Estimación análoga

Proyecto de referencia: Easy Learning (proyecto integrador DSM31, C#/MySQL) — 1800 SLOC en 80 h → 22.5 SLOC/h. Azmuth: 2059 SLOC × factor 1.1 = **100.66 h**.

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
| **Total** | | | | **81.85** | | 4.79 |

Con 95 % de confianza: entre 72.26 y 91.44 horas.

### 4. Puntos de función

| Tipo | Complejidad | Cantidad | Peso | Subtotal |
|---|---|---|---|---|
| EI | simple | 10 | 3 | 30 |
| EI | media | 4 | 4 | 16 |
| EI | compleja | 1 | 6 | 6 |
| EO | media | 4 | 5 | 20 |
| EO | compleja | 3 | 7 | 21 |
| EQ | simple | 6 | 3 | 18 |
| EQ | media | 3 | 4 | 12 |
| ILF | simple | 3 | 7 | 21 |
| ILF | media | 3 | 10 | 30 |
| EIF | simple | 3 | 5 | 15 |
| EIF | media | 3 | 7 | 21 |
| **PFNA** | | | | **210** |

VAF = 0.65 + 0.01 × 42 = 1.07 → PFA = 224.7 → 224.7 × 0.45 h/PF = **101.12 h**.

### Comparación

| Técnica | Horas estimadas |
|---|---|
| Juicio de expertos | 80.33 |
| Análoga | 100.66 |
| Tres puntos (PERT) | 81.85 |
| Puntos de función | 101.12 |
| **Real (registro de sprints)** | **90.0** |
