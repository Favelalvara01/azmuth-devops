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
import idioma
import tematicas
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

EXTRA_INGLES = """

LANGUAGE: the user switched AZMUTH to ENGLISH. Always answer in natural English \
(American), with the same personality, even if older messages in the history are in \
Spanish. Keep the [MEMORIA: ...] tag exactly as described, but write the fact itself in English. \
Unless you are told you are in DESKTOP MODE, do not use Markdown (no **bold**, lists or tables): \
your answer is read aloud."""

_RE_MEMORIA = re.compile(r"\[MEMORIA:\s*(.+?)\]", re.IGNORECASE)

_cliente = None
_historial = []


SIN_CLAVE = ("No tengo configurada ninguna clave de IA todavía. Ponga ANTHROPIC_API_KEY, "
             "GROQ_API_KEY o GEMINI_API_KEY (las dos últimas son gratis) en su archivo .env, por favor.")
SIN_VISION = ("Para ver la pantalla necesito una clave de Anthropic o de Gemini; "
              "Groq solo sirve para conversar. Agregue GEMINI_API_KEY (gratis) a su .env.")


def _tiene_imagen(mensajes) -> bool:
    return any(isinstance(m["content"], list) and any(b.get("type") == "image" for b in m["content"])
               for m in mensajes)


def proveedor(con_imagen: bool = False):
    """Qué IA usar: Claude si hay clave; si no, Groq (rápida) para texto y Gemini para
    imágenes o como respaldo. None si no hay ninguna clave que sirva."""
    if config.ANTHROPIC_API_KEY:
        return "claude"
    groq, gemini_ = getattr(config, "GROQ_API_KEY", ""), getattr(config, "GEMINI_API_KEY", "")
    if con_imagen:
        return "gemini" if gemini_ else None
    return "groq" if groq else ("gemini" if gemini_ else None)


def completar(system: str, mensajes: list, max_tokens: int) -> str:
    """Punto único para hablar con la IA (Claude, Groq o Gemini). Lanza excepción si falla."""
    con_imagen = _tiene_imagen(mensajes)
    elegido = proveedor(con_imagen)
    if elegido is None and con_imagen and proveedor():
        raise RuntimeError(SIN_VISION)
    if elegido == "groq":
        import groq_ia as groq
        try:
            return groq.completar(system, mensajes, max_tokens)
        except Exception:
            if not getattr(config, "GEMINI_API_KEY", ""):
                raise
        elegido = "gemini"  # Groq falló: se intenta con Gemini si hay clave
    if elegido == "gemini":
        import gemini
        return gemini.completar(system, mensajes, max_tokens)
    respuesta = _obtener_cliente().messages.create(
        model=config.MODELO_CLAUDE, max_tokens=max_tokens, system=system, messages=mensajes)
    return "".join(b.text for b in respuesta.content if b.type == "text").strip()


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

    prompt += tematicas.extra_prompt()
    if idioma.es_ingles():
        prompt += EXTRA_INGLES
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
    if not proveedor():
        return SIN_CLAVE

    usar_historial_voz = mensajes is None
    if usar_historial_voz:
        _historial.append({"role": "user", "content": texto_usuario})
        mensajes = _historial[-12:]

    system = _construir_system_prompt()
    if modo == "escritorio":
        system += EXTRA_ESCRITORIO

    try:
        texto = completar(system, mensajes, 2000 if modo == "escritorio" else 800)
        texto = _extraer_y_guardar_memoria(texto) if texto else texto
        texto = texto or "No logré generar una respuesta. ¿Puede intentarlo de nuevo?"
        if usar_historial_voz:
            _historial.append({"role": "assistant", "content": texto})
        return texto
    except Exception as e:
        return f"Tuve un problema conectando con mi cerebro: {e}"


def analizar_imagen(imagen_jpeg: bytes, pregunta: str, modo: str = "voz") -> str:
    """Visión: manda una imagen (ej. captura de pantalla) a Claude con la pregunta."""
    if not proveedor():
        return SIN_CLAVE
    if not proveedor(con_imagen=True):
        return SIN_VISION
    import base64
    system = _construir_system_prompt()
    if modo == "escritorio":
        system += EXTRA_ESCRITORIO
    else:
        system += ("\nEstás viendo una captura de la pantalla del usuario. Responde en máximo 3 "
                   "oraciones, sin Markdown, porque se va a decir en voz alta.")
    contenido = [
        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                     "data": base64.b64encode(imagen_jpeg).decode("ascii")}},
        {"type": "text", "text": pregunta},
    ]
    try:
        texto = completar(system, [{"role": "user", "content": contenido}], 1500 if modo == "escritorio" else 400)
        return texto or "No logré describir la pantalla."
    except Exception as e:
        return f"Tuve un problema analizando la pantalla: {e}"


_cache_traducciones = {}


def traducir(texto: str, a: str = "en") -> str:
    """Traduce una respuesta corta de una skill (ej. "Abriendo paint.") al idioma
    pedido. Si no hay clave o falla, regresa el texto original: nunca rompe el flujo."""
    if not texto or not proveedor():
        return texto
    clave = (texto, a)
    if clave in _cache_traducciones:
        return _cache_traducciones[clave]
    destino = "natural American English" if a == "en" else "español de México"
    try:
        traducido = completar(
            f"Translate the user's text into {destino}. It is a reply from a voice assistant. "
            "Keep names, numbers, URLs, emojis and line breaks. Output ONLY the translation.",
            [{"role": "user", "content": texto}], 600) or texto
    except Exception:
        return texto
    if len(_cache_traducciones) > 300:
        _cache_traducciones.clear()
    _cache_traducciones[clave] = traducido
    return traducido


def borrar_historial():
    global _historial
    _historial = []


def actualizar_perfil_si_toca():
    """Se llama en segundo plano (main.py) cada cierto tiempo. Si ya
    toca regenerar el perfil (ver skills/perfil.py) y hay suficiente
    historial acumulado, le pide a Claude que sintetice un perfil de
    personalidad/estilo corto a partir de la memoria y los hábitos."""
    if not proveedor() or not perfil.toca_actualizar():
        return

    hechos = memoria.recordar_todo()
    resumen_habitos = habitos.resumen_para_perfil()
    if not hechos and not resumen_habitos:
        return  # nada de historial todavía, no vale la pena gastar una llamada

    entrada = "Hechos guardados sobre el usuario:\n" + ("\n".join(f"- {h}" for h in hechos) or "(ninguno todavía)")
    entrada += "\n\nPatrones de uso (qué tanto y cuándo usa cada tipo de comando):\n" + (resumen_habitos or "(ninguno todavía)")

    try:
        texto = completar(
            (
                "A partir de estos datos sobre un usuario, escribe un perfil de "
                "personalidad/estilo de 3 a 5 oraciones en español, en tercera persona, "
                "que le sirva a un asistente de IA para adaptar su tono y sus sugerencias "
                "en conversaciones futuras. Sé concreto y evita generalidades vacías -si "
                "los datos son pocos, di un perfil corto y modesto en vez de inventar. "
                "Responde solo con el perfil, sin preámbulo."
            ),
            [{"role": "user", "content": entrada}], 300)
        if texto:
            perfil.guardar_perfil(texto)
    except Exception:
        pass  # si falla, simplemente se reintenta en el próximo ciclo
