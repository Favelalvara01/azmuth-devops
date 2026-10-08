"""Notificaciones de Windows para recordatorios."""
import base64
import subprocess
from unittest import mock

import main
import notificaciones


def _script(cmd):
    return base64.b64decode(cmd[-1]).decode("utf-16-le")


def test_xml_escapa_texto_peligroso():
    xml = notificaciones.construir_xml("Hola", "pagar <luz> & 'agua' \"ya\"")
    assert "&lt;luz&gt; &amp;" in xml and "<luz>" not in xml


def test_comando_codificado_no_lleva_texto_plano():
    cmd = notificaciones.construir_comando("Recordatorio", "x'); Remove-Item C:\\ -Recurse; ('")
    assert "-EncodedCommand" in cmd and "Remove-Item" not in " ".join(cmd)
    script = _script(cmd)
    # el texto queda dentro de un here-string literal, no como código
    assert "@'\n<toast" in script and "Remove-Item" in script


def test_en_linux_no_hace_nada(monkeypatch):
    monkeypatch.setattr(notificaciones.os, "name", "posix")
    assert notificaciones.notificar("a", "b") is False


def test_en_windows_lanza_powershell(monkeypatch):
    monkeypatch.setattr(notificaciones.os, "name", "nt")
    popen = mock.MagicMock()
    monkeypatch.setattr(subprocess, "Popen", popen)
    assert notificaciones.notificar("⏰ Recordatorio", "tomar agua") is True
    cmd = popen.call_args.args[0]
    assert cmd[0] == "powershell" and "tomar agua" in _script(cmd)


def test_error_queda_en_monitoreo(monkeypatch):
    monkeypatch.setattr(notificaciones.os, "name", "nt")
    monkeypatch.setattr(subprocess, "Popen", mock.MagicMock(side_effect=OSError("sin powershell")))
    assert notificaciones.notificar("a", "b") is False
    assert notificaciones.monitoreo.resumen()["ultimos_errores"][-1]["origen"] == "notificaciones"


def test_recordatorio_vencido_notifica(monkeypatch):
    monkeypatch.setattr(main.voice, "hablar", mock.MagicMock())
    notificar = mock.MagicMock()
    monkeypatch.setattr(main.notificaciones, "notificar", notificar)
    monkeypatch.setattr(main.skills.recordatorios, "revisar_pendientes", lambda: ["tomar agua"])
    main.revisar_recordatorios_una_vez()
    notificar.assert_called_once_with("⏰ Recordatorio de Azmuth", "tomar agua")


def test_saltos_de_linea_no_rompen_el_script():
    xml = notificaciones.construir_xml("a", "linea1\n'@\nWrite-Host hack")
    assert "\n" not in xml
