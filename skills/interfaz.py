"""
Puente entre el motor de voz (main.py) y la ventana gráfica (app_desktop.py).

¿Por qué existe este archivo? Porque main.py corre en un hilo de fondo y no
debería tener que saber nada sobre pywebview. En vez de eso, llama a
interfaz.estado(...) e interfaz.log(...), y este módulo se encarga de
mandarlo a la ventana si es que ya existe una conectada.

app_desktop.py llama a conectar(window) una sola vez, justo después de
crear la ventana. Si Azmuth corre sin ventana (por ejemplo con
python main.py directo, como antes), ventana se queda en None y estas
funciones simplemente no hacen nada — main.py sigue funcionando igual.
"""

ventana = None


def conectar(window):
    """Llamado una sola vez desde app_desktop.py, en cuanto la ventana existe."""
    global ventana
    ventana = window


def estado(nombre: str):
    """
    Cambia el estado visual del núcleo en la ventana.
    Valores esperados: 'inactivo', 'escuchando', 'pensando', 'ejecutando'.
    """
    if ventana is None:
        return
    try:
        ventana.evaluate_js(f"cambiarEstado('{nombre}')")
    except Exception as e:
        print(f"[interfaz] No pude actualizar el estado: {e}")


def log(texto: str):
    """Agrega una línea a la consola visual dentro de la ventana."""
    if ventana is None:
        return
    texto_seguro = (
        texto.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", " ")
    )
    try:
        ventana.evaluate_js(f"agregarLog('{texto_seguro}')")
    except Exception as e:
        print(f"[interfaz] No pude actualizar el log: {e}")