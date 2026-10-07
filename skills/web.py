"""
Skill: búsquedas, mapas/direcciones y WhatsApp (por número o por contacto
guardado — ver skills/contactos.py).
"""
import re
import os
import webbrowser
from urllib.parse import quote

from . import contactos


def _abrir_whatsapp(numero: str, mensaje: str) -> bool:
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
        return True
    except Exception:
        pass
    try:
        url_web = f"https://wa.me/{numero}" + (f"?text={texto_codificado}" if mensaje else "")
        webbrowser.open(url_web)
        return True
    except Exception:
        return False


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
    patron_mapas = r"^(?:cómo\s+llegar\s+a|como\s+llegar\s+a|cómo\s+llego\s+a|como\s+llego\s+a|llévame\s+a|llevame\s+a|dame\s+direcciones\s+a|direcciones\s+a|abre\s+mapas\s+a|dónde\s+queda|donde\s+queda)\s+(.+)"
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
    m = re.match(r"^(?:mándale|manda|escríbele|envíale)\s+(?:un\s+)?whats\s?app\s+(?:al?\s+)?(.+)", t)
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
        if _abrir_whatsapp(numero, mensaje):
            return f"Le abro WhatsApp para {resto}" + (" con su mensaje ya escrito." if mensaje else ".")
        return "No pude abrir WhatsApp. Revise que tenga instalada la app o un navegador configurado."

    return None
