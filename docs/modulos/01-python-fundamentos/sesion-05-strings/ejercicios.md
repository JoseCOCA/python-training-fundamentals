# S05 — Ejercicios

Práctica de strings + cierre del M1 con el primer hito del integrador.

---

## Ejercicio 1 — Indexar y slicear (5 min)

```python
saludo = "Hola, Mundo Python!"

# Predice ANTES de ejecutar:
print(saludo[0])              # ?
print(saludo[-1])             # ?
print(saludo[:4])             # ?
print(saludo[6:11])           # ?
print(saludo[::-1])           # ?
print(saludo[::2])            # ?  (¿qué hace ::2?)
print(len(saludo))            # ?
```

Después ejecuta y verifica.

---

## Ejercicio 2 — f-strings con format (10 min)

Crea `formato.py`:

```python
nombre = "Carolina"
edad = 28
saldo = 1234567.891
porcentaje = 0.1525

print(f"Nombre: {nombre}")
print(f"Nombre en mayúsculas: {nombre.upper()}")
print(f"Edad el año que viene: {edad + 1}")
print(f"Saldo: ${saldo:,.2f}")
print(f"Descuento aplicado: {porcentaje:.1%}")
print(f"|{nombre:<15}| alineado izquierda")
print(f"|{nombre:>15}| alineado derecha")
print(f"|{nombre:^15}| centrado")
```

Modifica los format specifiers — prueba `{saldo:.0f}`, `{saldo:e}`, `{nombre:*^20}`, etc.

---

## Ejercicio 3 — Métodos de string (10 min)

Para cada línea, predice la salida ANTES de ejecutar:

```python
texto = "  Hola, Mundo Python!  "

print(texto.strip())
print(texto.strip().lower())
print(texto.strip().replace("Mundo", "AI Engineer"))
print(texto.strip().split())
print(texto.strip().split(","))
print("-".join(["hola", "mundo", "python"]))
print(texto.strip().startswith("Hola"))
print(texto.strip().endswith("?"))
print("banana".count("a"))
print("python".find("th"))
```

---

## Ejercicio 4 — Parsear líneas de catálogo (15 min)

Crea `parsear.py`:

```python
lineas = [
    "Auriculares Bluetooth | $89.99 | stock: 5",
    "Teclado Mecánico      | $49.50 | stock: 12",
    "Monitor 4K            | $320.00 | stock: 0",
    "Ratón Inalámbrico     | $19.99 | stock: 30",
]

productos = []

for linea in lineas:
    campos = [c.strip() for c in linea.split("|")]
    nombre = campos[0]
    precio = float(campos[1].replace("$", ""))
    stock = int(campos[2].replace("stock:", "").strip())

    productos.append({
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
    })

# Imprimir todos los productos como tabla
print(f"{'Nombre':25} {'Precio':>10} {'Stock':>8}")
print("-" * 45)
for p in productos:
    print(f"{p['nombre']:25} ${p['precio']:>9.2f} {p['stock']:>8}")
```

**Modificación:** ordena los productos por precio descendente y solo imprime los que tienen `stock > 0`.

---

## Ejercicio 5 — Normalizar y comparar (10 min)

Cuando comparas strings que vienen de input, conviene normalizarlos. Escribe `normalizar.py`:

```python
def normalizar(texto):
    """Devuelve texto sin espacios al borde y en lowercase."""
    return texto.strip().lower()


candidatos = [
    "  AURICULARES  ",
    "auriculares",
    " Auriculares\n",
    "AuRiCuLaReS",
]

normalizados = [normalizar(c) for c in candidatos]

for original, normalizado in zip(candidatos, normalizados):
    print(f"{original!r:25} → {normalizado!r}")

# ¿Todos los normalizados son iguales?
print(f"Todos iguales: {len(set(normalizados)) == 1}")
```

---

## Ejercicio 6 — Construir un string con `join()` (5 min)

Convierte estos dos bloques al patrón `join()`:

```python
# Versión MALA — concatenación con +=
items = ["manzana", "pera", "uva", "kiwi"]
resultado = ""
for item in items:
    resultado += item + ", "
print(resultado)
# Imprime: manzana, pera, uva, kiwi,    ← coma de más al final

# Versión BUENA — join()
resultado = ", ".join(items)
print(resultado)
# Imprime: manzana, pera, uva, kiwi      ← limpio
```

**Regla:** cualquier vez que veas un `for` que concatena strings con `+=`, refactorízalo a `join`.

---

## Reto opcional — Slug generator (10 min)

Escribe `slug.py` que tome un título y devuelva su "slug" (la versión URL-safe):

```python
def slug(titulo):
    """Convierte un título a slug.

    Ejemplos:
        slug("Hola Mundo!")           → "hola-mundo"
        slug("Auriculares Bluetooth") → "auriculares-bluetooth"
        slug("¿Café o Té?")           → "cafe-o-te"   (extra credit con acentos)
    """
    # tu implementación
    ...

# pruebas
print(slug("Hola Mundo!"))
print(slug("Auriculares Bluetooth"))
print(slug("Producto: Monitor 4K"))
print(slug("¿Café o Té?"))    # extra credit: quitar acentos también
```

