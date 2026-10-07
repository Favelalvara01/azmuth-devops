"""
basedatos.py — conexión SQLite compartida por las skills que antes
guardaban su información en archivos .json sueltos (notas,
recordatorios, memoria, hábitos, contactos, perfil).

Todo vive en un solo archivo: datos/azmuth.db. Cada función abre su
propia conexión corta con conectar() y la cierra al terminar (con
"with conectar() as con: ...") — sqlite3 lo permite sin problema desde
varios hilos, mientras cada hilo abra la suya en vez de compartir una
conexión larga entre hilos.
"""
import sqlite3
import os

_RUTA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "azmuth.db")


def conectar():
    """Regresa una conexión nueva, con las tablas ya creadas si hacía
    falta (CREATE TABLE IF NOT EXISTS, así que nunca truena si ya
    existen). con.row_factory = sqlite3.Row deja leer las columnas por
    nombre (fila["texto"]) en vez de por índice."""
    os.makedirs(os.path.dirname(_RUTA_DB), exist_ok=True)
    con = sqlite3.connect(_RUTA_DB)
    con.row_factory = sqlite3.Row
    _crear_tablas(con)
    return con


def _crear_tablas(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto TEXT NOT NULL,
        fecha TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS recordatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto TEXT NOT NULL,
        recurrente INTEGER NOT NULL DEFAULT 0,
        hora_objetivo TEXT,
        notificado INTEGER NOT NULL DEFAULT 0,
        hora TEXT,
        dias TEXT,
        ultima_notificacion TEXT,
        fecha_creado TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS memoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        texto TEXT NOT NULL,
        fecha TEXT NOT NULL,
        origen TEXT NOT NULL DEFAULT 'manual'
    );

    CREATE TABLE IF NOT EXISTS contactos (
        nombre TEXT PRIMARY KEY,
        numero TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS habitos_categorias (
        categoria TEXT PRIMARY KEY,
        conteo INTEGER NOT NULL DEFAULT 0,
        ultima_vez TEXT,
        rachas_rechazo INTEGER NOT NULL DEFAULT 0,
        silenciada_hasta TEXT
    );

    CREATE TABLE IF NOT EXISTS habitos_horas (
        categoria TEXT NOT NULL,
        hora INTEGER NOT NULL,
        conteo INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (categoria, hora)
    );

    CREATE TABLE IF NOT EXISTS habitos_meta (
        clave TEXT PRIMARY KEY,
        valor TEXT
    );

    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        creado TEXT NOT NULL,
        actualizado TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS mensajes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        rol TEXT NOT NULL CHECK (rol IN ('user', 'assistant')),
        texto TEXT NOT NULL,
        origen TEXT NOT NULL DEFAULT 'texto',
        fecha TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ajustes (
        clave TEXT PRIMARY KEY,
        valor TEXT
    );

    CREATE TABLE IF NOT EXISTS perfil (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        texto TEXT,
        ultima_actualizacion TEXT
    );
    """)
    con.commit()