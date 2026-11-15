"""
conftest.py — configuración compartida de las pruebas de Azmuth.

Azmuth es un asistente de escritorio para Windows (micrófono, teclado
virtual, ventanas). En el pipeline de CI (GitHub Actions, Linux, sin
pantalla) esas librerías no existen, así que aquí se SIMULAN (mocks):
así se valida la lógica de cada skill sin abrir programas reales.

Además, cada prueba usa su propia base de datos SQLite temporal: nunca
se tocan las notas, recordatorios ni la memoria reales del usuario.
"""
import os
import sys
import types
from unittest import mock

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

# --- Librerías exclusivas de Windows / hardware: se reemplazan por dobles ---
class _ModuloSimulado(types.ModuleType):
    """Módulo falso: cada atributo que se pide (pyautogui.press, sd.InputStream…)
    se crea como MagicMock y se GUARDA en el __dict__ del módulo.

    Antes era un MagicMock directo, pero desde pytest 9.2 monkeypatch.setattr()
    solo restaura lo que está en __dict__: al terminar la prueba BORRABA
    pyautogui.press y las siguientes fallaban con "has no attribute 'press'"."""

    def __getattr__(self, nombre):
        if nombre.startswith("__"):
            raise AttributeError(nombre)
        valor = mock.MagicMock(name=f"{self.__name__}.{nombre}")
        setattr(self, nombre, valor)
        return valor


for nombre in ("pyautogui", "pygetwindow", "speech_recognition", "sounddevice", "webview", "pyttsx3"):
    if nombre not in sys.modules:
        sys.modules[nombre] = _ModuloSimulado(nombre)

# Sin claves reales durante las pruebas (nunca se llama a la API de verdad)
os.environ.setdefault("ANTHROPIC_API_KEY", "")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("GROQ_API_KEY", "")
os.environ.setdefault("DEEPSEEK_API_KEY", "")
os.environ.setdefault("ELEVENLABS_API_KEY", "")

if "anthropic" not in sys.modules:
    try:
        import anthropic  # noqa: F401
    except ImportError:  # pragma: no cover
        sys.modules["anthropic"] = types.SimpleNamespace(Anthropic=mock.MagicMock())


@pytest.fixture(autouse=True)
def bd_temporal(tmp_path, monkeypatch):
    """Cada prueba arranca con una base de datos SQLite vacía y aislada."""
    import basedatos
    monkeypatch.setattr(basedatos, "_RUTA_DB", str(tmp_path / "azmuth_test.db"))
    yield tmp_path / "azmuth_test.db"


@pytest.fixture(autouse=True)
def log_temporal(tmp_path, monkeypatch):
    """El registro de errores de las pruebas va a una carpeta temporal."""
    import monitoreo
    monkeypatch.setattr(monitoreo, "_RUTA_LOG", str(tmp_path / "errores.log"))
    monkeypatch.setattr(monitoreo, "_logger", None)
    yield tmp_path / "errores.log"


@pytest.fixture(autouse=True)
def sin_efectos_externos(monkeypatch):
    """Evita que una prueba abra el navegador, programas o comandos reales."""
    import webbrowser
    import subprocess
    abiertos = []
    monkeypatch.setattr(webbrowser, "open", lambda url, *a, **k: abiertos.append(url) or True)
    monkeypatch.setattr(subprocess, "run", mock.MagicMock(name="subprocess.run"))
    if hasattr(os, "startfile"):
        monkeypatch.setattr(os, "startfile", mock.MagicMock(side_effect=OSError("bloqueado en pruebas")))
    yield abiertos


@pytest.fixture(autouse=True)
def tematica_normal(monkeypatch):
    """Las pruebas no dependen de la fecha real (en octubre sería Halloween) ni hacen ruido."""
    import datetime
    import tematicas
    monkeypatch.setattr(tematicas, "_preferencia", None)
    monkeypatch.setattr(tematicas, "_hoy", lambda: datetime.date(2026, 6, 15))
    monkeypatch.setattr(tematicas, "_reproducir", mock.MagicMock(name="winsound"))
    yield


