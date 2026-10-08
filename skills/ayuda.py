"""
Skill: ayuda — lista los comandos exactos que Azmuth reconoce de verdad,
tomados directo de las expresiones que cada skill acepta (no genéricos).
"""
import re

import estado


_PIDE_AYUDA = re.compile(
    r"^(?:azmuth\s+)?(?:"
    r"ayuda|ay[uú]dame|manual|(?:el\s+)?manual de uso|opciones|"
    r"(?:dime\s+|cu[aá]les\s+son\s+|mu[eé]strame\s+)?(?:tus\s+|los\s+|mis\s+)?comandos|"
    r"qu[eé]\s+(?:puedes|sabes)\s+hacer|qu[eé]\s+haces"
    r")$"
)


# En modo voz se dice un resumen corto (leer todo en voz alta tardaría minutos);
# en modo escritorio se muestra el manual completo en Markdown.
RESUMEN_VOZ = (
    "Puedo ayudarle con: notas, recordatorios con aviso en Windows, memoria, hábitos, "
    "hora, fecha y clima, búsquedas, mapas y WhatsApp, contactos, música y volumen, "
    "pestañas y ventanas, abrir o cerrar cualquier aplicación que tenga instalada, "
    "y ver lo que hay en su pantalla para ayudarle. Lo que no sea un comando se lo contesto "
    "con inteligencia artificial. Para ver todos los ejemplos diga modo escritorio y escriba ayuda."
)

MANUAL = """## 🟢 Lo que puedo hacer

Háblame con la palabra clave o escríbeme en este chat. **Lo que no sea un comando lo contesta Claude** con el historial del chat.

### 🖥️ Pantalla (nuevo)
- «qué hay en mi pantalla» · «ayúdame con lo que hay en mi pantalla»
- «mira mi pantalla y dime qué error tiene» · «traduce lo que dice mi pantalla» · «resuelve lo de mi pantalla»
- *Toma una captura, Claude la analiza y no se guarda.*

### 🚀 Aplicaciones
- «abre Discord», «abre PowerPoint», «abre Steam»: **cualquier app instalada**, aunque no la conozca
- «cierra Spotify» · «cuando diga juego abre Fortnite» (le enseña un apodo)
- «qué aplicaciones aprendiste» · «actualiza tus aplicaciones»
- «abre youtube y busca lofi» · «abre messenger»

### ⏰ Recordatorios (con notificación de Windows)
- «recuérdame hablar con Jesús a la 1» · «recuérdame comprar pan» (sin hora)
- «recuérdame hacer ejercicio todos los días a las 7» · «… los martes y jueves a las 9»
- «mis recordatorios» · «borra el recordatorio de Jesús» · «borra todos los recordatorios»

### 📝 Notas y memoria
- «toma nota: comprar café» · «mis notas»
- «recuerda que mi proyecto se llama Chispa» · «qué recuerdas de mi proyecto» · «qué sabes»
- «olvídate de mi proyecto» · «olvida todo lo que recuerdas»

### 🌐 Búsquedas, mapas y mensajes
- «busca gatos» · «llévame a Plaza Sendero»
- «mándale un whatsapp a Jesús que diga voy en camino» · «abre whatsapp con Jesús»
- Contactos: «guarda el contacto de Jesús como 5512345678» · «mis contactos» · «borra el contacto de Jesús»

### 🎵 Música y volumen
- «pon mi playlist» · «menea la chapa» · «pausa» · «siguiente» · «anterior»
- «volumen a 50» · «sube el volumen» · «baja el volumen» · «silencia»

### 🗂️ Pestañas y ventanas
- «nueva pestaña» · «cierra pestaña» · «siguiente pestaña» · «pestaña anterior» · «pestaña 3» · «cambia de ventana»

### 🕒 Hora, clima y hábitos
- «qué hora es» · «qué fecha es» · «qué clima hace»
- «mis hábitos» (también le sugiero cosas si noto un patrón)

### 🔁 Modos y sistema
- «modo escritorio» / «modo voz» (o el botón de la ventana)
- «borra el historial» · «apágate»

### ⌚ Control desde el celular o el reloj
- Abra **/reloj** con su token: 26 acciones (multimedia, volumen, juegos, sistema, herramientas y pestañas)."""


def intentar(texto: str):
    t = texto.lower().strip()

    # DEF-011: antes bastaba con que la frase CONTUVIERA "manual" u "opciones"
    # en cualquier parte ("abre youtube y busca manual de guitarra" mostraba la
    # ayuda). Ahora la frase completa tiene que ser una petición de ayuda.
    t = re.sub(r"[¿?¡!.,]", "", t).strip()
    if _PIDE_AYUDA.match(t):
        if estado.obtener_modo() == "escritorio":
            return MANUAL
        return RESUMEN_VOZ

    return None
