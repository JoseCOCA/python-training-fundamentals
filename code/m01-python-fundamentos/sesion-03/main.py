"""Demo de S03 — Estructuras de datos: list, tuple, dict, set.

Ejecuta con:

    uv run python main.py
"""

# ============================================================
# 1. list — mutable, ordenada
# ============================================================

print("=== 1. list ===")
productos = ["auriculares", "teclado", "monitor"]
print(f"Original: {productos}")

productos.append("ratón")
productos.insert(0, "tablet")
print(f"Después de append+insert: {productos}")

print(f"Primero: {productos[0]}, último: {productos[-1]}")
print(f"Slice [1:3]: {productos[1:3]}")

# Ordenar (in-place vs nuevo)
ordenado = sorted(productos)
print(f"sorted (nueva): {ordenado}")
print(f"Original sigue: {productos}")

# ============================================================
# 2. tuple — inmutable, ordenada
# ============================================================

print("\n=== 2. tuple ===")
producto = ("auriculares", 89.99, 5)
nombre, precio, stock = producto
print(f"Desempaquetada: nombre={nombre}, precio={precio}, stock={stock}")

try:
    producto[0] = "monitor"  # type: ignore[index]
except TypeError as e:
    print(f"Modificar tupla falla: {e}")

# ============================================================
# 3. dict — clave-valor, mutable
# ============================================================

print("\n=== 3. dict ===")
producto = {
    "nombre": "auriculares",
    "precio": 89.99,
    "stock": 5,
}
print(f"Producto: {producto}")
print(f"Nombre: {producto['nombre']}")

# Acceso seguro con .get()
descripcion = producto.get("descripcion", "(sin descripción)")
print(f"Descripción (con default): {descripcion}")

# Iterar
for clave, valor in producto.items():
    print(f"  {clave}: {valor}")

# ============================================================
# 4. set — sin duplicados, sin orden
# ============================================================

print("\n=== 4. set ===")
emails = ["a@x.com", "b@x.com", "a@x.com", "c@x.com", "b@x.com"]
unicos = set(emails)
print(f"Originales: {len(emails)} | Únicos: {len(unicos)} | Set: {unicos}")

premium = {"a@x.com", "b@x.com"}
activos = {"b@x.com", "c@x.com"}
print(f"Premium ∩ activos: {premium & activos}")
print(f"Premium ∪ activos: {premium | activos}")

# ============================================================
# 5. Mutabilidad — el gotcha clásico
# ============================================================

print("\n=== 5. Mutabilidad ===")
a = [1, 2, 3]
b = a              # ¡b apunta al MISMO objeto que a!
b.append(4)
print(f"a = {a}  (¡cambió porque b modificó el mismo objeto!)")
print(f"b = {b}")

# Forma correcta de copiar
c = a.copy()
c.append(5)
print(f"a = {a}  (no cambió esta vez)")
print(f"c = {c}")

# ============================================================
# 6. Catálogo: lista de dicts (preview del integrador)
# ============================================================

print("\n=== 6. Catálogo TiendaPro ===")
catalogo = [
    {"nombre": "auriculares", "precio": 89.99, "stock": 5},
    {"nombre": "teclado", "precio": 49.50, "stock": 12},
    {"nombre": "monitor", "precio": 320.00, "stock": 0},
    {"nombre": "ratón", "precio": 19.99, "stock": 30},
]

# Ordenar por precio ascendente
por_precio = sorted(catalogo, key=lambda p: p["precio"])
print("Por precio ascendente:")
for p in por_precio:
    print(f"  {p['nombre']:15} ${p['precio']:>7.2f}  stock: {p['stock']}")

# Filtrar solo con stock
en_stock = [p for p in catalogo if p["stock"] > 0]
print(f"\nProductos con stock: {len(en_stock)} de {len(catalogo)}")
