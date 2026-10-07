"""
El "cerebro" de AZMUTH: aquí se conversa con Claude (Anthropic)
cuando ninguna skill local supo resolver el comando directamente.

También vive aquí el aprendizaje "pasivo": la extracción automática de
hechos memorables durante la conversación libre (sin que el usuario
tenga que decir "recuerda que...") y la generación periódica de un
perfil de personalidad/estilo a partir de todo lo que Azmuth ya sabe.
"""
import re
import anthropic
import config
from skills import memoria, habitos, perfil

SYSTEM_PROMPT = """Eres AZMUTH, un asistente de inteligencia artificial personal que vive \
en la computadora de tu usuario y le ayuda con tareas, preguntas, estudio y organización. \
Respondes siempre en español neutro/mexicano. Tu tono es servicial, eficiente, un poco \
formal (tratas de "usted" y a veces dices "señor" con naturalidad, sin exagerar) pero \
cercano y con un toque de ingenio seco. Sé conciso: 2 a 5 oraciones salvo que te pidan \
explícitamente más detalle. Nunca inventes que ejecutaste una acción real en la \
computadora del usuario (abrir programas, mandar mensajes, etc.) — solo las skills \
registradas en la carpeta skills/ pueden hacer eso de verdad; tú solo conversas y \
respondes preguntas. Si detectas que el usuario pidió algo que suena a una acción del \
sistema, sugiérele la frase exacta que sí activa esa skill, en vez de fingir que ya lo hiciste.

APRENDIZAJE AUTOMÁTICO: si durante la conversación el usuario reveló un dato duradero \
sobre sí mismo que valga la pena recordar en conversaciones futuras -un gusto, un \
proyecto, una relación, una rutina, algo que lo describe-, agrega al FINAL de tu \
respuesta, en su propia línea, una marca así: [MEMORIA: hecho corto en tercera persona]. \
Puedes agregar varias líneas [MEMORIA: ...] si hay varios hechos distintos. Sé muy \
selectivo: NO marques estados de ánimo pasajeros, preguntas de una sola vez, ni nada que \
ya te haya dicho antes (lo verás en "lo que ya sabes de él" si te lo pasan como contexto). \
Si no hay nada nuevo que valga la pena recordar, no agregues ninguna línea [MEMORIA: ...]. \
El usuario nunca ve estas líneas -se recortan antes de mostrárselas-, así que escríbelas \
tal cual, sin explicarlas ni comentarlas en el resto de tu respuesta."""

EXTRA_ESCRITORIO = """

MODO ESCRITORIO: ahora el usuario te está ESCRIBIENDO en una ventana de chat (como \
ChatGPT o Claude), no hablando. Aquí sí puedes dar respuestas completas y del largo que \
pida la pregunta, y usar Markdown cuando ayude a leer mejor: listas, **negritas**, \
tablas y bloques de código con su lenguaje (```python). Sigue siendo AZMUTH, con el \
mismo tono. Las reglas de [MEMORIA: ...] y de no fingir acciones siguen aplicando."""

_RE_MEMORIA = re.compile(r"\[MEMORIA:\s*(.+?)\]", re.IGNORECASE)

_cliente = None
_historial = []


def _obtener_cliente():
    global _cliente
    if _cliente is None:
        _cliente = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _cliente


def _construir_system_prompt():
    """El puente entre lo que Azmuth ya sabe (memoria explícita +
    automática, y el perfil de personalidad) y la conversación libre:
    cada vez que se habla con Claude, se le pasa todo esto como
    contexto, para que lo use de forma natural sin que haya que
    programar nada por adelantado."""
    prompt = SYSTEM_PROMPT

    hechos = memoria.recordar_todo()
    if hechos:
        lista = "\n".join(f"- {h}" for h in hechos)
        prompt += (
            "\n\nEsto es lo que ya sabes sobre el usuario (guardado explícitamente por "
            "voz o aprendido solo en conversaciones anteriores). Úsalo cuando sea "
            "relevante, de forma natural, sin recitar la lista completa a menos que te "
            "la pidan directamente:\n" + lista
        )

    perfil_texto = perfil.obtener_perfil_actual()
    if perfil_texto:
        prompt += "\n\nPerfil de personalidad/estilo del usuario (generado a partir de su historial de uso):\n" + perfil_texto

    return prompt


