# J.A.R.V.I.S. — Documentación del agente

## ¿Qué es?

Un asistente personal que corre como programa de Python directo en tu
computadora con Windows, pensado para quedarse encendido todo el día.
A diferencia de una app web, sí puede abrir programas reales de tu
compu, porque no vive dentro de un navegador con restricciones — vive
en el propio sistema operativo.

## Cómo funciona (arquitectura)

Desde esta actualización, TODO corre en un solo proceso de Python, sin
terminal negra: `app_desktop.py` es el punto de arranque único, y abre
una ventana de escritorio limpia (PyWebView) con el núcleo animado de
Azmuth en vez de una consola.

```
app_desktop.py  → ARRANQUE ÚNICO. Levanta, todo en el mismo proceso:
                   el servidor web, el túnel de Ngrok, el motor de voz
                   y la ventana de escritorio con la interfaz gráfica.
servidor.py     → servidor FastAPI único: sirve azmuth.html (la
                   interfaz), el endpoint /estado (para animar el
                   núcleo) y /comando (para el control remoto vía
                   Ngrok — reloj, celular, etc).
main.py         → escucha el micrófono todo el tiempo, esperando la
                   palabra clave. Cuando la oye, captura tu comando.
                   Ya no abre su propio servidor (antes duplicaba uno
                   en Flask) — usa el mismo de servidor.py.
estado.py       → el "puente" entre la voz y la interfaz: guarda si
                   Azmuth está en reposo, escuchando, procesando o
                   ejecutando una orden, y la consola visual (el
                   reemplazo de la terminal negra).
skills/         → "habilidades" que resuelven comandos al instante,
                   sin usar la IA (hora, notas, abrir apps, multimedia,
                   pestañas, etc.)
cerebro.py      → si ninguna skill supo resolverlo, se lo pregunta a
                   Claude (Anthropic) y trae una respuesta conversacional.
voice.py        → convierte cualquier respuesta en voz, usando
                   ElevenLabs; si falla, usa la voz de Windows de reserva.
config.py       → carga tus claves de API y ajustes desde el .env.
azmuth.html     → la interfaz gráfica: el núcleo animado que cambia de
                   color y velocidad según el estado, y la consola
                   visual que reemplaza a la terminal negra.
datos/          → aquí se guardan tus notas, recordatorios y el log de
                   arranque (archivos locales en tu propia compu).
```

### El núcleo animado (estados visuales)

La interfaz consulta `/estado` dos veces por segundo y cambia el color
y la velocidad del núcleo según lo que Azmuth esté haciendo:

| Estado | Cuándo aparece | Color |
|---|---|---|
| **En espera** | Esperando la palabra clave | Verde/naranja (ambiental) |
| **Escuchando** | Capturando tu orden por el micrófono | Cian |
| **Procesando** | Interpretando el comando (skill o Claude) | Morado |
| **Ejecutando orden** | Realizando la acción / hablando la respuesta | Naranja/rojo |

Si algo se traba a medio camino, el núcleo vuelve solo a "En espera"
después de unos segundos — nunca se queda animando algo que ya terminó.

## Cómo debe completar tareas

Cuando le dices un comando, JARVIS sigue este orden:

1. **Primero intenta resolverlo con una skill local** (instantáneo,
   gratis, no necesita la IA). Por ejemplo "qué hora es" o "abre
   calculadora".
2. **Si ninguna skill aplica**, se lo manda a Claude para que conteste
   como conversación normal.
3. **Nunca debe inventar que hizo algo que no hizo.** Si le pides algo
   que ninguna skill sabe ejecutar todavía, debe decírtelo claramente
   y sugerirte la frase exacta que sí funciona, en vez de fingir.

## Palabra de activación

Por defecto: **"hora de ser héroe"**. La puedes cambiar en tu archivo
`.env`, en la línea `PALABRA_CLAVE`.

Mientras el programa esté corriendo con la ventana abierta, di la
palabra clave seguida de tu comando, por ejemplo:

> "Hora de ser héroe, abre YouTube y busca música para estudiar"

Si solo dices la palabra clave sola, JARVIS te contesta "Dígame" y
espera tu siguiente frase.

## Comandos que ya entiende

| Categoría | Ejemplo de frase |
|---|---|
| Hora / fecha | "qué hora es", "qué fecha es" |
| Notas | "toma nota: comprar café", "mis notas" |
| Recordatorios | "recuérdame llamar al doctor", "mis recordatorios" |
| Abrir apps | "abre calculadora", "abre bloc de notas", "abre edge" |
| YouTube | "abre youtube y busca [tema]" |
| Buscar en Google | "busca [algo]" |
| Mapas | "llévame a [lugar]" |
| WhatsApp | "mándale un whatsapp al [número] que diga [mensaje]" |
| Messenger | "abre messenger" (tú buscas el contacto y mandas el mensaje) |
| Reiniciar memoria | "borra el historial" |
| Cualquier otra cosa | Se lo pregunta a Claude directamente |

