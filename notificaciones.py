"""Notificaciones nativas de Windows (toast) sin librerías extra.

Se usan para los recordatorios: aunque tengas la bocina apagada o estés en
otra app, el aviso aparece en la esquina y queda en el Centro de notificaciones.

Seguridad: el texto del usuario se escapa como XML y el script viaja a
PowerShell codificado en Base64 (-EncodedCommand), así un recordatorio con
comillas o símbolos no puede inyectar comandos.
"""
import base64
import os
import subprocess
from xml.sax.saxutils import escape

import monitoreo

# AppID de PowerShell: Windows exige un AppID registrado para mostrar el toast.
_APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"
_SIN_VENTANA = 0x08000000  # CREATE_NO_WINDOW

_PLANTILLA = """
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml(@'
{xml}
'@)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('{app_id}').Show($toast)
"""


def construir_xml(titulo: str, mensaje: str) -> str:
    # Una sola línea: así el texto nunca puede cerrar el here-string ('@) de PowerShell
    titulo, mensaje = (" ".join(x.split()) for x in (titulo, mensaje))
    return (
        '<toast scenario="reminder"><visual><binding template="ToastGeneric">'
        f"<text>{escape(titulo[:120])}</text><text>{escape(mensaje[:300])}</text>"
        "</binding></visual>"
        '<actions><action content="Listo" arguments="listo" activationType="system"/></actions>'
        '<audio src="ms-winsoundevent:Notification.Reminder"/></toast>'
    )


def construir_comando(titulo: str, mensaje: str) -> list[str]:
    script = _PLANTILLA.format(xml=construir_xml(titulo, mensaje), app_id=_APP_ID)
    codificado = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    return ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", codificado]


def notificar(titulo: str, mensaje: str) -> bool:
    """Muestra el toast en segundo plano. Devuelve False si no se pudo (p. ej. en Linux/Docker)."""
    if os.name != "nt":
        return False
    try:
        subprocess.Popen(construir_comando(titulo, mensaje), creationflags=_SIN_VENTANA,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        monitoreo.registrar_error("notificaciones", e)
        return False
