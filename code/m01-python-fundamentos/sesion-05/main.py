"""Demo de S05 — Strings y manipulación de texto.

Ejecuta con:

    uv run python main.py
"""

# ============================================================
# 1. Indexing y slicing
# ============================================================

print("=== 1. Indexing y slicing ===")
saludo = "Hola, Mundo Python!"
print(f"Primer carácter: {saludo[0]}")
print(f"Último carácter:  {saludo[-1]}")
print(f"Primeros 4:       {saludo[:4]}")
print(f"Desde el 6 al 11: {saludo[6:11]}")
print(f"Al revés:         {saludo[::-1]}")

# ============================================================
# 2. f-strings con format specifiers
# ============================================================

print("\n=== 2. f-strings ===")
nombre = "Carolina"
edad = 28
saldo = 1234567.891
porcentaje = 0.1525

print(f"Nombre:                {nombre}")
print(f"Mayúsculas:            {nombre.upper()}")
print(f"Edad el año que viene: {edad + 1}")
print(f"Saldo formateado:      ${saldo:,.2f}")
print(f"Descuento:             {porcentaje:.1%}")
print(f"|{nombre:<15}| alineado izquierda")
print(f"|{nombre:>15}| alineado derecha")
print(f"|{nombre:^15}| centrado")

# ============================================================
# 3. Métodos esenciales
# ============================================================

print("\n=== 3. Métodos esenciales ===")
texto = "  Hola, Mundo Python!  "
print(f"strip:        {texto.strip()!r}")
print(f"lower:        {texto.strip().lower()!r}")
print(f"upper:        {texto.strip().upper()!r}")
print(f"replace:      {texto.strip().replace('Mundo', 'AI Engineer')!r}")
print(f"split por ,:  {texto.strip().split(',')}")
print(f"split sin sep: {texto.strip().split()}")
print(f"join:         {'-'.join(['hola', 'mundo', 'python'])!r}")
print(f"startswith:   {texto.strip().startswith('Hola')}")
print(f"find:         {texto.strip().find('Mundo')}")

# ============================================================
# 4. Parseo de líneas (catálogo)
# ============================================================

print("\n=== 4. Parseo de catálogo ===")
lineas = [
    "Auriculares Bluetooth | $89.99 | stock: 5",
    "Teclado Mecánico      | $49.50 | stock: 12",
    "Monitor 4K            | $320.00 | stock: 0",
]

productos = []
for linea in lineas:
    campos = [c.strip() for c in linea.split("|")]
    nombre = campos[0]
    precio = float(campos[1].replace("$", ""))
    stock = int(campos[2].replace("stock:", "").strip())
    productos.append({"nombre": nombre, "precio": precio, "stock": stock})

print(f"{'Nombre':25} {'Precio':>10} {'Stock':>8}")
print("-" * 45)
for p in productos:
    print(f"{p['nombre']:25} ${p['precio']:>9.2f} {p['stock']:>8}")

# ============================================================
# 5. Concatenación: join vs += en bucle
# ============================================================

print("\n=== 5. join vs += ===")
items = ["manzana", "pera", "uva", "kiwi"]

# Forma idiomática
print(", ".join(items))

# Forma anti-idiomática (no la uses)
resultado = ""
for item in items:
    resultado += item + ", "
print(f"con +=: {resultado}  ← coma sobrante al final")

# ============================================================
# 6. Encoding (UTF-8)
# ============================================================

print("\n=== 6. Encoding ===")
texto_con_acentos = "Atención: café con leche"
bytes_utf8 = texto_con_acentos.encode("utf-8")
print(f"Original:     {texto_con_acentos}")
print(f"En UTF-8:     {bytes_utf8}")
print(f"Decodificado: {bytes_utf8.decode('utf-8')}")
print(f"Bytes para 'café': {len('café')} caracteres, {len('café'.encode('utf-8'))} bytes")