## Cómo agregar una skill nueva

1. Crea un archivo en `skills/`, por ejemplo `skills/musica.py`.
2. Dale una función con esta forma exacta:
   ```python
   def intentar(texto: str):
       if "tu condición" in texto.lower():
           return "Tu respuesta aquí"
       return None
   ```
3. Ábrelo en `skills/__init__.py`, impórtalo y agrégalo a la lista `SKILLS`.

Eso es todo — no hay que tocar `main.py` ni ningún otro archivo.

## Límites honestos (para que no te lleves sorpresas)

- No puede buscar un contacto por nombre y mandarle un mensaje sin que
  tú lo confirmes — ninguna app permite eso desde fuera, por privacidad.
- No pone alarmas ni notificaciones nativas de Windows todavía — solo
  guarda y recita recordatorios cuando se los pides.
- Solo escucha mientras la ventana de escritorio de Azmuth está
  abierta. Si la cierras, se apaga todo el sistema (voz, servidor y
  túnel de Ngrok incluidos).
- La calidad de reconocimiento de voz depende de tu micrófono y del
  ruido ambiente.

## Instalación (Windows)

### 1. Instalar Python
Si no lo tienes, descárgalo de [python.org](https://www.python.org/downloads/)
(marca la casilla "Add Python to PATH" durante la instalación).

### 2. Instalar las dependencias
Abre PowerShell o CMD dentro de la carpeta del proyecto y corre:
```
pip install -r requirements.txt
```
Si `pyaudio` da error al instalar, prueba:
```
pip install pipwin
pipwin install pyaudio
```

### 3. Conseguir tu clave de Anthropic (para que hable con la IA)
1. Ve a **console.anthropic.com** y crea una cuenta (con correo o Google).
2. Agrega un método de pago en **Settings → Billing** (la API se cobra
   por uso, no es gratis como claude.ai — pero los mensajes de un
   asistente personal cuestan centavos).
3. Ve a **Settings → API Keys → Create Key**, dale un nombre y cópiala
   de inmediato — solo la muestran una vez.

### 4. Conseguir tu clave de ElevenLabs (para la voz)
1. Ve a **elevenlabs.io** y crea una cuenta (tienen plan gratis con un
   límite de caracteres al mes, suficiente para probar).
2. En tu perfil, busca la sección de **API Keys** y genera una.
3. Elige una voz en su biblioteca de voces y copia su **Voice ID**
   (aparece en los detalles de cada voz).

### 5. Configurar tus claves
Copia el archivo `.env.example` y renómbralo a `.env`. Ábrelo con el
Bloc de notas y pega tus claves reales donde dice
`tu_clave_de_anthropic_aqui` y `tu_clave_de_elevenlabs_aqui`.

### 6. (Opcional) Conseguir tu token de Ngrok — para control remoto
Si quieres seguir controlando Azmuth desde tu reloj o celular aunque no
estés en la misma red Wi-Fi:
1. Ve a **dashboard.ngrok.com**, crea una cuenta y copia tu **Authtoken**
   (Setup & Installation → Your Authtoken).
2. Pégalo en tu `.env`, en `NGROK_AUTHTOKEN`.
3. (Opcional) Si quieres una URL fija que no cambie cada vez que
   arrancas, reserva un dominio gratis en **Domains → New Domain** y
   pégalo en `NGROK_DOMINIO`.
4. Si dejas `NGROK_AUTHTOKEN` vacío, Azmuth arranca igual, solo que sin
   control remoto (nada más funciona en tu propia compu).

### 7. Arrancarlo

**Modo normal (interfaz gráfica, sin terminal):**
```
python app_desktop.py
```
Se abre la ventana de escritorio con el núcleo animado. El servidor,
el túnel de Ngrok y la voz arrancan solos en segundo plano.

**Modo desarrollador (con consola, para depurar):**
```
python main.py
```
Útil para ver en vivo qué entendió el micrófono (`DEBUG — Escuché: ...`).

### 8. Que arranque solo al prender la compu, sin ninguna ventana negra
1. Copia toda esta carpeta (`jarvis-agent`) dentro de otra carpeta, por
   ejemplo `asistente\jarvis-agent`.
2. Ajusta la ruta dentro de `iniciar_azmuth.bat` si tu carpeta no se
   llama igual.
3. Abre `lanzador_oculto.vbs` con un editor de texto y corrige la ruta
   a tu `iniciar_azmuth.bat` real.
4. Crea un acceso directo a `lanzador_oculto.vbs` y colócalo en la
   carpeta de inicio de Windows: `Win + R` → escribe `shell:startup` →
   Enter → pega el acceso directo ahí.

Desde el próximo reinicio, Azmuth arranca solo, invisible, y directo a
la ventana de escritorio con el núcleo animado — nunca una terminal.
