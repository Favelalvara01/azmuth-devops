"""
Skill: habitos — registro silencioso de qué tanto usa cada tipo de
comando (tablas "habitos_categorias", "habitos_horas" y "habitos_meta"),
para que Azmuth pueda notar patrones (ej. casi siempre pide música a
las 8pm) y, con el tiempo, sugerir cosas por su cuenta.

No es algo que usted "active" diciendo una frase — main.py llama a
registrar_uso() después de CADA comando que procesa, sin que usted haga
nada. Sí tiene un comando de voz para consultarlo: "mis hábitos".

sugerir_por_hora() la usa main.py (desde el hilo principal, nunca desde
un hilo aparte, para no competir por el micrófono) para, de vez en
cuando, proponer algo por su cuenta ("¿quiere que le ponga música?") si
nota un patrón fuerte para la hora actual. Cuando el usuario responde,
main.py llama a registrar_respuesta_sugerencia(): si la rechaza varias
veces seguidas, esa categoría deja de sugerirse sola por un tiempo -las
sugerencias "aprenden" a no insistir con lo que no le interesa.
"""
from datetime import datetime, timedelta

from basedatos import conectar

_HORAS_ENTRE_SUGERENCIAS = 2
_UMBRAL_SUGERENCIA = 3  # mínimo de veces a esta hora para que valga sugerir
_RECHAZOS_PARA_SILENCIAR = 3
_DIAS_SILENCIADA = 7

# Solo se sugieren en voz alta las categorías con una frase natural aquí.
# Las demás (sistema, ayuda, ia, apagado, etc.) igual se cuentan para las
# estadísticas de "mis hábitos", pero nunca se ofrecen solas.
_FRASES_SUGERENCIA = {
    "multimedia": "¿quiere que le ponga música?",
    "aplicaciones": "¿le abro sus aplicaciones de siempre?",
    "web": "¿busco algo por usted?",
}

# Si el usuario acepta la sugerencia, esto es lo que main.py ejecuta de
# verdad (se procesa como si lo hubiera dicho por voz). Las categorías
# sin una acción única y clara (aplicaciones, web) se quedan sin
# entrada: ahí solo se reconoce el "sí", sin adivinar qué app o qué
# buscar.
ACCION_SUGERIDA = {
    "multimedia": "pon mi playlist",
}

_NOMBRES_LEGIBLES = {
    "multimedia": "Multimedia / música",
    "aplicaciones": "Abrir aplicaciones",
    "pestanas": "Pestañas y ventanas",
    "notas": "Notas",
    "recordatorios": "Recordatorios",
    "memoria": "Memoria a largo plazo",
    "contactos": "Contactos",
    "web": "Búsquedas web",
    "sistema": "Comandos de sistema",
    "tiempo": "Hora / fecha / clima",
    "ayuda": "Ayuda",
    "ia": "Conversación libre (Claude)",
    "apagado": "Apagar el sistema",
}


def _obtener_meta(con, clave):
    fila = con.execute("SELECT valor FROM habitos_meta WHERE clave = ?", (clave,)).fetchone()
    return fila["valor"] if fila else None


def _set_meta(con, clave, valor):
    con.execute(
        "INSERT INTO habitos_meta (clave, valor) VALUES (?, ?) "
        "ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
        (clave, valor),
    )


def registrar_uso(categoria: str):
    """Se llama en silencio después de cada comando procesado. Nunca debe
    tronar el flujo principal de voz si algo sale mal aquí."""
    if not categoria:
        return
    try:
        hora = int(datetime.now().hour)
        with conectar() as con:
            con.execute(
                "INSERT INTO habitos_categorias (categoria, conteo, ultima_vez) VALUES (?, 1, ?) "
                "ON CONFLICT(categoria) DO UPDATE SET conteo = conteo + 1, ultima_vez = excluded.ultima_vez",
                (categoria, datetime.now().isoformat()),
            )
            con.execute(
                "INSERT INTO habitos_horas (categoria, hora, conteo) VALUES (?, ?, 1) "
                "ON CONFLICT(categoria, hora) DO UPDATE SET conteo = conteo + 1",
                (categoria, hora),
            )
    except Exception:
        pass


