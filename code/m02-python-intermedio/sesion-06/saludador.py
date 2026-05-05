"""Módulo simple — demuestra qué hace `if __name__ == "__main__"`.

Si ejecutas este archivo directamente:
    uv run python saludador.py
verás el saludo de demostración.

Si lo importas desde otro archivo (`import saludador`), el saludo NO
se ejecuta — solo quedan disponibles las funciones.
"""

PI = 3.1416


def saludar(nombre: str) -> str:
    return f"Hola, {nombre}"


def despedir(nombre: str) -> str:
    return f"Adiós, {nombre}"


if __name__ == "__main__":
    print("Ejecutando saludador.py directamente.")
    print(f"__name__ vale: {__name__!r}")
    print(saludar("Mundo"))
    print(despedir("Mundo"))
