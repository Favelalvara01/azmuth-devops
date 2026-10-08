"""
Skill: apps_instaladas — abre (y cierra) CUALQUIER aplicación instalada,
aunque no esté en la lista fija de skills/aplicaciones.py.

Cómo "aprende" sola, sin que nadie tenga que programar una skill nueva:

  1. ESCANEO: lee todas las apps de Windows con PowerShell (Get-StartApps:
     menú Inicio + Microsoft Store) y los accesos directos del escritorio.
     El resultado se guarda en la tabla "apps_indice" y se refresca cada 24 h
     (o diciendo "actualiza tus aplicaciones").
  2. BÚSQUEDA: compara lo que dijiste con los nombres (sin acentos, por
     parecido). Si hay un ganador claro, la abre.
  3. IA: si hay varias parecidas, le pregunta a Claude cuál quisiste decir.
  4. MEMORIA: lo que encontró queda en "apps_aprendidas" (alias -> app),
     así la siguiente vez la abre directo. También se le puede enseñar:
     "cuando diga el juego abre Roblox".

Va al FINAL de la lista de skills: solo actúa si ninguna otra entendió.
"""
import difflib
import json
import os
import re
import subprocess
import unicodedata
from datetime import datetime, timedelta

from basedatos import conectar

_HORAS_ENTRE_ESCANEOS = 24
_UMBRAL_SEGURO = 0.82     # parecido mínimo para abrir sin preguntar
_UMBRAL_DUDA = 0.55       # entre este y el seguro, decide la IA
_RELLENO = {"el", "la", "los", "las", "un", "una", "app", "aplicacion", "programa", "juego", "de", "mi", "por", "favor"}

_ABRIR = re.compile(r"^(?:abre|abreme|abrir|inicia|iniciar|ejecuta|ejecutar|lanza|lanzar|arranca)\s+(.+)$")
_CERRAR = re.compile(r"^(?:cierra|cierrame|cerrar|mata|termina)\s+(.+)$")
_ENSENAR = re.compile(r"^(?:cuando\s+(?:diga|te\s+diga)|aprende\s+que)\s+(.+?)\s+(?:abre|es|significa)\s+(.+)$")
_REESCANEAR = re.compile(r"^(?:actualiza|escanea|busca)\s+(?:tus|mis|las)\s+(?:aplicaciones|apps|programas)$")
_LISTAR = re.compile(r"^(?:que|cuales)\s+(?:aplicaciones|apps)\s+(?:aprendiste|conoces|tengo)")


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFD", (texto or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^\w\s]", " ", t)
    palabras = [p for p in t.split() if p not in _RELLENO]
    return " ".join(palabras)


# ------------------------------------------------------------------ índice
_PS_ESCANEO = r"""
$ErrorActionPreference = 'SilentlyContinue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$apps = @(Get-StartApps | ForEach-Object { @{ nombre = $_.Name; tipo = 'appid'; destino = $_.AppID } })
$esc = @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('CommonDesktopDirectory'))
foreach ($d in $esc) {
  Get-ChildItem -Path $d -Include *.lnk,*.url -Recurse -Depth 1 | ForEach-Object {
    $apps += @{ nombre = $_.BaseName; tipo = 'ruta'; destino = $_.FullName }
  }
}
$apps | ConvertTo-Json -Compress
"""


