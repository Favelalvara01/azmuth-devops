"""
Skill: hora, fecha y clima.
La hora y fecha no necesitan internet. El clima sí, usa Open-Meteo
y geolocalización por red con respaldo automático para Ciudad Juárez.
"""
import re
from datetime import datetime
import requests


def _obtener_clima():
    try:
        # Intentamos obtener la ubicación real actual por IP mediante un servicio web
        ubicacion_ip = requests.get("https://ipapi.co/json/", timeout=4).json()
        lat = ubicacion_ip.get("latitude")
        lon = ubicacion_ip.get("longitude")
        ciudad = ubicacion_ip.get("city")

        # Si la IP nos regresa un valor extraño o fuera de rango, usamos Juárez por defecto
        if not lat or not lon or not ciudad:
            raise Exception("Ubicación por IP no disponible")
            
    except Exception:
        # Respaldo automático garantizado para Ciudad Juárez si la red falla
        lat = 31.7333
        lon = -106.4833
        ciudad = "Ciudad Juárez"

    try:
        clima = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature",
                "timezone": "auto",
            },
            timeout=5,
        ).json()

        temp = round(clima["current"]["temperature_2m"])
        sensacion = round(clima["current"]["apparent_temperature"])
        return f"En {ciudad} hace {temp}°C ahora mismo, sensación térmica de {sensacion}°C."
    except Exception as e:
        return f"No pude consultar el clima ahora mismo: {e}"


def intentar(texto: str):
    t = texto.lower().strip()

    if re.match(r"^(qué hora es|dime la hora|hora actual)", t):
        return "Son las " + datetime.now().strftime("%H:%M") + "."

    if re.match(r"^(qué (día|fecha) es|dime la fecha|fecha de hoy)", t):
        return "Hoy es " + datetime.now().strftime("%A %d de %B de %Y") + "."

    if re.match(r"^(qué clima hace|cómo está el clima|dime el clima|clima de hoy|qué temperatura hace|cuántos grados hace)", t):
        return _obtener_clima()

    return None
