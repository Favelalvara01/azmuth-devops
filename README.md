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

## Comandos para calcular las métricas en la terminal

Desde la carpeta `jarvis-agent` (en Windows usa `py -3.13 -m` en lugar de `python -m`):

```bash
pip install -r requirements-dev.txt                       # 1. herramientas (una sola vez)
mkdir reports                                              # 2. carpeta de reportes

python -m ruff check . --select E9,F63,F7,F82              # 3. validación estática (gate)
python -m pytest --cov --cov-report=term --cov-report=json:reports/coverage.json --junitxml=reports/pruebas.xml   # 4. pruebas + cobertura
python -m radon cc . -s -a -e "tests/*,metricas/*"         # 5. complejidad ciclomática
python -m radon mi . -s -e "tests/*,metricas/*"            #    índice de mantenibilidad
python metricas/calcular_metricas.py --reportes reports --historial metricas/resultados/historial.csv   # 6. producto, proceso, proyecto
python metricas/estimacion.py --reportes reports           # 7. 4 técnicas de estimación
python metricas/graficas.py --reportes reports             # 8. gráficas → metricas/resultados/graficas/
python metricas/analisis_ia.py --reportes reports          # 9. dictamen con IA (usa ANTHROPIC_API_KEY del .env)
```

O todo de una vez en Windows: `pipeline_local.bat`.

Las gráficas y métricas también se regeneran **solas en cada push**: GitHub Actions las
recalcula y las sube a `metricas/resultados/` (haz `git pull` para verlas en tu compu).

## Pruebas de software (por tipo)

Las pruebas nuevas están en `tests/tipos_de_prueba/` y se ejecutan por tipo con marcadores de pytest
(`pytest -m humo -v`). En Windows, `ejecutar_pruebas.bat` corre cada tipo con una pausa para capturar la pantalla.

| Marcador | Archivo | Qué valida |
|---|---|---|
| `unitaria` | test_unitarias.py | funciones aisladas |
| `componente` | test_componentes.py | módulos completos (skills, chats, monitoreo) |
| `integracion` | test_integracion.py | API → núcleo → skills → SQLite / IA |
| `sistema` | test_sistema.py | servidor real por HTTP, de punta a punta |
| `aceptacion` | test_aceptacion.py | historias de usuario (Dado / Cuando / Entonces) |
| `exploratoria` | test_exploratorias.py | fuzzing con semilla |
| `usabilidad` | test_usabilidad.py | heurísticas de Nielsen y WCAG |
| `funcional` / `no_funcional` | test_funcionales.py / test_no_funcionales.py | caja negra / rendimiento, carga, fiabilidad |
| `humo` / `interfaz` | test_humo.py / test_interfaz.py | arranque / contratos de la API y la interfaz |
| `seguridad` | test_seguridad.py | OWASP Top 10 |
| `api_remota` | tests/api_remota/ | API en la VM de VirtualBox ([hiperconvergencia/](hiperconvergencia/README.md)) |

## Defectos conocidos

Las pruebas marcadas `xfail` documentan defectos detectados por las pruebas automatizadas
y aún abiertos (DEF-011, DEF-012, DEF-013 en `metricas/datos/defectos.csv`).