def escanear_windows():
    """Lista [{nombre, tipo, destino}] de las apps instaladas. En Linux/CI regresa []."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", _PS_ESCANEO],
                           capture_output=True, text=True, timeout=40, encoding="utf-8", errors="ignore")
        datos = json.loads(r.stdout or "[]")
        return datos if isinstance(datos, list) else [datos]
    except Exception:
        return []


def guardar_indice(apps):
    with conectar() as con:
        con.execute("DELETE FROM apps_indice")
        con.executemany(
            "INSERT OR IGNORE INTO apps_indice (nombre, normal, tipo, destino) VALUES (?, ?, ?, ?)",
            [(a["nombre"], normalizar(a["nombre"]), a["tipo"], a["destino"]) for a in apps if a.get("nombre") and a.get("destino")],
        )
        con.execute("INSERT INTO ajustes (clave, valor) VALUES ('apps_escaneo', ?) "
                    "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor", (datetime.now().isoformat(),))
    return len(apps)


def reescanear():
    return guardar_indice(escanear_windows())


def _indice(forzar=False):
    with conectar() as con:
        fila = con.execute("SELECT valor FROM ajustes WHERE clave = 'apps_escaneo'").fetchone()
        viejo = not fila or datetime.now() - datetime.fromisoformat(fila["valor"]) > timedelta(hours=_HORAS_ENTRE_ESCANEOS)
    if forzar or viejo:
        reescanear()
    with conectar() as con:
        return [dict(f) for f in con.execute("SELECT nombre, normal, tipo, destino FROM apps_indice").fetchall()]


# ---------------------------------------------------------------- búsqueda
def puntuar(buscado: str, nombre_normal: str) -> float:
    if not buscado or not nombre_normal:
        return 0.0
    if buscado == nombre_normal:
        return 1.0
    palabras = nombre_normal.split()
    if buscado in palabras or nombre_normal.startswith(buscado + " "):
        return 0.93
    if re.search(rf"\b{re.escape(buscado)}\b", nombre_normal):
        return 0.88
    ratio = difflib.SequenceMatcher(None, buscado, nombre_normal).ratio()
    mejor_palabra = max((difflib.SequenceMatcher(None, buscado, p).ratio() for p in palabras), default=0)
    return max(ratio, mejor_palabra * 0.9)


def candidatos(buscado: str, indice, n=8):
    b = normalizar(buscado)
    puntuados = sorted(((puntuar(b, a["normal"]), a) for a in indice), key=lambda x: -x[0])
    vistos, salida = set(), []
    for p, a in puntuados:
        if a["nombre"].lower() in vistos:
            continue
        vistos.add(a["nombre"].lower())
        salida.append((round(p, 3), a))
        if len(salida) == n:
            break
    return salida


def elegir_con_ia(frase: str, opciones):
    """Le pide a Claude que elija cuál de las apps instaladas quiso decir el usuario.
    Regresa (app | None, consultada). consultada=False si no hay IA disponible."""
    try:
        import cerebro
        if not cerebro.proveedor():
            return None, False
        lista = "\n".join(f"- {a['nombre']}" for _, a in opciones)
        respuesta = cerebro.completar(
            "Eliges aplicaciones. Responde SOLO con el nombre exacto de una opción de la lista, o NINGUNA.",
            [{"role": "user", "content": f'El usuario dijo: "{frase}". ¿Cuál de estas apps quiso abrir?\n{lista}'}], 40)
        elegido = respuesta.strip().strip('"').strip("- ")
        return next((a for _, a in opciones if a["nombre"].lower() == elegido.lower()), None), True
    except Exception:
        return None, False


# ---------------------------------------------------------------- memoria
def aprender(alias: str, app: dict):
    with conectar() as con:
        con.execute(
            "INSERT INTO apps_aprendidas (alias, nombre, tipo, destino, usos, fecha) VALUES (?, ?, ?, ?, 1, ?) "
            "ON CONFLICT(alias) DO UPDATE SET nombre = excluded.nombre, tipo = excluded.tipo, "
            "destino = excluded.destino, usos = usos + 1",
            (normalizar(alias), app["nombre"], app["tipo"], app["destino"], datetime.now().isoformat()),
        )


def recordada(alias: str):
    with conectar() as con:
        fila = con.execute("SELECT nombre, tipo, destino FROM apps_aprendidas WHERE alias = ?", (normalizar(alias),)).fetchone()
    return dict(fila) if fila else None


def resolver(frase: str):
    """Regresa (app, como) o (None, sugerencias). como = memoria | indice | ia."""
    app = recordada(frase)
    if app:
        return app, "memoria"
    for forzar in (False, True):  # si no aparece, re-escanea una vez (app recién instalada)
        indice = _indice(forzar=forzar)
        opciones = candidatos(frase, indice)
        if opciones and opciones[0][0] >= _UMBRAL_SEGURO and (len(opciones) == 1 or opciones[0][0] - opciones[1][0] >= 0.05):
            return opciones[0][1], "indice"
        dudosas = [o for o in opciones if o[0] >= _UMBRAL_DUDA]
        if dudosas:
            elegida, consultada = elegir_con_ia(frase, dudosas)
            if elegida:
                return elegida, "ia"
            if consultada:
                return None, []  # la IA dice que no es ninguna app: que lo conteste Claude
            return None, [a["nombre"] for _, a in dudosas[:3]]
    return None, []


# ----------------------------------------------------------------- acciones
def lanzar(app: dict) -> bool:
    try:
        if app["tipo"] == "appid":
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app['destino']}"])
        else:
            os.startfile(app["destino"])
        return True
    except Exception:
        return False


def cerrar(app: dict) -> bool:
    nombre = normalizar(app["nombre"]).split(" ")[0]
    ps = (f"Get-Process | Where-Object {{ $_.MainWindowTitle -like '*{app['nombre']}*' -or $_.ProcessName -like '*{nombre}*' }}"
          " | Stop-Process -ErrorAction SilentlyContinue")
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, timeout=15)
        return True
    except Exception:
        return False


def intentar(texto: str):
    t = normalizar_frase(texto)
    if not t:
        return None

    if _REESCANEAR.match(t):
        n = reescanear()
        return f"Listo, encontré {n} aplicaciones y accesos directos en su computadora."

    if _LISTAR.match(t):
        with conectar() as con:
            filas = con.execute("SELECT alias, nombre FROM apps_aprendidas ORDER BY usos DESC LIMIT 10").fetchall()
        if not filas:
            return "Todavía no he aprendido ninguna aplicación nueva. Pídame abrir cualquiera y la busco."
        return "Aplicaciones que ya aprendí:\n" + "\n".join(f"- \"{f['alias']}\" → {f['nombre']}" for f in filas)

    m = _ENSENAR.match(t)
    if m:
        alias, objetivo = m.group(1), m.group(2)
        app, info = resolver(objetivo)
        if not app:
            return f'No encontré "{objetivo}" entre sus aplicaciones.'
        aprender(alias, app)
        return f'Entendido. Cuando diga "{alias}" abriré {app["nombre"]}.'

    m = _ABRIR.match(t)
    if m:
        pedido = m.group(1).strip()
        app, info = resolver(pedido)
        if not app:
            if info:
                return f'No estoy seguro de cuál quiere abrir. ¿Quiso decir {", ".join(info)}? Dígame "abre" con el nombre exacto.'
            return None  # no parece una app: que lo conteste Claude
        if not lanzar(app):
            return f"Encontré {app['nombre']}, pero Windows no me dejó abrirla."
        aprender(pedido, app)
        nueva = info != "memoria"
        return f"Abriendo {app['nombre']}." + (" La agregué a las aplicaciones que conozco." if nueva else "")

    m = _CERRAR.match(t)
    if m:
        app, info = resolver(m.group(1).strip())
        if not app:
            return None
        cerrar(app)
        return f"Cerrando {app['nombre']}."
    return None


def normalizar_frase(texto: str) -> str:
    """Igual que normalizar() pero sin quitar palabras: conserva el verbo."""
    t = unicodedata.normalize("NFD", (texto or "").lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


def precargar():
    """Se llama al arrancar Azmuth (en segundo plano) para tener el índice listo."""
    try:
        _indice()
    except Exception:
        pass