**Pistas:**
- `.lower()`, `.strip()`, `.replace()` cubren los casos básicos.
- Para quitar caracteres no alfanuméricos: `import re; re.sub(r'[^a-z0-9]+', '-', texto)`.
- Para quitar acentos: usa `unicodedata.normalize` (búscalo).

---

## Hito M1 del proyecto integrador — Primer script de TiendaPro Lite

Vas a construir el primer script real del integrador. Lee el catálogo desde un JSON, lo procesa y lo imprime.

### Setup

Ya está creado `code/proyecto-integrador/` con un `catalogo.json` de ejemplo.

```bash
cd code/proyecto-integrador/
ls
```

Deberías ver:

```
README.md
data/catalogo.json
main.py        ← implementación de referencia
pyproject.toml
```

### Lo que tu script tiene que hacer

**Pero antes — implementalo TÚ desde cero, sin mirar `main.py`.** Si necesitas referencia, mírala SOLO al final para comparar con tu solución.

Crea un archivo nuevo: `mi_solucion.py` en el mismo directorio. Ese archivo debe:

1. **Cargar** el JSON de productos desde `data/catalogo.json`. Pista:
   ```python
   import json
   from pathlib import Path

   def cargar_catalogo(ruta):
       contenido = Path(ruta).read_text(encoding="utf-8")
       return json.loads(contenido)
   ```

2. **Filtrar** solo los productos con `stock > 0`.

3. **Ordenar** los productos por precio ascendente.

4. **Imprimir** una tabla con columnas: nombre, categoría, precio, stock.

5. **Imprimir un resumen final** con:
   - Total de productos disponibles.
   - Producto más barato.
   - Producto más caro.
   - Suma total del inventario (`precio * stock` por cada producto).

### Estructura sugerida

Usa funciones puras donde puedas:

```python
import json
from pathlib import Path


def cargar_catalogo(ruta_archivo):
    """Lee el JSON y devuelve la lista de productos."""
    ...


def filtrar_disponibles(catalogo):
    """Devuelve nueva lista solo con productos en stock."""
    ...


def ordenar_por_precio(catalogo):
    """Devuelve nueva lista ordenada por precio ascendente."""
    ...


def imprimir_tabla(catalogo):
    """Imprime la tabla formateada en stdout."""
    ...


def calcular_resumen(catalogo):
    """Devuelve un dict con: total, mas_barato, mas_caro, valor_inventario."""
    ...


def imprimir_resumen(resumen):
    """Imprime el resumen formateado en stdout."""
    ...


# Main
catalogo = cargar_catalogo("data/catalogo.json")
disponibles = filtrar_disponibles(catalogo)
ordenado = ordenar_por_precio(disponibles)

imprimir_tabla(ordenado)
print()
imprimir_resumen(calcular_resumen(ordenado))
```

### Ejecutarlo

```bash
uv run python mi_solucion.py
```

### Salida esperada (aproximada)

```
Nombre                       Categoría          Precio    Stock
--------------------------------------------------------------
Ratón Inalámbrico            computación    $    19.99       30
Cargador USB-C               accesorios     $    24.99       15
Lámpara de escritorio LED    oficina        $    35.50        7
Teclado Mecánico             computación    $    49.50       12
Auriculares Bluetooth        audio          $    89.99        5
Silla ergonómica             oficina        $   220.00        2
Monitor 4K                   computación    $   320.00        3
Tablet 10"                   computación    $   450.00        8

Resumen
--------------------------------------------------------------
Productos disponibles:    8
Más barato:               Ratón Inalámbrico ($19.99)
Más caro:                 Tablet 10" ($450.00)
Valor total inventario:   $7,267.00
```

### Cuando termines

1. Comparalo con `main.py` (la implementación de referencia).
2. ¿Qué hiciste igual? ¿Qué hiciste distinto?
3. Si tu versión funciona, **¡felicitaciones!** Acabas de cerrar M1.

---

## Aporte al proyecto integrador — `proyecto-m1`

Después de hacer este ejercicio, el integrador queda en su primer hito:

- `code/proyecto-integrador/data/catalogo.json` — datos de TiendaPro.
- `code/proyecto-integrador/main.py` — script que carga, filtra, ordena, imprime.
- `code/proyecto-integrador/pyproject.toml`, `README.md` — proyecto uv funcional.

Cuando estés conforme, haz el commit como `feat(proyecto-integrador): cierra M1 con primer hito` y etiquétalo con `git tag proyecto-m1`.

---

## Antes de pasar al Módulo 2

- ✅ Hiciste los ejercicios 1-6.
- ✅ Implementaste tu propia versión del hito M1 y la comparaste con la referencia.
- ✅ Te resultan claras f-strings, slicing y los 7 métodos esenciales.

Si los tres están listos, **terminaste el Módulo 1**. Sigue con [Módulo 2 — Python intermedio](../../02-python-intermedio/) (próximamente).
