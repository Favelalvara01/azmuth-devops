"""
Skill: perfil — resumen de personalidad/estilo del usuario que se
regenera solo cada cierto tiempo, a partir de lo que Azmuth ya sabe
(hechos de memoria.py + patrones de habitos.py). No es un comando de
voz: cerebro.py lo usa como contexto extra en cada conversación, y lo
va actualizando en segundo plano sin que el usuario tenga que pedirlo.
Guardado en la tabla "perfil" (una sola fila, id=1).
"""
from datetime import datetime

from basedatos import conectar

# No regenerar el perfil más seguido que esto — no hace falta, y cada
# regeneración es una llamada extra a Claude.
_HORAS_ENTRE_ACTUALIZACIONES = 24


def obtener_perfil_actual() -> str:
    """El texto del perfil guardado, o "" si todavía no se ha generado
    ninguno (ej. recién instalado, sin historial suficiente)."""
    try:
        with conectar() as con:
            fila = con.execute("SELECT texto FROM perfil WHERE id = 1").fetchone()
        return (fila["texto"] if fila else "") or ""
    except Exception:
        return ""


def toca_actualizar() -> bool:
    """True si ya pasaron _HORAS_ENTRE_ACTUALIZACIONES desde la última
    vez que se generó el perfil (o nunca se ha generado uno)."""
    try:
        with conectar() as con:
            fila = con.execute("SELECT ultima_actualizacion FROM perfil WHERE id = 1").fetchone()
        if not fila or not fila["ultima_actualizacion"]:
            return True
        horas = (datetime.now() - datetime.fromisoformat(fila["ultima_actualizacion"])).total_seconds() / 3600
        return horas >= _HORAS_ENTRE_ACTUALIZACIONES
    except Exception:
        return False


def guardar_perfil(texto: str):
    with conectar() as con:
        con.execute(
            "INSERT INTO perfil (id, texto, ultima_actualizacion) VALUES (1, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET texto = excluded.texto, ultima_actualizacion = excluded.ultima_actualizacion",
            ((texto or "").strip(), datetime.now().isoformat()),
        )
