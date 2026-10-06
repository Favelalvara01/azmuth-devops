from skills import notas


def test_crear_y_listar_notas():
    assert notas.intentar("toma nota: comprar café") == 'Nota guardada: "comprar café".'
    notas.intentar("anota que estudiar métricas")
    lista = notas.intentar("mis notas")
    assert "1. comprar café" in lista and "2. estudiar métricas" in lista


def test_lista_vacia():
    assert notas.intentar("mis notas") == "No tiene notas guardadas."


def test_borrar_una_nota_y_todas():
    notas.intentar("toma nota: llamar al doctor")
    notas.intentar("toma nota: lavar el carro")
    assert "Borré la nota" in notas.intentar("borra la nota sobre doctor")
    assert "doctor" not in notas.intentar("mis notas")
    assert notas.intentar("borra todas las notas") == "Borré todas sus notas."
    assert notas.intentar("mis notas") == "No tiene notas guardadas."


def test_borrar_nota_inexistente():
    assert "No encontré" in notas.intentar("borra la nota sobre marte")


def test_frase_ajena_no_la_toma():
    assert notas.intentar("qué hora es") is None
