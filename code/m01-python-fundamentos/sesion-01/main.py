"""Demo de S01 — Variables, tipos primitivos y expresiones.

Ejecuta este script con:

    uv run python main.py

El script no pide input — solo demuestra los conceptos de la sesión imprimiendo
resultados. Después de leerlo, modifícalo: cambia valores, agrega expresiones,
rómpelo intencionalmente y observa los errores.
"""

# ============================================================
# 1. Variables y tipos primitivos
# ============================================================

nombre_producto = "Auriculares Bluetooth"
precio_unitario = 89.99
cantidad_disponible = 12
es_promocion = True
descuento_aplicado = None  # todavía no se asignó

print("=== Datos del producto ===")
print(f"Nombre:    {nombre_producto}      (tipo: {type(nombre_producto).__name__})")
print(f"Precio:    {precio_unitario}      (tipo: {type(precio_unitario).__name__})")
print(f"Stock:     {cantidad_disponible}  (tipo: {type(cantidad_disponible).__name__})")
print(f"Promo:     {es_promocion}         (tipo: {type(es_promocion).__name__})")
print(f"Descuento: {descuento_aplicado}   (tipo: {type(descuento_aplicado).__name__})")

# ============================================================
# 2. Operadores aritméticos
# ============================================================

print("\n=== Cálculo de subtotal y descuento ===")
unidades_a_comprar = 3
subtotal = precio_unitario * unidades_a_comprar
descuento_porcentaje = 0.15
descuento_total = subtotal * descuento_porcentaje
total_final = subtotal - descuento_total

print(f"Subtotal:  ${subtotal:.2f}")
print(f"Descuento: -${descuento_total:.2f} ({descuento_porcentaje * 100:.0f}%)")
print(f"Total:     ${total_final:.2f}")

# ============================================================
# 3. Conversión de tipos
# ============================================================

print("\n=== Conversiones ===")
precio_como_str = "29.99"
precio_como_float = float(precio_como_str)
print(f"'{precio_como_str}' (str) → {precio_como_float} ({type(precio_como_float).__name__})")

# Cuidado: int() trunca, no redondea
print(f"int(19.99) = {int(19.99)}  ← truncado, no redondeado")

# ============================================================
# 4. Comparaciones y booleanos
# ============================================================

print("\n=== Comparaciones ===")
hay_stock = cantidad_disponible > 0
es_caro = precio_unitario > 100

print(f"¿Hay stock? {hay_stock}")
print(f"¿Es caro?   {es_caro}")
print(f"Promo Y hay stock: {es_promocion and hay_stock}")
print(f"Promo O es caro:   {es_promocion or es_caro}")

# ============================================================
# 5. La trampa del float (gotcha clásico)
# ============================================================

print("\n=== Precisión de float ===")
suma = 0.1 + 0.2
print(f"0.1 + 0.2 = {suma}        ← no es 0.3 exacto")
print(f"0.1 + 0.2 == 0.3 → {suma == 0.3}")
print(f"abs(0.1 + 0.2 - 0.3) < 1e-9 → {abs(suma - 0.3) < 1e-9}  ← forma correcta de comparar")
