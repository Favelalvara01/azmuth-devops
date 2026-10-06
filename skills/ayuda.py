"""
Skill: ayuda — lista los comandos exactos que Azmuth reconoce de verdad,
tomados directo de las expresiones que cada skill acepta (no genéricos).
"""
import re


def intentar(texto: str):
    t = texto.lower().strip()

    if re.search(r"\b(comandos|qué puedes hacer|que puedes hacer|ayuda|manual|opciones)\b", t):
        return (
            "Estos son mis comandos exactos:\n"
            "\n"
            "NOTAS — \"toma nota: comprar café\" · \"mis notas\"\n"
            "\n"
            "RECORDATORIOS — \"recuérdame hablar con Jesús a la 1\" (con hora, te aviso solo) "
            "· \"recuérdame comprar pan\" (sin hora, solo queda guardado) "
            "· \"recuérdame hacer ejercicio todos los días a las 7\" (recurrente diario) "
            "· \"recuérdame entregar el reporte los martes y jueves a las 9\" (días específicos) "
            "· \"mis recordatorios\" · \"borra el recordatorio de Jesús\" · \"borra todos los recordatorios\"\n"
            "\n"
            "MEMORIA A LARGO PLAZO — \"recuerda que mi proyecto se llama Chispa\" "
            "· \"qué recuerdas de mi proyecto\" · \"qué sabes\" (lista todo) "
            "· \"olvídate de mi proyecto\" · \"olvida todo lo que recuerdas\" "
            "(también aprende cosas solo, sin que se lo pidas, durante la conversación libre)\n"
            "\n"
            "HÁBITOS — \"mis hábitos\" (qué tanto usa cada tipo de comando; también le "
            "sugiere cosas solo por su cuenta si nota un patrón fuerte, y deja de insistir "
            "si le dice que no varias veces seguidas)\n"
            "\n"
            "HORA, FECHA Y CLIMA — \"qué hora es\" · \"qué fecha es\" · \"qué clima hace\"\n"
            "\n"
            "BUSCAR Y MAPAS — \"busca gatos\" · \"llévame a Plaza Sendero\" "
            "· \"mándale un whatsapp al 5512345678 que diga voy en camino\" "
            "· \"mándale un whatsapp a Jesús que diga voy en camino\" (con contacto guardado) "
            "· \"abre whatsapp con Jesús\" / \"abre la conversación con Jesús\" (sin mandar mensaje)\n"
            "\n"
            "CONTACTOS — \"guarda el contacto de Jesús como 5512345678\" · \"mis contactos\" "
            "· \"borra el contacto de Jesús\"\n"
            "\n"
            "VOLUMEN Y MÚSICA — \"volumen a 50\" · \"sube el volumen\" · \"baja el volumen\" "
            "· \"pausa\" · \"siguiente\" · \"anterior\" · \"silencia\" · \"pon mi playlist\" "
            "· \"menea la chapa\"\n"
            "\n"
            "PESTAÑAS Y VENTANAS — \"nueva pestaña\" · \"cierra pestaña\" · \"siguiente pestaña\" "
            "· \"pestaña anterior\" · \"pestaña 3\" · \"cambia de ventana\"\n"
            "\n"
            "ABRIR APLICACIONES — di \"abre\" seguido de: bloc de notas, calculadora, explorador, "
            "paint, edge, word, excel, powerpoint, spotify, configuración, xbox, fortnite, "
            "rocket league, roblox, whatsapp, teams, visual studio code, android studio, "
            "youtube, messenger. También \"abre youtube y busca [algo]\".\n"
            "\n"
            "CERRAR APLICACIONES — di \"cierra\" seguido de: bloc de notas, calculadora, paint, "
            "edge, spotify, visual studio code, word, excel, powerpoint, xbox, teams, "
            "configuración, fortnite.\n"
            "\n"
            "SISTEMA — \"borra el historial\""
        )

    return None