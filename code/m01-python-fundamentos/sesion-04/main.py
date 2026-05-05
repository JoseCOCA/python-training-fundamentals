"""Demo de S04 — Funciones, scope y argumentos.

Ejecuta con:

    uv run python main.py
"""

# ============================================================
# 1. Función básica con un argumento
# ============================================================


def saludar(nombre):
    """Devuelve un saludo personalizado."""
    return f"Hola, {nombre}!"


print("=== 1. Función básica ===")
print(saludar("Carolina"))
print(saludar("Marco"))


# ============================================================
# 2. Múltiples argumentos y retornos
# ============================================================


def calcular_subtotal_y_descuento(precio, cantidad, descuento):
    """Calcula subtotal y descuento total, devuelve tupla."""
    subtotal = precio * cantidad
    descuento_total = subtotal * descuento
    return subtotal, descuento_total


print("\n=== 2. Múltiples retornos vía tupla ===")
sub, desc = calcular_subtotal_y_descuento(89.99, 3, 0.15)
print(f"Subtotal: ${sub:.2f}, descuento: ${desc:.2f}")


# ============================================================
# 3. Argumentos por nombre y defaults
# ============================================================


def crear_producto(nombre, precio, stock=0, categoria="general", disponible=True):
    """Crea un dict con los datos del producto."""
    return {
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "categoria": categoria,
        "disponible": disponible,
    }


print("\n=== 3. Defaults y por nombre ===")
print(crear_producto("auriculares", 89.99))
print(crear_producto("teclado", 49.50, stock=12, categoria="computación"))
print(crear_producto("monitor", 320.0, disponible=False))


# ============================================================
# 4. El gotcha de mutable default — versión MALA y BUENA
# ============================================================


def mala(item, lista=[]):
    """❌ Default mutable: la lista se comparte entre llamadas."""
    lista.append(item)
    return lista


def buena(item, lista=None):
    """✅ Patrón correcto: None como sentinel + crear adentro."""
    if lista is None:
        lista = []
    lista.append(item)
    return lista


print("\n=== 4. Mutable default gotcha ===")
print("❌ Mala (la lista 'recuerda' entre llamadas):")
print(f"  {mala('a')}")
print(f"  {mala('b')}")
print(f"  {mala('c')}")

print("✅ Buena (cada llamada empieza limpia):")
print(f"  {buena('a')}")
print(f"  {buena('b')}")
print(f"  {buena('c')}")


# ============================================================
# 5. *args y **kwargs
# ============================================================


def promedio(*numeros):
    """Promedio de un número variable de argumentos."""
    if not numeros:
        return 0.0
    return sum(numeros) / len(numeros)


def producto_flexible(nombre, **extras):
    """Crea producto con campos extra arbitrarios."""
    return {"nombre": nombre, **extras}


print("\n=== 5. *args y **kwargs ===")
print(f"promedio(10, 20, 30) = {promedio(10, 20, 30)}")
print(f"promedio() = {promedio()}")
print(producto_flexible("auriculares", precio=89.99, color="negro", peso=0.3))


# ============================================================
# 6. Scope y LEGB
# ============================================================

mensaje = "global"


def fuera():
    mensaje = "enclosing"

    def dentro():
        mensaje = "local"
        print(f"  dentro ve: {mensaje}")

    dentro()
    print(f"  fuera ve: {mensaje}")


print("\n=== 6. Scope LEGB ===")
fuera()
print(f"  módulo ve: {mensaje}")


# ============================================================
# 7. Pura vs efecto secundario
# ============================================================


def aplicar_descuento_puro(producto, porcentaje):
    """Devuelve una COPIA con descuento. No modifica el original."""
    nuevo = producto.copy()
    nuevo["precio"] = producto["precio"] * (1 - porcentaje)
    return nuevo


def aplicar_descuento_impuro(producto, porcentaje):
    """Modifica el producto IN-PLACE. Efecto secundario."""
    producto["precio"] = producto["precio"] * (1 - porcentaje)


print("\n=== 7. Pura vs efecto secundario ===")
original = {"nombre": "auriculares", "precio": 100.0}

con_descuento = aplicar_descuento_puro(original, 0.10)
print(f"Pura: original = {original}")
print(f"      copia con descuento = {con_descuento}")

aplicar_descuento_impuro(original, 0.10)
print(f"Impura: original modificado = {original}  ← ¡cambió el original!")
