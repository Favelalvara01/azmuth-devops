import pytest
from skills import contactos, web


@pytest.mark.parametrize("entrada,esperado", [
    ("656 123 4567", "5216561234567"),
    ("+52 1 656 123 4567", "5216561234567"),
    ("15551234567", "15551234567"),
])
def test_normalizar_numero(entrada, esperado):
    assert contactos.normalizar_numero(entrada) == esperado


def test_guardar_buscar_listar_borrar_contacto():
    assert "guardé a Jesús" in contactos.intentar("guarda el contacto de Jesús como 6561234567")
    assert contactos.buscar("jesús") == "5216561234567"
    assert "Jesús — 5216561234567" in contactos.intentar("mis contactos")
    assert "Borré el contacto" in contactos.intentar("borra el contacto de jesús")
    assert contactos.buscar("Jesús") is None
    assert contactos.intentar("mis contactos") == "No tiene contactos guardados."


def test_busqueda_google(sin_efectos_externos):
    assert web.intentar("busca gatos con botas") == 'Aquí tiene los resultados para "gatos con botas".'
    assert sin_efectos_externos[-1].startswith("https://www.google.com/search?q=gatos")


def test_mapas(sin_efectos_externos):
    assert web.intentar("llévame a Plaza Sendero") == "Aquí tiene la ruta hacia plaza sendero."
    assert "google.com/maps" in sin_efectos_externos[-1]


def test_whatsapp_a_numero(sin_efectos_externos):
    resp = web.intentar("mándale un whatsapp al 6561234567 que diga voy en camino")
    assert "con su mensaje ya escrito" in resp
    assert sin_efectos_externos[-1] == "https://wa.me/5216561234567?text=voy%20en%20camino"


def test_whatsapp_a_contacto_no_guardado():
    assert "No tengo el número" in web.intentar("mándale un whatsapp a pedro que diga hola")


def test_whatsapp_a_contacto_guardado(sin_efectos_externos):
    contactos.intentar("guarda el contacto de Ana como 6560000000")
    assert web.intentar("abre whatsapp con ana") == "Le abro la conversación con ana."


def test_texto_vacio():
    assert web.intentar("") is None
