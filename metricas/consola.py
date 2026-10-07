"""
consola.py — Muestra los reportes Markdown en la terminal con formato:
tablas con bordes y columnas alineadas, títulos y negritas (librería rich).
Si rich no está instalado, imprime el Markdown tal cual.
"""


def mostrar(markdown_texto: str):
    try:
        from rich.console import Console
        from rich.markdown import Markdown
    except ImportError:
        print(markdown_texto)
        return
    Console().print(Markdown(markdown_texto, code_theme="monokai"))
