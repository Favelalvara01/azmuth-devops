"""
Skill: búsquedas, mapas/direcciones y WhatsApp (por número o por contacto
guardado — ver skills/contactos.py).
"""
import re
import os
import time
import webbrowser
from urllib.parse import quote

import confirmaciones

from . import contactos


def _abrir_whatsapp(numero: str, mensaje: str):
    """Prioriza abrir DIRECTO en WhatsApp Desktop vía su protocolo
    whatsapp:// — si el navegador es el que abre primero un enlace wa.me,
    esa misma página de WhatsApp intenta relevarte a la app de escritorio
    sola, y terminas con las dos ventanas abiertas. Abriendo el protocolo
    directo nos saltamos ese intermediario. Si no hay app de escritorio
    instalada (falla el protocolo), caemos de regreso al enlace web."""
    texto_codificado = quote(mensaje) if mensaje else ""
    uri_escritorio = f"whatsapp://send?phone={numero}" + (f"&text={texto_codificado}" if mensaje else "")
    try:
        os.startfile(uri_escritorio)
        return "app"  # se abrió WhatsApp de escritorio
    except Exception:
        pass
    try:
        url_web = f"https://wa.me/{numero}" + (f"?text={texto_codificado}" if mensaje else "")
        webbrowser.open(url_web)
        return "web"  # WhatsApp Web en el navegador
    except Exception:
        return None


def _ventana_whatsapp_al_frente(segundos: float = 15) -> bool:
    """Espera a que la ventana de WhatsApp de escritorio quede al frente (la trae si hace
    falta). Solo así es seguro presionar Enter: nunca se teclea en otro programa."""
    try:
        import pygetwindow as gw
    except ImportError:
        return False
    fin = time.time() + segundos
    while time.time() < fin:
        try:
            activa = gw.getActiveWindow()
            if activa is not None and str(activa.title).strip() == "WhatsApp":
                return True
            for ventana in gw.getWindowsWithTitle("WhatsApp"):
                if str(ventana.title).strip() == "WhatsApp":
                    ventana.activate()
        except Exception:
            pass
        time.sleep(0.4)
    return False


def _enviar_whatsapp(numero: str, mensaje: str, nombre: str) -> str:
    """Abre el chat con el mensaje escrito y presiona Enter por el usuario (ya confirmó)."""
    como = _abrir_whatsapp(numero, mensaje)
    if como is None:
        return "No pude abrir WhatsApp. Revise que tenga instalada la app o un navegador configurado."
    if como == "app" and _ventana_whatsapp_al_frente():
        time.sleep(1.5)  # que cargue el chat y el mensaje en la caja de texto
        if _ventana_whatsapp_al_frente(segundos=1):
            import pyautogui
            pyautogui.press("enter")
            return f"Listo, le envié el WhatsApp a {nombre}."
    return (f"Le dejé el mensaje escrito para {nombre}, pero no pude enviarlo yo solo: "
            "presione Enter en WhatsApp para mandarlo. Si instala WhatsApp de escritorio, lo envío yo.")


def _resolver_numero(destinatario: str):
    """Regresa (numero_normalizado, None) o (None, mensaje_de_error).
    Si destinatario ya parece un número lo normaliza directo; si no,
    intenta resolverlo como un contacto guardado."""
    numero = re.sub(r"[^\d+]", "", destinatario)
    if len(numero.replace("+", "")) >= 7:
        return contactos.normalizar_numero(numero), None

    numero_contacto = contactos.buscar(destinatario)
    if not numero_contacto:
        return None, (
            f'No tengo el número de "{destinatario}" ni me dio uno directamente. '
            f'Dígame "guarda el contacto de {destinatario} como su número" y de ahí '
            f'en adelante puede usar su nombre.'
        )
    return numero_contacto, None


def intentar(texto: str):
    if not texto:
        return None
        
    t = texto.lower().strip()

    # --- BÚSQUEDAS EN GOOGLE ---
    m = re.match(r"^(?:busca|búscame|googlea)\s+(.+?)(?:\s+en google)?$", t)
    if m:
        consulta = m.group(1).strip()
        webbrowser.open(f"https://www.google.com/search?q={quote(consulta)}")
        return f'Aquí tiene los resultados para "{consulta}".'

    # --- MAPAS Y DIRECCIONES (Limpio y sin errores en consola) ---
    patron_mapas = (
        r"^(?:cómo\s+llegar\s+a|como\s+llegar\s+a|cómo\s+llego\s+a|como\s+llego\s+a|"
        r"llévame\s+a|llevame\s+a|dame\s+direcciones\s+a|direcciones\s+a|"
        r"abre\s+mapas\s+a|dónde\s+queda|donde\s+queda)\s+(.+)"
    )
    m = re.match(patron_mapas, t)
    if m:
        lugar = m.group(1).strip()
        url = f"https://www.google.com/maps/search/{quote(lugar)}"
        
        # Apertura limpia utilizando el navegador predeterminado
        webbrowser.open(url)
        return f"Aquí tiene la ruta hacia {lugar}."

    # --- ABRIR LA CONVERSACIÓN DE WHATSAPP, SIN MANDAR NADA ---
    m = re.match(r"^abre\s+(?:la\s+)?(?:conversaci[oó]n(?:\s+de\s+whats\s?app)?\s+con|whats\s?app\s+con)\s+(.+)", t)
    if m:
        destinatario = m.group(1).strip()
        numero, error = _resolver_numero(destinatario)
        if error:
            return error
        numero = numero.lstrip("+")
        if _abrir_whatsapp(numero, ""):
            return f"Le abro la conversación con {destinatario}."
        return "No pude abrir WhatsApp. Revise que tenga instalada la app o un navegador configurado."

    # --- WHATSAPP CON MENSAJE (número directo o contacto guardado) ---
    # Se busca en el texto original (no en minúsculas) para respetar cómo escribió el mensaje
    m = re.match(r"^(?:m[aá]ndale|manda|escr[ií]bele|env[ií]ale)\s+(?:un\s+)?whats\s?app\s+(?:al?\s+)?(.+)",
                 texto.strip(), re.IGNORECASE)
    if m:
        resto = m.group(1).strip()
        mensaje = ""
        partes = re.split(r"\s+(?:que diga|diciendo|con el mensaje)\s+", resto, flags=re.IGNORECASE)
        if len(partes) > 1:
            resto, mensaje = partes[0].strip(), partes[1].strip()

        numero, error = _resolver_numero(resto)
        if error:
            return error

        numero = numero.lstrip("+")
        if mensaje:
            # Por voz llega todo en minúsculas: "jesús" → "Jesús", "ya llegué" → "Ya llegué"
            nombre = resto if resto != resto.lower() else resto.title()
            mensaje = mensaje[0].upper() + mensaje[1:]
            # Primero se lo lee y pregunta; solo si dice "sí" se envía (ver confirmaciones.py)
            confirmaciones.pedir(lambda: _enviar_whatsapp(numero, mensaje, nombre),
                                 al_cancelar="Listo, no envié el mensaje.")
            return f"Le voy a mandar a {nombre}: «{mensaje}». ¿Lo envío?"
        if _abrir_whatsapp(numero, ""):
            return f"Le abro WhatsApp para {resto}."
        return "No pude abrir WhatsApp. Revise que tenga instalada la app o un navegador configurado."

    return None
