import re
from datetime import datetime
from unittest import mock

from skills import tiempo, habitos


def test_hora_y_fecha():
    assert re.fullmatch(r"Son las \d{2}:\d{2}\.", tiempo.intentar("qué hora es"))
    assert tiempo.intentar("qué fecha es").startswith("Hoy es ")
    assert tiempo.intentar("hola") is None


def _respuesta(datos):
    r = mock.MagicMock()
    r.json.return_value = datos
    return r


def test_clima_con_ubicacion_por_ip():
    with mock.patch("skills.tiempo.requests.get", side_effect=[
        _respuesta({"latitude": 31.7, "longitude": -106.4, "city": "Juárez"}),
        _respuesta({"current": {"temperature_2m": 24.4, "apparent_temperature": 26.6}}),
    ]):
        assert tiempo.intentar("qué clima hace") == "En Juárez hace 24°C ahora mismo, sensación térmica de 27°C."


def test_clima_respaldo_ciudad_juarez_si_falla_la_ip():
    with mock.patch("skills.tiempo.requests.get", side_effect=[
        Exception("sin red"),
        _respuesta({"current": {"temperature_2m": 10, "apparent_temperature": 8}}),
    ]):
        assert tiempo.intentar("dime el clima").startswith("En Ciudad Juárez hace 10°C")


def test_clima_sin_red_no_truena():
    with mock.patch("skills.tiempo.requests.get", side_effect=Exception("sin red")):
        assert tiempo.intentar("clima de hoy").startswith("No pude consultar el clima")


def test_habitos_registro_y_consulta():
    assert habitos.intentar("mis hábitos") == "Todavía no tengo suficientes datos sobre sus hábitos."
    for _ in range(3):
        habitos.registrar_uso("multimedia")
    habitos.registrar_uso("notas")
    habitos.registrar_uso("")
    texto = habitos.intentar("mis hábitos")
    assert "1. Multimedia / música — 3 veces" in texto
    assert "Multimedia / música: 3 veces" in habitos.resumen_para_perfil()


def test_sugerencia_por_hora_y_silencio_tras_rechazos():
    for _ in range(3):
        habitos.registrar_uso("multimedia")
    assert habitos.sugerir_por_hora() == ("¿quiere que le ponga música?", "multimedia")
    assert habitos.sugerir_por_hora() is None  # no repite antes de 2 horas
    for _ in range(3):
        habitos.registrar_respuesta_sugerencia("multimedia", aceptada=False)
    from basedatos import conectar
    with conectar() as con:
        fila = con.execute("SELECT silenciada_hasta FROM habitos_categorias WHERE categoria='multimedia'").fetchone()
    assert datetime.fromisoformat(fila["silenciada_hasta"]) > datetime.now()
    habitos.registrar_respuesta_sugerencia("multimedia", aceptada=True)
    with conectar() as con:
        fila = con.execute("SELECT silenciada_hasta FROM habitos_categorias WHERE categoria='multimedia'").fetchone()
    assert fila["silenciada_hasta"] is None
