"""Pronóstico con recomendaciones (paraguas, chamarra...) y trato por nombre."""
import datetime as dt
from unittest import mock

import pytest

import cerebro
import config
import idioma
import skills
import tematicas
from skills import tiempo


def _resp(datos):
    r = mock.MagicMock()
    r.json.return_value = datos
    return r


_IP = {"latitude": 31.7, "longitude": -106.4, "city": "Juárez"}


def _pronostico(lluvia=(10, 10), maxima=(26, 26), minima=(15, 15), uv=(4, 4), viento=(15, 15), codigo=(1, 1), por_hora=None):
    hoy = dt.date.today()
    dias = [hoy.isoformat(), (hoy + dt.timedelta(days=1)).isoformat()]
    horas = [f"{d}T{h:02d}:00" for d in dias for h in range(24)]
    return {
        "current": {"temperature_2m": 21.4, "weather_code": codigo[0]},
        "daily": {"time": dias, "weather_code": list(codigo), "temperature_2m_max": list(maxima),
                  "temperature_2m_min": list(minima), "precipitation_probability_max": list(lluvia),
                  "uv_index_max": list(uv), "wind_speed_10m_max": list(viento)},
        "hourly": {"time": horas, "precipitation_probability": por_hora or [0] * 48},
    }


def _preguntar(frase, datos):
    with mock.patch("skills.tiempo.requests.get", side_effect=[_resp(_IP), _resp(datos)]) as get:
        return tiempo.intentar(frase), get


@pytest.fixture(autouse=True)
def espanol():
    yield
    idioma.cambiar("es", guardar=False)


def test_solo_el_clima_si_pregunta_que_clima_hace():
    respuesta, get = _preguntar("qué clima hace", {"current": {"temperature_2m": 24, "apparent_temperature": 25, "weather_code": 0}})
    assert respuesta == "En Juárez hace 24°C ahora mismo (despejado), sensación térmica de 25°C."
    assert "daily" not in get.call_args.kwargs["params"]  # sin pronóstico ni consejos


@pytest.mark.parametrize("frase", ["va a llover hoy", "¿Va a llover hoy?", "lloverá hoy", "necesito paraguas",
                                   "habrá lluvia hoy", "hay probabilidad de lluvia"])
def test_si_va_a_llover_recomienda_paraguas(frase):
    por_hora = [0] * 17 + [70] + [0] * 30
    respuesta, _ = _preguntar(frase, _pronostico(lluvia=(70, 0), por_hora=por_hora))
    assert "Probabilidad de lluvia: 70%" in respuesta and "paraguas" in respuesta


def test_hora_de_mas_lluvia(monkeypatch):
    por_hora = [0] * 24 + [0] * 24
    por_hora[17] = 55
    with mock.patch.object(tiempo, "datetime") as falso:
        falso.now.return_value = dt.datetime.combine(dt.date.today(), dt.time(8, 0))
        respuesta, _ = _preguntar("va a llover hoy", _pronostico(lluvia=(55, 0), por_hora=por_hora))
    assert "cerca de las 17:00" in respuesta and "por si acaso" in respuesta


def test_sin_lluvia_dice_que_no_hace_falta_paraguas():
    respuesta, _ = _preguntar("va a llover hoy", _pronostico(lluvia=(5, 5)))
    assert "no se espera lluvia" in respuesta.lower()


def test_dia_completo_con_frio_calor_sol_y_viento():
    respuesta, _ = _preguntar("cómo estará el día de hoy", _pronostico(maxima=(36, 20), minima=(4, 4), uv=(9, 3), viento=(45, 10)))
    assert "máxima de 36°C y mínima de 4°C" in respuesta
    for consejo in ("chamarra gruesa", "mucha agua", "bloqueador", "viento fuerte"):
        assert consejo in respuesta
    assert "no se espera lluvia" not in respuesta.lower()  # no preguntó por la lluvia


def test_dia_tranquilo():
    respuesta, _ = _preguntar("qué me recomiendas llevar hoy", _pronostico())
    assert "Será un día agradable" in respuesta


def test_manana_usa_el_dia_siguiente():
    respuesta, _ = _preguntar("va a llover mañana", _pronostico(lluvia=(0, 80)))
    assert respuesta.startswith("Mañana en Juárez") and "80%" in respuesta and "paraguas" in respuesta


def test_en_la_manana_es_hoy():
    respuesta, _ = _preguntar("va a llover en la mañana", _pronostico(lluvia=(0, 80)))
    assert respuesta.startswith("Hoy en Juárez")


def test_pronostico_sin_red_no_truena():
    with mock.patch("skills.tiempo.requests.get", side_effect=Exception("sin red")):
        assert tiempo.intentar("va a llover hoy").startswith("No pude consultar el pronóstico")


def test_en_ingles_will_it_rain(monkeypatch):
    idioma.cambiar("en", guardar=False)
    monkeypatch.setattr(cerebro, "traducir", lambda texto, a="en": f"[EN] {texto}")
    with mock.patch("skills.tiempo.requests.get", side_effect=[_resp(_IP), _resp(_pronostico(lluvia=(0, 90)))]):
        respuesta, skill = skills.procesar("will it rain tomorrow")
    assert skill == "tiempo" and respuesta.startswith("[EN] Mañana")


# ---------- Trato por nombre ----------
def test_con_nombre_dice_bienvenido_y_no_senor(monkeypatch):
    monkeypatch.setattr(config, "NOMBRE_USUARIO", "Favela")
    assert tematicas.saludo() == "Bienvenido, Favela. Sistema iniciado. A sus órdenes."
    tematicas.cambiar("halloween", guardar=False)
    assert "¡Feliz Halloween, Favela!" in tematicas.saludo() and "señor" not in tematicas.saludo()
    assert idioma.trato() == "Favela"
    assert "«Favela»" in cerebro._construir_system_prompt()


def test_sin_nombre_sigue_diciendo_senor(monkeypatch):
    monkeypatch.setattr(config, "NOMBRE_USUARIO", "")
    assert tematicas.saludo() == "Sistema iniciado. A sus órdenes."
    assert idioma.trato() == "señor"
    idioma.cambiar("en", guardar=False)
    assert idioma.trato() == "sir"
