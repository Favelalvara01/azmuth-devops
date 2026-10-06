"""
migrar_json_a_sqlite.py — corre esto UNA SOLA VEZ para pasar tus datos
de los .json viejos (notas, recordatorios, memoria, hábitos, contactos,
perfil) a la nueva base de datos datos/azmuth.db.

Uso: abre una terminal en la carpeta jarvis-agent y corre:
    python migrar_json_a_sqlite.py

Es seguro correrlo más de una vez -si una tabla ya tiene datos, no
la vuelve a migrar (para no duplicar). Los .json originales NO se
borran ni se tocan, se quedan ahí por si acaso.
"""
import json
import os
from datetime import datetime

from basedatos import conectar

_CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")


def _leer_json(nombre):
    ruta = os.path.join(_CARPETA_DATOS, nombre)
    if not os.path.exists(ruta):
        return None
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def migrar_notas(con):
    datos = _leer_json("notas.json")
    if not datos:
        print("notas.json: nada que migrar.")
        return
    ya = con.execute("SELECT COUNT(*) AS n FROM notas").fetchone()["n"]
    if ya:
        print(f"notas: ya hay {ya} filas en la base, no vuelvo a migrar (evito duplicar).")
        return
    for n in datos:
        con.execute(
            "INSERT INTO notas (texto, fecha) VALUES (?, ?)",
            (n.get("texto", ""), n.get("fecha") or datetime.now().isoformat()),
        )
    print(f"notas: migradas {len(datos)}.")


def migrar_recordatorios(con):
    datos = _leer_json("recordatorios.json")
    if not datos:
        print("recordatorios.json: nada que migrar.")
        return
    ya = con.execute("SELECT COUNT(*) AS n FROM recordatorios").fetchone()["n"]
    if ya:
        print(f"recordatorios: ya hay {ya} filas, no vuelvo a migrar.")
        return
    for r in datos:
        con.execute(
            "INSERT INTO recordatorios "
            "(texto, recurrente, hora_objetivo, notificado, hora, dias, ultima_notificacion, fecha_creado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                r.get("texto", ""),
                1 if r.get("recurrente") else 0,
                r.get("hora_objetivo"),
                1 if r.get("notificado") else 0,
                r.get("hora"),
                json.dumps(r.get("dias")) if r.get("dias") is not None else None,
                r.get("ultima_notificacion"),
                r.get("fecha_creado") or r.get("fecha") or datetime.now().isoformat(),
            ),
        )
    print(f"recordatorios: migrados {len(datos)}.")


def migrar_memoria(con):
    datos = _leer_json("memoria.json")
    if not datos:
        print("memoria.json: nada que migrar.")
        return
    ya = con.execute("SELECT COUNT(*) AS n FROM memoria").fetchone()["n"]
    if ya:
        print(f"memoria: ya hay {ya} filas, no vuelvo a migrar.")
        return
    for h in datos:
        con.execute(
            "INSERT INTO memoria (texto, fecha, origen) VALUES (?, ?, ?)",
            (h.get("texto", ""), h.get("fecha") or datetime.now().isoformat(), h.get("origen", "manual")),
        )
    print(f"memoria: migrados {len(datos)}.")


def migrar_contactos(con):
    datos = _leer_json("contactos.json")
    if not datos:
        print("contactos.json: nada que migrar.")
        return
    ya = con.execute("SELECT COUNT(*) AS n FROM contactos").fetchone()["n"]
    if ya:
        print(f"contactos: ya hay {ya} filas, no vuelvo a migrar.")
        return
    for nombre, numero in datos.items():
        con.execute("INSERT OR REPLACE INTO contactos (nombre, numero) VALUES (?, ?)", (nombre, numero))
    print(f"contactos: migrados {len(datos)}.")


def migrar_habitos(con):
    datos = _leer_json("habitos.json")
    if not datos:
        print("habitos.json: nada que migrar.")
        return
    ya = con.execute("SELECT COUNT(*) AS n FROM habitos_categorias").fetchone()["n"]
    if ya:
        print(f"hábitos: ya hay {ya} categorías, no vuelvo a migrar.")
        return
    for categoria, info in datos.get("categorias", {}).items():
        con.execute(
            "INSERT INTO habitos_categorias (categoria, conteo, ultima_vez, rachas_rechazo, silenciada_hasta) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                categoria,
                info.get("conteo", 0),
                info.get("ultima_vez"),
                info.get("rachas_rechazo", 0),
                info.get("silenciada_hasta"),
            ),
        )
        for hora, conteo in info.get("horas", {}).items():
            con.execute(
                "INSERT INTO habitos_horas (categoria, hora, conteo) VALUES (?, ?, ?)",
                (categoria, int(hora), conteo),
            )
    if datos.get("ultima_sugerencia"):
        con.execute(
            "INSERT OR REPLACE INTO habitos_meta (clave, valor) VALUES ('ultima_sugerencia', ?)",
            (datos["ultima_sugerencia"],),
        )
    print(f"hábitos: migradas {len(datos.get('categorias', {}))} categorías.")


def migrar_perfil(con):
    datos = _leer_json("perfil.json")
    if not datos or not datos.get("texto"):
        print("perfil.json: nada que migrar.")
        return
    ya = con.execute("SELECT texto FROM perfil WHERE id = 1").fetchone()
    if ya and ya["texto"]:
        print("perfil: ya hay uno guardado, no vuelvo a migrar.")
        return
    con.execute(
        "INSERT OR REPLACE INTO perfil (id, texto, ultima_actualizacion) VALUES (1, ?, ?)",
        (datos["texto"], datos.get("ultima_actualizacion")),
    )
    print("perfil: migrado.")


if __name__ == "__main__":
    con = conectar()
    migrar_notas(con)
    migrar_recordatorios(con)
    migrar_memoria(con)
    migrar_contactos(con)
    migrar_habitos(con)
    migrar_perfil(con)
    con.commit()
    con.close()
    print("\nListo. Tus datos ya están en datos/azmuth.db")