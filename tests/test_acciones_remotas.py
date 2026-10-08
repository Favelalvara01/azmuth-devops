"""HU-11: la tabla de despacho del control remoto y los manejadores de aplicaciones."""
import subprocess

import pytest

import acciones_remotas
from skills import aplicaciones


def test_tabla_tiene_las_26_acciones():
    assert len(acciones_remotas.ACCIONES) == 26


def test_accion_inexistente_devuelve_none():
    assert acciones_remotas.ejecutar("volar") is None


@pytest.mark.parametrize("accion", ["vol_up", "alt_tab", "escritorio"])
def test_scripts_de_teclado_bien_formados(accion):
    acciones_remotas.ejecutar(accion)
    script = subprocess.run.call_args.args[0][2]
    assert script.startswith("$code = ") and "keybd_event" in script
    assert script.count("{") == script.count("}")


def test_volumen_repite_cinco_veces():
    acciones_remotas.ejecutar("vol_up")
    assert "1..5 | ForEach-Object" in subprocess.run.call_args.args[0][2]


def test_brillo_sube_y_baja():
    acciones_remotas.ejecutar("brillo_up")
    assert "Min(100, $curr + 15)" in subprocess.run.call_args.args[0][2]
    acciones_remotas.ejecutar("brillo_down")
    assert "Max(0, $curr - 15)" in subprocess.run.call_args.args[0][2]


def test_cerrar_app_desconocida_detiene_la_cadena():
    # 'cierra X' que no está en la lista fija no debe caer en otros manejadores
    assert aplicaciones.intentar("cierra abreviaturas") is None


def test_cerrar_explorador_usa_powershell():
    assert aplicaciones.intentar("cierra explorador") == "Cerrando explorador."
    assert "Shell.Application" in subprocess.run.call_args.args[0]
