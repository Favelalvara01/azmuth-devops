import json
from datetime import datetime, timedelta

from basedatos import conectar
from skills import recordatorios as r


def test_recordatorio_sin_hora():
    assert r.intentar("recuérdame comprar pan") == 'Recordatorio anotado: "comprar pan".'
    assert "1. comprar pan" in r.intentar("mis recordatorios")


def test_recordatorio_con_hora_pm():
    resp = r.intentar("recuérdame hablar con Jesús a las 5 pm")
    assert "hablar con Jesús" in resp and "17:00" in resp


def test_recordatorio_con_hora_de_la_mañana_y_minutos():
    resp = r.intentar("recuérdame correr a las 6:30 de la mañana")
    assert "06:30" in resp


def test_hora_objetivo_siempre_en_el_futuro():
    objetivo = r._calcular_hora_objetivo(1, 0, None)
    assert objetivo > datetime.now()
    assert objetivo - datetime.now() <= timedelta(hours=12, minutes=1)


def test_recurrente_dias_especificos():
    resp = r.intentar("recuérdame entregar el reporte los martes y jueves a las 9 am")
    assert "martes, jueves" in resp and "09:00" in resp
    with conectar() as con:
        fila = con.execute("SELECT * FROM recordatorios").fetchone()
    assert fila["recurrente"] == 1 and json.loads(fila["dias"]) == [1, 3]


def test_recurrente_diario():
    resp = r.intentar("recuérdame hacer ejercicio todos los días a las 7 pm")
    assert "todos los días" in resp and "19:00" in resp


def test_recurrente_sin_hora_pide_hora():
    assert "necesito que me diga una hora" in r.intentar("recuérdame regar las plantas los lunes")


def test_revisar_pendientes_avisa_una_sola_vez():
    pasado = (datetime.now() - timedelta(minutes=1)).isoformat()
    with conectar() as con:
        con.execute("INSERT INTO recordatorios (texto, recurrente, hora_objetivo, fecha_creado) VALUES ('tomar agua', 0, ?, ?)",
                    (pasado, pasado))
    assert r.revisar_pendientes() == ["tomar agua"]
    assert r.revisar_pendientes() == []


def test_revisar_pendientes_recurrente_hoy():
    hoy = datetime.now().weekday()
    with conectar() as con:
        con.execute("INSERT INTO recordatorios (texto, recurrente, hora, dias, fecha_creado) VALUES ('estirar', 1, '00:00', ?, 'x')",
                    (json.dumps([hoy]),))
    assert r.revisar_pendientes() == ["estirar"]
    assert r.revisar_pendientes() == []


def test_borrar_recordatorios():
    r.intentar("recuérdame comprar pan")
    assert "Borré el recordatorio" in r.intentar("borra el recordatorio de pan")
    assert "No encontré" in r.intentar("borra el recordatorio de leche")
    r.intentar("recuérdame algo")
    assert r.intentar("borra todos los recordatorios") == "Borré todos sus recordatorios."
    assert r.intentar("mis recordatorios") == "No tiene recordatorios pendientes."
