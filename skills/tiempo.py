"""
Skill: hora, fecha, clima y pronóstico con recomendaciones.
La hora y fecha no necesitan internet. El clima sí: usa Open-Meteo (gratis, sin
clave) y geolocalización por red con respaldo automático para Ciudad Juárez.

- "qué clima hace" → solo el clima de ahorita.
- "va a llover hoy", "cómo estará el día", "necesito paraguas", "hará frío mañana",
  "qué me recomiendas llevar hoy" → pronóstico del día con recomendaciones
  (paraguas, chamarra, agua, bloqueador, viento...).
"""
import re
from datetime import datetime

import requests

_URL = "https://api.open-meteo.com/v1/forecast"

# Códigos del clima de la Organización Meteorológica Mundial (los usa Open-Meteo)
_CIELO = {
    0: "despejado", 1: "mayormente despejado", 2: "parcialmente nublado", 3: "nublado",
    45: "con niebla", 48: "con niebla", 51: "con llovizna ligera", 53: "con llovizna", 55: "con llovizna intensa",
    56: "con llovizna helada", 57: "con llovizna helada", 61: "con lluvia ligera", 63: "con lluvia",
    65: "con lluvia fuerte", 66: "con lluvia helada", 67: "con lluvia helada", 71: "con nevada ligera",
    73: "con nevada", 75: "con nevada fuerte", 77: "con aguanieve", 80: "con chubascos ligeros",
    81: "con chubascos", 82: "con chubascos fuertes", 85: "con chubascos de nieve", 86: "con chubascos de nieve",
    95: "con tormenta eléctrica", 96: "con tormenta y granizo", 99: "con tormenta y granizo",
}
_NIEVE = {71, 73, 75, 77, 85, 86}
_TORMENTA = {95, 96, 99}


def _ubicacion():
    try:
        # Ubicación real actual por IP
        datos = requests.get("https://ipapi.co/json/", timeout=4).json()
        lat, lon, ciudad = datos.get("latitude"), datos.get("longitude"), datos.get("city")
        if not lat or not lon or not ciudad:
            raise ValueError("Ubicación por IP no disponible")
        return lat, lon, ciudad
    except Exception:
        return 31.7333, -106.4833, "Ciudad Juárez"  # respaldo si la red falla


def _obtener_clima():
    lat, lon, ciudad = _ubicacion()
    try:
        clima = requests.get(_URL, params={
            "latitude": lat, "longitude": lon, "timezone": "auto",
            "current": "temperature_2m,apparent_temperature,weather_code",
        }, timeout=5).json()
        actual = clima["current"]
        temp, sensacion = round(actual["temperature_2m"]), round(actual["apparent_temperature"])
        cielo = _CIELO.get(actual.get("weather_code"))
        return (f"En {ciudad} hace {temp}°C ahora mismo" + (f" ({cielo})" if cielo else "")
                + f", sensación térmica de {sensacion}°C.")
    except Exception as e:
        return f"No pude consultar el clima ahora mismo: {e}"


def _hora_de_mas_lluvia(horas, probabilidades, dia: str):
    """La hora del día pedido con más probabilidad de lluvia (solo desde ahora si es hoy)."""
    ahora = datetime.now().strftime("%Y-%m-%dT%H")
    mejor = None
    for hora, prob in zip(horas, probabilidades):
        if hora.startswith(dia) and hora[:13] >= max(ahora, dia + "T00") and prob is not None:
            if mejor is None or prob > mejor[1]:
                mejor = (hora, prob)
    return mejor


def _recomendaciones(maxima, minima, lluvia, uv, viento, codigo, pregunta_lluvia):
    consejos = []
    if codigo in _TORMENTA:
        consejos.append("hay probabilidad de tormenta eléctrica: lleve paraguas y evite estar en lugares abiertos")
    elif lluvia >= 60:
        consejos.append("es muy probable que llueva: le recomiendo llevar paraguas o impermeable")
    elif lluvia >= 30:
        consejos.append("podría llover: por si acaso, lleve un paraguas")
    elif pregunta_lluvia:
        consejos.append("no se espera lluvia, puede dejar el paraguas en casa")
    if codigo in _NIEVE:
        consejos.append("podría nevar: abríguese muy bien y maneje con cuidado")
    if minima <= 5:
        consejos.append("hará mucho frío: lleve chamarra gruesa, gorro y guantes")
    elif minima <= 12:
        consejos.append("en la mañana y en la noche estará fresco: lleve chamarra o sudadera")
    if maxima >= 35:
        consejos.append("hará mucho calor: tome mucha agua y evite el sol del mediodía")
    elif maxima >= 30:
        consejos.append("hará calor: lleve agua")
    if uv >= 8:
        consejos.append("el sol estará muy fuerte: use bloqueador, gorra y lentes de sol")
    elif uv >= 6:
        consejos.append("use bloqueador si va a estar al sol")
    if viento >= 40:
        consejos.append(f"habrá viento fuerte, de hasta {round(viento)} km/h: puede levantar polvo, cuide sus ojos")
    return consejos


