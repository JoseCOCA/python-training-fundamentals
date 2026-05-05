"""Demo de S02 — Control de flujo: if, while, for y comprensiones.

Ejecuta con:

    uv run python main.py
"""

# ============================================================
# 1. if / elif / else
# ============================================================

print("=== 1. Categorización por precio ===")
precios = [10, 50, 120, 199, 350, 800]

for precio in precios:
    if precio < 50:
        categoria = "barato"
    elif precio < 200:
        categoria = "medio"
    elif precio < 500:
        categoria = "caro"
    else:
        categoria = "premium"
    print(f"${precio:>4} → {categoria}")

# ============================================================
# 2. Truthiness
# ============================================================

print("\n=== 2. Valores falsy ===")
ejemplos = [0, 0.0, "", None, False, [], "0", "False", 1]
for valor in ejemplos:
    veredicto = "truthy" if valor else "falsy"
    print(f"{valor!r:10} → {veredicto}")

# ============================================================
# 3. for con range, enumerate, zip
# ============================================================

print("\n=== 3. Iterar de tres formas ===")

productos = ["auriculares", "teclado", "monitor"]
precios = [89.99, 49.50, 320.00]

print("Con range:")
for i in range(len(productos)):
    print(f"  {i}: {productos[i]}")

print("Con enumerate (idiomático):")
for i, producto in enumerate(productos):
    print(f"  {i}: {producto}")

print("Con zip (combinando dos listas):")
for nombre, precio in zip(productos, precios):
    print(f"  {nombre} → ${precio}")

# ============================================================
# 4. break y continue
# ============================================================

print("\n=== 4. break / continue ===")
print("Solo pares, paramos al llegar a 8:")
for n in range(20):
    if n % 2 != 0:
        continue
    if n > 8:
        break
    print(f"  {n}")

# ============================================================
# 5. for/else — bucle que NO encontró
# ============================================================

print("\n=== 5. for/else (búsqueda) ===")
buscar = "tablet"
for p in productos:
    if p == buscar:
        print(f"  ¡{buscar} encontrado!")
        break
else:
    print(f"  {buscar} no está en el catálogo")

# ============================================================
# 6. Comprensiones
# ============================================================

print("\n=== 6. Comprensiones ===")
con_iva = [round(p * 1.21, 2) for p in precios]
print(f"  Con IVA: {con_iva}")

caros = [p for p in precios if p > 50]
print(f"  Caros (>$50): {caros}")

catalogo = {nombre: precio for nombre, precio in zip(productos, precios)}
print(f"  Catálogo (dict): {catalogo}")