@pytest.fixture(autouse=True)
def sin_confirmaciones_pendientes():
    """Ninguna pregunta "¿Lo envío?" pasa de una prueba a otra."""
    import confirmaciones
    confirmaciones.cancelar()
    yield
    confirmaciones.cancelar()


# ---------------------------------------------------------------------------
#  Explicación en pantalla de cada tipo de prueba (para presentarlas en clase)
#  py -3.13 -m pytest -m humo -v   ->  al inicio dice qué es y para qué sirve,
#                                      y al final la conclusión del resultado.
# ---------------------------------------------------------------------------
EXPLICACIONES = {
    "humo": ("PRUEBAS DE HUMO (smoke testing)", [
        "Qué son: pocas verificaciones, muy rápidas, de que lo esencial 'enciende sin echar humo'.",
        "Para qué sirven: son lo primero que se corre después de cada cambio; si fallan, la versión",
        "se rechaza y ya no tiene caso ejecutar las demás pruebas.",
        "En Azmuth revisan: que importen los 8 módulos principales, que respondan /estado y /salud,",
        "que carguen la interfaz y el reloj, que SQLite cree sus tablas y que estén las 17 skills.",
    ], "lo esencial de Azmuth arranca; la versión puede pasar al resto de las pruebas."),
    "unitaria": ("PRUEBAS UNITARIAS", [
        "Qué son: prueban UNA sola función, aislada del resto del programa (patrón AAA:",
        "preparar, actuar y comprobar).",
        "Para qué sirven: si una falla, señala exactamente qué función está mal.",
        "En Azmuth revisan: variantes de texto sin acentos, títulos de chat de 48 caracteres, claves",
        "del .env, hora de recordatorios, días de la semana, fecha en español (DEF-021),",
        "escape de comodines SQL (DEF-019) y el orden de las IA.",
    ], "cada función probada devuelve exactamente lo esperado."),
    "componente": ("PRUEBAS DE COMPONENTES", [
        "Qué son: prueban un MÓDULO completo (no una sola función) por su interfaz pública,",
        "pero aislado del resto, con su propia base de datos temporal.",
        "Para qué sirven: confirman que cada pieza cumple su responsabilidad antes de unirla con otras.",
        "En Azmuth revisan: la skill de notas, los recordatorios, el gestor de chats, el monitoreo",
        "de errores y el catálogo del control remoto.",
    ], "cada componente funciona correctamente por sí solo."),
    "integracion": ("PRUEBAS DE INTEGRACIÓN", [
        "Qué son: prueban que VARIOS módulos funcionan juntos y que los datos pasan bien de uno a otro.",
        "Estrategia ascendente: skills + base de datos, luego núcleo + chats + IA, y al final la API.",
        "Para qué sirven: detectan errores en las 'uniones' que las pruebas unitarias no ven.",
        "En Azmuth revisan: API -> núcleo -> skills -> SQLite, la memoria de la IA, los hábitos,",
        "el respaldo automático entre IAs y que una skill que falla no tumbe el chat (DEF-022).",
    ], "los módulos se comunican correctamente entre sí."),
    "sistema": ("PRUEBAS DE SISTEMA", [
        "Qué son: prueban Azmuth COMPLETO como caja negra, de punta a punta (end-to-end).",
        "Se levanta el servidor real (uvicorn) y se le habla por HTTP, como lo haría la interfaz.",
        "Para qué sirven: confirman que el producto entero funciona, no solo sus partes.",
        "En Azmuth revisan: modo escritorio completo (chat, skill, IA, renombrar, borrar), cambio",
        "de idioma reflejado en todo el sistema y el control remoto desde el reloj.",
    ], "el sistema completo responde correctamente de punta a punta."),
    "aceptacion": ("PRUEBAS DE ACEPTACIÓN", [
        "Qué son: comprueban que Azmuth cumple lo que pidió el USUARIO, a partir de sus historias",
        "de usuario, con criterios DADO (contexto) / CUANDO (acción) / ENTONCES (resultado).",
        "Para qué sirven: si todas pasan, la historia de usuario se considera terminada y aceptada.",
        "En Azmuth revisan: HU-02 notas y recordatorios, HU-08 chat escrito, HU-09 texto sin",
        "acentos, HU-10 control remoto protegido y HU-11 Azmuth en inglés.",
    ], "las historias de usuario cumplen sus criterios de aceptación."),
    "exploratoria": ("PRUEBAS EXPLORATORIAS", [
        "Qué son: el tester aprende, diseña y ejecuta al mismo tiempo siguiendo una 'carta' (charter).",
        "Aquí se automatiza con FUZZING: cientos de entradas aleatorias (emojis, SQL, <script>,",
        "textos larguísimos); la semilla 2026 permite repetir cualquier hallazgo.",
        "Para qué sirven: descubren errores que nadie pensó en probar (así se encontró DEF-021).",
        "En Azmuth revisan: 500 frases al enrutador, datos raros a 5 endpoints y la fecha en español.",
    ], "ninguna entrada aleatoria hizo tronar a Azmuth ni produjo un error 500."),
    "usabilidad": ("PRUEBAS DE USABILIDAD", [
        "Qué son: miden qué tan fácil y agradable es usar Azmuth (ISO 9241-11).",
        "Se revisan reglas objetivas de las heurísticas de Nielsen y de accesibilidad WCAG 2.1;",
        "la satisfacción se mide aparte con usuarios y el cuestionario SUS (resultado: 90/100).",
        "Para qué sirven: aseguran que el usuario entienda la interfaz y no se frustre.",
        "En Azmuth revisan: idioma y títulos, botones con nombre, botones táctiles de 44 px,",
        "Enter para enviar, frases sin acentos, respuestas en menos de 1 s y errores en español.",
    ], "la interfaz y las respuestas cumplen las reglas de usabilidad y accesibilidad."),
    "funcional": ("TÉCNICA: PRUEBAS FUNCIONALES (caja negra)", [
        "Qué son: validan QUÉ hace el sistema contra sus requisitos: entrada -> salida esperada,",
        "sin mirar el código.",
        "Técnicas de diseño: partición de equivalencia (clases válidas e inválidas), valores límite",
        "(47, 48 y 49 caracteres), tabla de decisión (reglas del token) y casos de uso.",
        "Para qué sirven: con pocos casos bien elegidos se cubren muchas situaciones.",
    ], "cada requisito funcional produce la salida esperada."),
    "no_funcional": ("TÉCNICA: PRUEBAS NO FUNCIONALES", [
        "Qué son: no revisan QUÉ hace Azmuth sino CÓMO lo hace: atributos de calidad de ISO/IEC 25010.",
        "Para qué sirven: miden con números el rendimiento, la carga, la fiabilidad y la portabilidad.",
        "En Azmuth miden: latencia de /estado (p95 < 50 ms), 20 usuarios simultáneos sin errores,",
        "recuperación después de un error, persistencia de datos, que la API funcione sin librerías",
        "de Windows y que todas las skills cumplan el mismo contrato.",
    ], "Azmuth cumple los umbrales de rendimiento, carga, fiabilidad y portabilidad."),
    "interfaz": ("TÉCNICA: PRUEBAS DE INTERFAZ", [
        "Qué son: revisan los puntos donde dos partes se comunican.",
        "API: el CONTRATO de cada endpoint (código HTTP, tipo de contenido y forma del JSON).",
        "Interfaz gráfica: que cada botón y cada fetch() apunten a acciones y rutas que existen.",
        "Para qué sirven: si la API deja de mandar un campo que la ventana necesita, lo detectan.",
    ], "la API respeta su contrato y la interfaz está conectada a acciones reales."),
    "seguridad": ("PRUEBAS DE SEGURIDAD", [
        "Qué son: buscan debilidades que un atacante podría aprovechar (guía: OWASP Top 10).",
        "Para qué sirven: evitan accesos sin permiso, robo de datos y ejecución de comandos.",
        "En Azmuth revisan: token del control remoto (incluye la red local, DEF-020), inyección SQL,",
        "comodines LIKE (DEF-019), inyección de comandos, path traversal, cookies seguras,",
        "errores sin traza, claves que nunca salen en las respuestas y escape de HTML (XSS).",
        "Se complementan con bandit (código) y pip-audit (dependencias).",
    ], "no se encontraron vulnerabilidades en los ataques probados."),
    "api_remota": ("PRUEBAS DE API Y SERVICIOS EN LA HIPERCONVERGENCIA", [
        "Qué son: pruebas por la RED contra la API de Azmuth que corre en un contenedor dentro",
        "de la VM Ubuntu Server (nodo hiperconvergente), a través del hipervisor VirtualBox.",
        "Camino: Windows 127.0.0.1:8082 -> VirtualBox NAT -> VM :8080 -> contenedor azmuth-api.",
        "Para qué sirven: comprueban la comunicación hipervisor <-> hiperconvergencia, el token,",
        "el contrato, el almacenamiento del nodo y la latencia de la red virtual.",
    ], "la API del nodo responde correctamente a través del hipervisor."),
}


