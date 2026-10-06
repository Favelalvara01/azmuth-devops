from datetime import datetime, timedelta

from basedatos import conectar
from skills import memoria, perfil


def test_guardar_y_consultar():
    assert memoria.intentar("recuerda que mi equipo favorito es Bravos").startswith("Guardado")
    assert "Bravos" in memoria.intentar("qué recuerdas de equipo")
    assert memoria.recordar_todo() == ["mi equipo favorito es Bravos"]


def test_no_duplica_hechos_parecidos():
    assert memoria.guardar_hecho("le gusta el café") is True
    assert memoria.guardar_hecho("Le gusta el café") is False
    assert memoria.guardar_hecho("   ") is False


def test_olvidar():
    memoria.guardar_hecho("estudia en la UTCJ")
    assert "olvidé" in memoria.intentar("olvídate de utcj")
    assert "No tengo nada" in memoria.intentar("olvídate de marte")
    memoria.guardar_hecho("x")
    assert "borré toda" in memoria.intentar("olvida todo lo que recuerdas")
    assert memoria.intentar("qué sabes") == "Todavía no me ha pedido que recuerde nada."


def test_perfil_toca_actualizar():
    assert perfil.obtener_perfil_actual() == ""
    assert perfil.toca_actualizar() is True
    perfil.guardar_perfil("  Usuario práctico.  ")
    assert perfil.obtener_perfil_actual() == "Usuario práctico."
    assert perfil.toca_actualizar() is False
    viejo = (datetime.now() - timedelta(hours=25)).isoformat()
    with conectar() as con:
        con.execute("UPDATE perfil SET ultima_actualizacion = ? WHERE id = 1", (viejo,))
    assert perfil.toca_actualizar() is True
