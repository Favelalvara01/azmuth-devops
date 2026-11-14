"""
PRUEBAS DE COMPONENTES (automatizadas)
======================================
Un componente es una pieza más grande que una función: un módulo completo
con su propia responsabilidad (una skill, el gestor de chats, el monitoreo,
el catálogo del control remoto). Se prueba el componente entero, por su
interfaz pública, pero AISLADO del resto (con su propia base de datos
temporal y con dobles de prueba en lugar de Windows).

Ejecutar:  py -3.13 -m pytest -m componente -v
"""
import subprocess
from datetime import datetime, timedelta

import pytest

import acciones_remotas
import chats
import monitoreo
from basedatos import conectar
from skills import notas, recordatorios

pytestmark = pytest.mark.componente


def test_cp_com_01_skill_notas_ciclo_completo():
    """CP-COM-01: el componente notas crea, lista y borra notas en SQLite."""
    assert notas.intentar("toma nota: comprar pan") == 'Nota guardada: "comprar pan".'
    assert notas.intentar("anota que la junta es el lunes") == 'Nota guardada: "la junta es el lunes".'
    assert notas.intentar("mis notas") == "Sus notas:\n1. comprar pan\n2. la junta es el lunes"
    assert notas.intentar("borra la nota de pan") == 'Borré la nota sobre "pan".'
    assert notas.intentar("borra todas mis notas") == "Borré todas sus notas."
    assert notas.intentar("mis notas") == "No tiene notas guardadas."
    assert notas.intentar("pon música") is None          # no le toca: regresa None


def test_cp_com_02_recordatorio_se_avisa_una_sola_vez():
    """CP-COM-02: recordatorios guarda la hora y revisar_pendientes() avisa una vez."""
    respuesta = recordatorios.intentar("recuérdame tomar agua a las 5 pm")
    assert "tomar agua" in respuesta and "17:00" in respuesta
    # Simulamos que la hora ya pasó moviendo la hora objetivo al pasado
    with conectar() as con:
        con.execute("UPDATE recordatorios SET hora_objetivo = ?",
                    ((datetime.now() - timedelta(minutes=1)).isoformat(),))
    assert recordatorios.revisar_pendientes() == ["tomar agua"]
    assert recordatorios.revisar_pendientes() == []    # no se repite


def test_cp_com_03_gestor_de_chats():
    """CP-COM-03: chats crea conversaciones, guarda mensajes y cambia el activo."""
    a = chats.crear_chat()
    b = chats.crear_chat()
    assert chats.obtener_activo() == b
    chats.agregar_mensaje(a, "user", "Hola Azmuth")
    chats.agregar_mensaje(a, "assistant", "Hola, señor")
    assert [m["rol"] for m in chats.obtener_mensajes(a)] == ["user", "assistant"]
    chats.borrar_chat(b)
    assert not chats.existe(b)
    assert chats.obtener_activo(crear_si_no_hay=False) is None


def test_cp_com_04_monitoreo_registra_errores_sin_tronar(log_temporal):
    """CP-COM-04: monitoreo guarda el error en errores.log y lo resume para /salud."""
    try:
        1 / 0
    except ZeroDivisionError as e:
        monitoreo.registrar_error("prueba-componente", e)
    resumen = monitoreo.resumen()
    assert resumen["ultimos_errores"][-1]["tipo"] == "ZeroDivisionError"
    assert "prueba-componente" in log_temporal.read_text(encoding="utf-8")


def test_cp_com_05_catalogo_del_control_remoto():
    """CP-COM-05: acciones_remotas ejecuta acciones conocidas y rechaza desconocidas."""
    assert acciones_remotas.ejecutar("bloquear") == "PC bloqueada"
    assert subprocess.run.called                        # se pidió el comando a Windows (simulado)
    assert acciones_remotas.ejecutar("formatear_disco") is None
    assert len(acciones_remotas.ACCIONES) >= 20