def sugerir_por_hora():
    """Revisa si, a esta hora, hay un patrón fuerte de algún tipo de
    comando y todavía no se ha sugerido nada recientemente. Regresa
    (texto_a_decir, categoria), o None si no hay nada que sugerir."""
    try:
        ahora = datetime.now()
        with conectar() as con:
            ultima = _obtener_meta(con, "ultima_sugerencia")
            if ultima:
                horas_pasadas = (ahora - datetime.fromisoformat(ultima)).total_seconds() / 3600
                if horas_pasadas < _HORAS_ENTRE_SUGERENCIAS:
                    return None

            filas = con.execute(
                """
                SELECT hc.categoria, hh.conteo, hc.silenciada_hasta
                FROM habitos_horas hh
                JOIN habitos_categorias hc ON hc.categoria = hh.categoria
                WHERE hh.hora = ?
                """,
                (ahora.hour,),
            ).fetchall()

            mejor_categoria, mejor_conteo = None, 0
            for fila in filas:
                categoria = fila["categoria"]
                if categoria not in _FRASES_SUGERENCIA:
                    continue
                silenciada_hasta = fila["silenciada_hasta"]
                if silenciada_hasta and datetime.fromisoformat(silenciada_hasta) > ahora:
                    continue  # la rechazó varias veces seguidas, le damos un descanso
                if fila["conteo"] >= _UMBRAL_SUGERENCIA and fila["conteo"] > mejor_conteo:
                    mejor_categoria, mejor_conteo = categoria, fila["conteo"]

            if not mejor_categoria:
                return None

            _set_meta(con, "ultima_sugerencia", ahora.isoformat())

        return _FRASES_SUGERENCIA[mejor_categoria], mejor_categoria
    except Exception:
        return None


def registrar_respuesta_sugerencia(categoria: str, aceptada: bool):
    """main.py llama a esto justo después de que el usuario responde a
    una sugerencia. Aceptarla reinicia su racha de rechazos; rechazarla
    _RECHAZOS_PARA_SILENCIAR veces seguidas apaga esa categoría por
    _DIAS_SILENCIADA días -así deja de insistir con lo que no le
    interesa, sin que el usuario tenga que configurar nada."""
    try:
        with conectar() as con:
            con.execute(
                "INSERT INTO habitos_categorias (categoria) VALUES (?) ON CONFLICT(categoria) DO NOTHING",
                (categoria,),
            )
            if aceptada:
                con.execute(
                    "UPDATE habitos_categorias SET rachas_rechazo = 0, silenciada_hasta = NULL WHERE categoria = ?",
                    (categoria,),
                )
            else:
                fila = con.execute(
                    "SELECT rachas_rechazo FROM habitos_categorias WHERE categoria = ?", (categoria,)
                ).fetchone()
                nuevas_rachas = (fila["rachas_rechazo"] or 0) + 1
                silenciada_hasta = None
                if nuevas_rachas >= _RECHAZOS_PARA_SILENCIAR:
                    silenciada_hasta = (datetime.now() + timedelta(days=_DIAS_SILENCIADA)).isoformat()
                con.execute(
                    "UPDATE habitos_categorias SET rachas_rechazo = ?, silenciada_hasta = ? WHERE categoria = ?",
                    (nuevas_rachas, silenciada_hasta, categoria),
                )
    except Exception:
        pass


def resumen_para_perfil() -> str:
    """Texto corto con los patrones de uso, para pasárselo a Claude
    cuando genera el perfil de personalidad (ver cerebro.py)."""
    try:
        with conectar() as con:
            categorias = con.execute(
                "SELECT categoria, conteo FROM habitos_categorias ORDER BY conteo DESC LIMIT 6"
            ).fetchall()
            if not categorias:
                return ""
            lineas = []
            for cat in categorias:
                nombre = _NOMBRES_LEGIBLES.get(cat["categoria"], cat["categoria"])
                hora_top = con.execute(
                    "SELECT hora FROM habitos_horas WHERE categoria = ? ORDER BY conteo DESC LIMIT 1",
                    (cat["categoria"],),
                ).fetchone()
                if hora_top:
                    lineas.append(f"- {nombre}: {cat['conteo']} veces en total, más seguido cerca de las {hora_top['hora']}:00")
                else:
                    lineas.append(f"- {nombre}: {cat['conteo']} veces en total")
        return "\n".join(lineas)
    except Exception:
        return ""


def intentar(texto: str):
    tl = texto.lower().strip()
    if tl not in ("mis hábitos", "mis habitos", "cuáles son mis hábitos", "cuales son mis habitos"):
        return None

    with conectar() as con:
        filas = con.execute(
            "SELECT categoria, conteo FROM habitos_categorias ORDER BY conteo DESC LIMIT 5"
        ).fetchall()
    if not filas:
        return "Todavía no tengo suficientes datos sobre sus hábitos."

    lineas = [
        f"{i + 1}. {_NOMBRES_LEGIBLES.get(f['categoria'], f['categoria'])} — {f['conteo']} veces"
        for i, f in enumerate(filas)
    ]
    return "Esto es lo que más usa:\n" + "\n".join(lineas)