def _pronostico(manana: bool = False, pregunta_lluvia: bool = False):
    lat, lon, ciudad = _ubicacion()
    try:
        datos = requests.get(_URL, params={
            "latitude": lat, "longitude": lon, "timezone": "auto", "forecast_days": 2,
            "current": "temperature_2m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                     "uv_index_max,wind_speed_10m_max",
            "hourly": "precipitation_probability",
        }, timeout=5).json()
        d, i = datos["daily"], (1 if manana else 0)
        maxima, minima = round(d["temperature_2m_max"][i]), round(d["temperature_2m_min"][i])
        lluvia = d["precipitation_probability_max"][i] or 0
        uv = d.get("uv_index_max", [0, 0])[i] or 0
        viento = d.get("wind_speed_10m_max", [0, 0])[i] or 0
        codigo = d["weather_code"][i]
    except Exception as e:
        return f"No pude consultar el pronóstico ahora mismo: {e}"

    cuando = "Mañana" if manana else "Hoy"
    cielo = _CIELO.get(codigo, "")
    partes = [f"{cuando} en {ciudad}: máxima de {maxima}°C y mínima de {minima}°C" + (f", {cielo}" if cielo else "") + "."]
    if not manana and "current" in datos:
        partes.append(f"Ahorita hay {round(datos['current']['temperature_2m'])}°C.")
    texto_lluvia = f"Probabilidad de lluvia: {lluvia}%"
    hourly = datos.get("hourly", {})
    pico = _hora_de_mas_lluvia(hourly.get("time", []), hourly.get("precipitation_probability", []), d["time"][i]) \
        if lluvia >= 30 and "time" in d else None
    if pico and pico[1] >= 30:
        texto_lluvia += f", sobre todo cerca de las {int(pico[0][11:13])}:00"
    partes.append(texto_lluvia + ".")

    consejos = _recomendaciones(maxima, minima, lluvia, uv, viento, codigo, pregunta_lluvia)
    if consejos:
        primero = consejos[0][0].upper() + consejos[0][1:]
        partes.append(" ".join([primero + "."] + [c[0].upper() + c[1:] + "." for c in consejos[1:]]))
    else:
        partes.append("Será un día agradable, no necesita nada especial.")
    return " ".join(partes)


_LLUVIA = re.compile(r"\b(?:llover[aá]?|lluvia|llueve|lloviendo|paraguas|sombrilla|impermeable|tormenta)\b")
_PRONOSTICO = re.compile(
    r"^(?:(?:c[oó]mo|qu[eé]\s+tal)\s+(?:va\s+a\s+estar|estar[aá]|est[aá]|ser[aá]|va\s+a\s+ser)\s+(?:el\s+)?(?:d[ií]a|clima|tiempo)"
    r"|(?:el\s+)?pron[oó]stico|(?:va\s+a|crees\s+que\s+va\s+a)\s+(?:llover|hacer\s+(?:fr[ií]o|calor)|nevar)"
    r"|llover[aá]|habr[aá]\s+lluvia|nevar[aá]|har[aá]\s+(?:fr[ií]o|calor)|necesito\s+(?:llevar\s+)?(?:paraguas|sombrilla|chamarra|su[eé]ter|sudadera)"
    r"|(?:debo|tengo\s+que)\s+llevar\s+(?:paraguas|sombrilla|chamarra|su[eé]ter|sudadera)"
    r"|qu[eé]\s+me\s+(?:recomiendas|aconsejas)\s+(?:llevar|ponerme|usar)|qu[eé]\s+(?:me\s+)?pongo"
    r"|(?:hay\s+)?probabilidad(?:es)?\s+de\s+lluvia)")


def intentar(texto: str):
    t = texto.lower().strip()
    t_limpio = re.sub(r"[¿?¡!.,]", "", t).strip()

    if re.match(r"^(qué hora es|dime la hora|hora actual)", t):
        return "Son las " + datetime.now().strftime("%H:%M") + "."

    if re.match(r"^(qué (día|fecha) es|dime la fecha|fecha de hoy)", t):
        return "Hoy es " + datetime.now().strftime("%A %d de %B de %Y") + "."

    if re.match(r"^(qué clima hace|cómo está el clima|dime el clima|clima de hoy|qué temperatura hace|cuántos grados hace)", t):
        return _obtener_clima()

    if _PRONOSTICO.match(t_limpio):
        # "mañana" = el día siguiente; "en la mañana" / "por la mañana" = hoy temprano
        manana = bool(re.search(r"\bma[ñn]ana\b", t_limpio)) and not re.search(r"\b(?:en|por|de)\s+la\s+ma[ñn]ana\b", t_limpio)
        return _pronostico(manana=manana,
                           pregunta_lluvia=bool(_LLUVIA.search(t_limpio)))

    return None