def _tipo_de_prueba(config):
    marca = (getattr(config.option, "markexpr", "") or "").strip()
    if marca in EXPLICACIONES:
        return marca
    if any("api_remota" in str(a) for a in config.args):
        return "api_remota"
    return None


def pytest_report_header(config):
    tipo = _tipo_de_prueba(config)
    if not tipo:
        return None
    titulo, lineas, _ = EXPLICACIONES[tipo]
    borde = "=" * 96
    return ["", borde, f"  {titulo}", borde, *[f"  {linea}" for linea in lineas], borde]


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Debajo de la tabla de cobertura: qué significa y si el porcentaje está bien (metricas/explicaciones.py).
    Si se ejecutó un solo tipo de prueba (-m humo, -m seguridad...), también escribe su conclusión."""
    import json
    tipo = _tipo_de_prueba(config)
    if tipo:
        stats = terminalreporter.stats
        aprobadas = len(stats.get("passed", []))
        fallidas = len(stats.get("failed", [])) + len(stats.get("error", []))
        titulo, _, si_pasa = EXPLICACIONES[tipo]
        terminalreporter.write_sep("=", "CONCLUSIÓN")
        omitidas = len(stats.get("skipped", []))
        if not aprobadas and not fallidas and omitidas:
            terminalreporter.write_line(f"  Se omitieron {omitidas} casos: falta AZMUTH_URL y AZMUTH_TOKEN (¿está encendida la VM?).",
                                        yellow=True, bold=True)
        elif fallidas == 0 and aprobadas:
            terminalreporter.write_line(f"  {aprobadas} de {aprobadas} casos aprobados: {si_pasa}", green=True, bold=True)
        else:
            aviso = f"  {fallidas} caso(s) fallaron de {aprobadas + fallidas}: hay que revisar el defecto antes de entregar."
            terminalreporter.write_line(aviso, red=True, bold=True)
    if not getattr(config.option, "cov_source", None):
        return
    reportes = getattr(config.option, "cov_report", None) or {}
    ruta = reportes.get("json") if isinstance(reportes, dict) else None
    if not ruta:  # solo si se pidió el reporte JSON (--cov-report=json:reports/coverage.json)
        return
    ruta = ruta if os.path.isabs(ruta) else os.path.join(str(config.invocation_params.dir), ruta)
    if not os.path.exists(ruta):
        return
    try:
        from metricas.explicaciones import interpretar_cobertura
        stats = terminalreporter.stats
        aprobadas = len(stats.get("passed", []))
        total = aprobadas + len(stats.get("failed", [])) + len(stats.get("error", []))
        lineas = interpretar_cobertura(json.load(open(ruta, encoding="utf-8")), aprobadas, total,
                                       len(stats.get("warnings", [])))
    except Exception:
        return
    for linea in lineas:
        terminalreporter.write_line(linea, bold=linea.startswith("¿"))
