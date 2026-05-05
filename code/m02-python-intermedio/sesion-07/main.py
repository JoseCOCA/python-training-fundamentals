"""Demo de S07 — Manejo de errores en cinco escenarios.

Ejecuta con:
    uv run python main.py
"""

from catalogo import obtener_precio
from errores import CatalogoError, ProductoIncompleto, ProductoNoEncontrado


def seccion(titulo: str) -> None:
    print()
    print("=" * 60)
    print(titulo)
    print("=" * 60)


CATALOGO = {
    "A001": {"nombre": "Auriculares", "precio": 89.99},
    "A002": {"nombre": "Cable USB"},                     # falta precio
    "A003": {"nombre": "Cargador", "precio": "doce"},    # precio inválido
}


def demo_caso_feliz() -> None:
    seccion("1. Caso feliz")
    precio = obtener_precio(CATALOGO, "A001")
    print(f"Precio de A001: ${precio:.2f}")


def demo_no_encontrado() -> None:
    seccion("2. SKU no existe")
    try:
        obtener_precio(CATALOGO, "Z999")
    except ProductoNoEncontrado as e:
        print(f"Captura específica: {e}")


def demo_incompleto_falta_precio() -> None:
    seccion("3. Producto sin precio")
    try:
        obtener_precio(CATALOGO, "A002")
    except ProductoIncompleto as e:
        print(f"Captura específica: {e}")


def demo_incompleto_precio_invalido() -> None:
    seccion("4. Precio no numérico")
    try:
        obtener_precio(CATALOGO, "A003")
    except ProductoIncompleto as e:
        print(f"Captura específica: {e}")


def demo_captura_base() -> None:
    seccion("5. Captura por base del dominio (atrapa cualquiera)")
    for sku in ("A001", "Z999", "A002", "A003"):
        try:
            precio = obtener_precio(CATALOGO, sku)
            print(f"{sku}: ${precio:.2f}")
        except CatalogoError as e:
            print(f"{sku}: error -> {type(e).__name__}: {e}")


def demo_raise_from_traceback() -> None:
    seccion("6. raise from preserva el traceback original")
    print("Forzamos un error para mostrar el encadenamiento. Mira el traceback:")
    obtener_precio(CATALOGO, "Z999")    # se propaga sin capturar


if __name__ == "__main__":
    demo_caso_feliz()
    demo_no_encontrado()
    demo_incompleto_falta_precio()
    demo_incompleto_precio_invalido()
    demo_captura_base()
    # La última demo deja el programa con código de error 1; coméntala si quieres
    # ver solo las cinco anteriores.
    demo_raise_from_traceback()
