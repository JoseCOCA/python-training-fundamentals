"""Punto de entrada de la demo de S06.

Ejecuta con:
    uv run python main.py

Este archivo demuestra:
- Importar un módulo simple (`saludador`).
- Importar funciones desde un paquete (`tienda`).
- Usar el guard `if __name__ == "__main__"`.
- Imprimir `sys.path` para entender dónde busca Python los módulos.
"""

import sys

import saludador
from tienda import crear, listar
from tienda.productos import imprimir_tabla


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


def demo_imports() -> None:
    seccion("1. Import de módulo simple (saludador)")
    print(f"saludador.PI = {saludador.PI}")
    print(saludador.saludar("Equipo M2"))

    seccion("2. Import desde un paquete (tienda)")
    productos = listar()
    print("Productos disponibles, ordenados por precio:")
    imprimir_tabla(productos)

    print()
    print("Crear clientes:")
    print(crear("Ana", "ana@example.com"))
    print(crear("Bruno", "bruno@example.com"))


def demo_dunder_name() -> None:
    seccion("3. ¿Qué vale __name__ aquí?")
    print(f"En main.py, __name__ = {__name__!r}")
    print("Cuando se ejecuta directamente, vale '__main__'.")
    print("Si fuera importado desde otro archivo, valdría 'main'.")


def demo_sys_path() -> None:
    seccion("4. sys.path — dónde busca Python los módulos")
    for i, ruta in enumerate(sys.path):
        marca = " <- vacío = directorio actual" if ruta == "" else ""
        print(f"  [{i}] {ruta!r}{marca}")


if __name__ == "__main__":
    demo_imports()
    demo_dunder_name()
    demo_sys_path()
