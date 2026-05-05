"""TiendaPro Lite — Hito M1.

Primer script del proyecto integrador. Lee el catálogo desde un archivo JSON,
filtra los productos disponibles, los ordena por precio ascendente, los
imprime en una tabla y muestra un resumen del inventario.

Ejecuta con:

    uv run python main.py

Este archivo es la **implementación de referencia**. Si estás haciendo el
ejercicio del hito M1 de S05, no lo mires hasta tener tu propia solución
funcionando.
"""

import json
from pathlib import Path

RUTA_CATALOGO = Path(__file__).parent / "data" / "catalogo.json"


def cargar_catalogo(ruta_archivo):
    """Lee el JSON de productos y devuelve la lista de dicts."""
    contenido = Path(ruta_archivo).read_text(encoding="utf-8")
    return json.loads(contenido)


def filtrar_disponibles(catalogo):
    """Devuelve nueva lista solo con productos con stock > 0."""
    return [p for p in catalogo if p["stock"] > 0]


def ordenar_por_precio(catalogo):
    """Devuelve nueva lista ordenada por precio ascendente."""
    return sorted(catalogo, key=lambda p: p["precio"])


def imprimir_tabla(catalogo):
    """Imprime el catálogo formateado como tabla."""
    print(f"{'Nombre':<28} {'Categoría':<14} {'Precio':>10} {'Stock':>8}")
    print("-" * 62)
    for p in catalogo:
        print(
            f"{p['nombre']:<28} {p['categoria']:<14} "
            f"${p['precio']:>9.2f} {p['stock']:>8}"
        )


def calcular_resumen(catalogo):
    """Calcula y devuelve un dict con los datos resumen del catálogo.

    Retorna un dict con:
        - total: cantidad de productos
        - mas_barato: dict del producto más barato
        - mas_caro: dict del producto más caro
        - valor_inventario: suma de precio*stock de todos los productos
    """
    if not catalogo:
        return {
            "total": 0,
            "mas_barato": None,
            "mas_caro": None,
            "valor_inventario": 0.0,
        }

    return {
        "total": len(catalogo),
        "mas_barato": min(catalogo, key=lambda p: p["precio"]),
        "mas_caro": max(catalogo, key=lambda p: p["precio"]),
        "valor_inventario": sum(p["precio"] * p["stock"] for p in catalogo),
    }


def imprimir_resumen(resumen):
    """Imprime el resumen del catálogo."""
    print("\nResumen")
    print("-" * 62)
    print(f"Productos disponibles:    {resumen['total']}")

    if resumen["mas_barato"]:
        mb = resumen["mas_barato"]
        print(f"Más barato:               {mb['nombre']} (${mb['precio']:.2f})")

    if resumen["mas_caro"]:
        mc = resumen["mas_caro"]
        print(f"Más caro:                 {mc['nombre']} (${mc['precio']:.2f})")

    print(f"Valor total inventario:   ${resumen['valor_inventario']:,.2f}")


def main():
    """Orquesta la carga, filtrado, ordenamiento e impresión del catálogo."""
    catalogo = cargar_catalogo(RUTA_CATALOGO)
    disponibles = filtrar_disponibles(catalogo)
    ordenado = ordenar_por_precio(disponibles)

    imprimir_tabla(ordenado)
    imprimir_resumen(calcular_resumen(ordenado))


if __name__ == "__main__":
    main()