def _extraer_y_guardar_memoria(texto: str) -> str:
    """Saca las líneas [MEMORIA: ...] de la respuesta de Claude, guarda
    cada hecho nuevo en skills/memoria.py, y regresa el texto ya limpio
    (sin esas líneas) para hablarlo/mostrarlo."""
    hechos = _RE_MEMORIA.findall(texto)
    for hecho in hechos:
        memoria.guardar_hecho(hecho.strip(), origen="automatico")
    return _RE_MEMORIA.sub("", texto).strip()


def preguntar(texto_usuario: str, mensajes=None, modo: str = "voz") -> str:
    """Manda el mensaje a Claude y regresa la respuesta en texto.

    - Modo voz (por defecto): usa el historial en memoria de la conversación
      hablada, con respuestas cortas para decirlas en voz alta.
    - Modo escritorio: recibe en `mensajes` el historial del chat escrito
      (ya incluye el mensaje actual del usuario) y permite respuestas largas
      con Markdown. Ese historial vive en la base de datos (ver chats.py)."""
    if not config.ANTHROPIC_API_KEY:
        return "No tengo configurada mi clave de Anthropic todavía. Revise su archivo .env, por favor."

    cliente = _obtener_cliente()
    usar_historial_voz = mensajes is None
    if usar_historial_voz:
        _historial.append({"role": "user", "content": texto_usuario})
        mensajes = _historial[-12:]

    system = _construir_system_prompt()
    if modo == "escritorio":
        system += EXTRA_ESCRITORIO

    try:
        respuesta = cliente.messages.create(
            model=config.MODELO_CLAUDE,
            max_tokens=2000 if modo == "escritorio" else 800,
            system=system,
            messages=mensajes,
        )
        texto = "".join(bloque.text for bloque in respuesta.content if bloque.type == "text").strip()
        texto = _extraer_y_guardar_memoria(texto) if texto else texto
        texto = texto or "No logré generar una respuesta. ¿Puede intentarlo de nuevo?"
        if usar_historial_voz:
            _historial.append({"role": "assistant", "content": texto})
        return texto
    except Exception as e:
        return f"Tuve un problema conectando con mi cerebro: {e}"


def borrar_historial():
    global _historial
    _historial = []


def actualizar_perfil_si_toca():
    """Se llama en segundo plano (main.py) cada cierto tiempo. Si ya
    toca regenerar el perfil (ver skills/perfil.py) y hay suficiente
    historial acumulado, le pide a Claude que sintetice un perfil de
    personalidad/estilo corto a partir de la memoria y los hábitos."""
    if not config.ANTHROPIC_API_KEY or not perfil.toca_actualizar():
        return

    hechos = memoria.recordar_todo()
    resumen_habitos = habitos.resumen_para_perfil()
    if not hechos and not resumen_habitos:
        return  # nada de historial todavía, no vale la pena gastar una llamada

    entrada = "Hechos guardados sobre el usuario:\n" + ("\n".join(f"- {h}" for h in hechos) or "(ninguno todavía)")
    entrada += "\n\nPatrones de uso (qué tanto y cuándo usa cada tipo de comando):\n" + (resumen_habitos or "(ninguno todavía)")

    try:
        cliente = _obtener_cliente()
        respuesta = cliente.messages.create(
            model=config.MODELO_CLAUDE,
            max_tokens=300,
            system=(
                "A partir de estos datos sobre un usuario, escribe un perfil de "
                "personalidad/estilo de 3 a 5 oraciones en español, en tercera persona, "
                "que le sirva a un asistente de IA para adaptar su tono y sus sugerencias "
                "en conversaciones futuras. Sé concreto y evita generalidades vacías -si "
                "los datos son pocos, di un perfil corto y modesto en vez de inventar. "
                "Responde solo con el perfil, sin preámbulo."
            ),
            messages=[{"role": "user", "content": entrada}],
        )
        texto = "".join(b.text for b in respuesta.content if b.type == "text").strip()
        if texto:
            perfil.guardar_perfil(texto)
    except Exception:
        pass  # si falla, simplemente se reintenta en el próximo ciclo
