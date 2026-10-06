# AZMUTH — Asistente personal con IA + DevOps

![CI Azmuth](https://github.com/Favelalvara01/azmuth-devops/actions/workflows/ci.yml/badge.svg)

**Autor:** Osiel Alberto Favela Alvarado — DSM51, Universidad Tecnológica de Ciudad Juárez
**Materia:** Estándares y Métricas para el Desarrollo de Software

Azmuth es un asistente personal de voz para Windows (estilo J.A.R.V.I.S.). Escucha una
palabra clave, resuelve comandos con *skills* locales (notas, recordatorios, apps,
música, WhatsApp, clima…) y, si ninguna aplica, conversa con **Claude (Anthropic)**,
aprendiendo datos del usuario de forma automática. Habla con **ElevenLabs** y tiene una
interfaz animada (PyWebView + FastAPI) que también se controla desde el celular vía Ngrok.

La documentación funcional del agente está en [AGENTE.md](AGENTE.md).

## ¿Por qué DevOps en este proyecto? (justificación)

| Problema real del proyecto | Práctica DevOps aplicada |
|---|---|
| Cada cambio en una skill podía romper otra (el orden de las skills ya causó defectos) | **Pruebas automatizadas** (pytest, 112 casos) que corren en cada *push* |
| El código depende de APIs externas que cambian (un modelo de Claude retirado dio error 404) | **Prueba de regresión** del modelo configurado + mocks de la API |
| Se instala en 2 computadoras (PC 24/7 y laptop) y las dependencias fallaban (pyngrok, pyaudio) | **Integración continua** en entorno limpio + **contenedor Docker** reproducible |
| Las claves (.env) y datos personales no deben publicarse | **.gitignore / .dockerignore** y **GitHub Secrets** |
| Se necesita medir la calidad, no suponerla | **Métricas automáticas** (complejidad, cobertura, defectos, MTTD/MTTR) en cada ejecución |
| Interpretar las métricas lleva tiempo | **IA (Claude)** que analiza las métricas y propone acciones preventivas |

## Pipeline CI/CD (`.github/workflows/ci.yml`)

```
push / pull request
   │
   ├─ Job "calidad"
   │    1. ruff (gate)          → errores de sintaxis / nombres indefinidos
   │    2. ruff (reporte)       → estilo y código sin uso
   │    3. pytest + cobertura   → 112 pruebas, reporte JUnit y coverage.json
   │    4. radon                → complejidad ciclomática y mantenibilidad
   │    5. calcular_metricas.py → producto, proceso, proyecto
   │    6. estimacion.py        → juicio de expertos, análoga, PERT, puntos de función
   │    7. analisis_ia.py       → dictamen de calidad con Claude
   │    8. artefacto "reportes-calidad" + resumen en la pestaña Actions
   │
   └─ Job "docker" (si "calidad" pasó)
        1. docker build
        2. pytest dentro del contenedor
        3. prueba de humo: GET /estado de la API FastAPI
```

## Estructura

```
├── app_desktop.py, main.py, cerebro.py, voice.py, servidor.py, estado.py, basedatos.py, config.py
├── skills/                 habilidades locales (una por archivo)
├── tests/                  pruebas automatizadas (pytest)
├── metricas/
│   ├── calcular_metricas.py   métricas de producto, proceso y proyecto
│   ├── estimacion.py          4 técnicas de estimación
│   ├── analisis_ia.py         análisis de calidad con Claude
│   └── datos/                 defectos.csv, sprints.csv, estimacion.json
├── .github/workflows/ci.yml   pipeline CI/CD
├── Dockerfile, .dockerignore
└── pipeline_local.bat      el mismo pipeline en Windows
```

## Cómo ejecutarlo

```bash
pip install -r requirements.txt        # para usar el asistente (Windows)
python app_desktop.py

pip install -r requirements-dev.txt    # para pruebas y métricas
pytest --cov
python metricas/calcular_metricas.py --reportes reports
```

En Windows basta con `pipeline_local.bat`. Con Docker:

```bash
docker build -t azmuth .
docker run --rm azmuth pytest -q            # pruebas
docker run -p 8080:8080 azmuth              # API en http://localhost:8080/estado
```

## Defectos conocidos

Las pruebas marcadas `xfail` documentan defectos detectados por las pruebas automatizadas
y aún abiertos (DEF-011, DEF-012, DEF-013 en `metricas/datos/defectos.csv`).
