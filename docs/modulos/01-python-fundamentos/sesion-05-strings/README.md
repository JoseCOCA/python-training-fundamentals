# S05 — Strings y manipulación de texto

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Cierra el Módulo 1** con el primer hito del proyecto integrador (`proyecto-m1`). Si vas hacia AI Engineering, el dominio de strings importa más que en cualquier otra área del software.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a:

- Manipular strings con confianza: indexar, slicear, dividir, unir, reemplazar.
- Conocer los métodos de string que usarás todos los días.
- Usar **f-strings** para formatear texto de forma legible.
- Entender que los strings son **inmutables** y qué consecuencias tiene.
- Saber qué es un encoding y por qué `UTF-8` es siempre la respuesta correcta.
- **Cerrar el primer hito de TiendaPro Lite**: leer un JSON con productos y mostrarlos ordenados por precio.

## 2. Prerequisitos

- [S01](../sesion-01-variables-tipos/README.md), [S02](../sesion-02-control-flujo/README.md), [S03](../sesion-03-estructuras-datos/README.md), [S04](../sesion-04-funciones/README.md) completas.
- En particular: comprensiones de lista, funciones y manejo de `dict`.

## 3. Conceptos clave

1. **String como secuencia inmutable.** Un `str` es una secuencia de caracteres que no se puede modificar — toda "modificación" crea un string nuevo.
2. **Indexing y slicing.** Mismo modelo que `list`. `s[0]` primer carácter, `s[-1]` último, `s[1:4]` slice.
3. **f-strings.** Forma idiomática de formatear texto en Python 3.6+. `f"Hola {nombre}"` interpola el valor de `nombre` directamente.
4. **Métodos de string.** `.split()`, `.join()`, `.strip()`, `.lower()`, `.replace()`, `.find()`, `.startswith()`, `.endswith()`. Estos siete cubren el 80% de tus casos.
5. **Encoding.** Cómo se representan los caracteres en bytes. `UTF-8` es el estándar moderno y debería ser tu default siempre.

## 4. Teoría

### 4.1. Strings como secuencias inmutables

```python
nombre = "Carolina"

# Indexar
nombre[0]            # → "C"
nombre[-1]           # → "a"

# Slicing (igual que con list)
nombre[0:4]          # → "Caro"
nombre[:4]           # → "Caro"
nombre[4:]           # → "lina"
nombre[::-1]         # → "aniloraC"  (al revés)

# Longitud
len(nombre)          # → 8

# Pertenencia
"oli" in nombre      # → True
```

**Inmutabilidad:**

```python
nombre[0] = "K"      # ❌ TypeError: 'str' object does not support item assignment
```

Para "modificar", creas un string nuevo:

```python
nombre = "K" + nombre[1:]    # → "Karolina"
```

Esto NO es ineficiente para casos normales. Si vas a hacer miles de concatenaciones en un bucle, hay patrones más rápidos (`"".join(lista)`) que veremos.

### 4.2. f-strings (la forma moderna de formatear)

**Versión vieja** (concatenación):

```python
nombre = "Carolina"
edad = 28
mensaje = "Hola, " + nombre + ", tienes " + str(edad) + " años"
```

**Versión vieja 2** (`%` o `.format()`):

```python
mensaje = "Hola, %s, tienes %d años" % (nombre, edad)
mensaje = "Hola, {}, tienes {} años".format(nombre, edad)
```

**Versión moderna** (f-string, Python 3.6+):

```python
mensaje = f"Hola, {nombre}, tienes {edad} años"
```

Las f-strings permiten **expresiones** dentro de las llaves:

```python
precio = 89.99
cantidad = 3

f"Total: ${precio * cantidad}"           # → "Total: $269.97"
f"Total: ${precio * cantidad:.2f}"       # → "Total: $269.97"  (2 decimales)
f"Cliente: {nombre.upper()}"             # → "Cliente: CAROLINA"
```

**Format specifiers comunes:**

```python
f"{numero:.2f}"        # 2 decimales:  19.99
f"{numero:>10}"        # alineado derecha, ancho 10
f"{numero:<10}"        # alineado izquierda
f"{numero:*^10}"       # centrado, rellenando con *
f"{numero:,}"          # separador de miles: 1,234,567
f"{porcentaje:.1%}"    # porcentaje: 0.15 → 15.0%
```

### 4.3. Métodos de string esenciales

**`split()`** — divide en lista:

```python
"manzana,pera,uva".split(",")           # → ["manzana", "pera", "uva"]
"hola mundo python".split()              # → ["hola", "mundo", "python"]
```

**`join()`** — une lista en string:

```python
",".join(["manzana", "pera", "uva"])    # → "manzana,pera,uva"
" ".join(["hola", "mundo"])              # → "hola mundo"
```

**`strip()`** — quita espacios al inicio y final:

```python
"  hola  ".strip()        # → "hola"
"  hola  ".lstrip()       # → "hola  "  (solo a la izquierda)
"  hola  ".rstrip()       # → "  hola"  (solo a la derecha)
"###texto###".strip("#")  # → "texto"   (quita # en lugar de espacios)
```

**`lower()` / `upper()` / `title()` / `capitalize()`** — caso:

```python
"Hola Mundo".lower()      # → "hola mundo"
"Hola Mundo".upper()      # → "HOLA MUNDO"
"hola mundo".title()      # → "Hola Mundo"
"hola mundo".capitalize() # → "Hola mundo"
```

**`replace()`** — reemplaza:

```python
"hola mundo".replace("mundo", "python")    # → "hola python"
```

**`find()` / `index()`** — busca posición:

```python
"hola mundo".find("mundo")     # → 5
"hola mundo".find("xyz")       # → -1   (no encontrado)
"hola mundo".index("mundo")    # → 5
"hola mundo".index("xyz")      # → ValueError
```

**`startswith()` / `endswith()`** — booleanos:

```python
"reporte.pdf".endswith(".pdf")     # → True
"https://...".startswith("https")  # → True
```

**`count()`** — cuántas veces aparece:

```python
"banana".count("a")     # → 3
```

### 4.4. Caso del catálogo: parsear y normalizar

Caso típico que vas a hacer en el integrador:

```python
linea = "  Auriculares Bluetooth | $89.99 | stock: 5  "

# Limpiar y separar
campos = [c.strip() for c in linea.split("|")]
# campos == ["Auriculares Bluetooth", "$89.99", "stock: 5"]

# Extraer precio (quitar $)
precio = float(campos[1].replace("$", ""))
# precio == 89.99

# Extraer stock (quitar "stock: ")
stock = int(campos[2].replace("stock:", "").strip())
# stock == 5

# Normalizar nombre (lowercase, sin espacios extras)
nombre = campos[0].lower()
# nombre == "auriculares bluetooth"
```

**Patrón:** chain de métodos. Cada uno devuelve un nuevo string que pasas al siguiente.

### 4.5. Strings multilínea y caracteres especiales

```python
mensaje = """Línea 1
Línea 2
Línea 3"""

# Caracteres de escape
print("primer linea\nsegunda linea")    # \n = newline
print("con\ttab")                        # \t = tab
print("comillas: \"hola\"")              # \" = comilla
print("backslash: \\")                   # \\ = un solo \

# Raw string — \n NO se interpreta
print(r"esto: \n no es newline")         # imprime: esto: \n no es newline
```

Los **raw strings** (`r"..."`) son útiles para rutas Windows y expresiones regulares.

### 4.6. Encoding (lo justo para no morir)

Un string en Python es una secuencia de **caracteres** Unicode. Cuando lo guardas en disco o lo mandas por red, hay que convertirlo a **bytes**. Esa conversión usa un **encoding**.

```python
texto = "café"
bytes_utf8 = texto.encode("utf-8")        # b'caf\xc3\xa9'   (5 bytes)
bytes_latin1 = texto.encode("latin-1")    # b'caf\xe9'        (4 bytes)

# Decodificar
bytes_utf8.decode("utf-8")    # → "café"
bytes_utf8.decode("latin-1")  # → "café"  ← MAL: garbled, mismo bytes pero distintos
```

**Reglas prácticas:**

- **Usa siempre UTF-8.** Es el estándar de internet y soporta cualquier idioma.
- Cuando abres un archivo, especifica `encoding="utf-8"`:
  ```python
  with open("archivo.txt", encoding="utf-8") as f:
      contenido = f.read()
  ```
- Si te encuentras con un archivo "raro" (de Windows viejo), puede ser `latin-1` o `cp1252`. Prueba uno por uno.

### 4.7. Por qué los strings importan tanto en AI Engineering

Cuando llegues al curso 2 vas a:

- Construir prompts (strings con interpolación de variables).
- Procesar respuestas de LLMs (parseo de output).
- Limpiar y normalizar texto antes de embeddings (lowercase, strip, normalizar acentos).
- Trabajar con tokens (un token es una pieza de string).

Cada línea de AI Engineering pasa por strings. Dominarlos en M1 es cimiento crítico.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| f-strings para formatear | concatenar con `+` y `str()` |
| `"separador".join(lista)` | bucle que concatena con `+=` |
| `texto.strip().lower()` (chain) | múltiples variables intermedias |
| `if texto.startswith("http")` | `if texto[:4] == "http"` |
| Especificar `encoding="utf-8"` al abrir archivos | depender del default del sistema operativo |
| Usar raw strings para regex y rutas | escapar manualmente cada `\` |
| Comprensión para parsear líneas | bucle largo con `append` |

## 6. Conexión con el proyecto integrador — Hito M1

Acabamos de cubrir todo lo necesario para el **primer hito** de TiendaPro Lite. En `ejercicios.md` y en `code/proyecto-integrador/` vas a:

- Leer un archivo `data/catalogo.json` con productos.
- Validar / normalizar los datos básicos.
- Ordenarlos por precio ascendente.
- Imprimirlos en formato tabla.

El código va a usar todo lo de M1: variables (S01), `for`/`if` (S02), `list` y `dict` (S03), funciones (S04), y f-strings + strings (S05).

Al terminar, hacemos `git tag proyecto-m1` y queda asentado el primer hito.

## 7. Resumen

1. **Strings son secuencias inmutables.** Indexá y sliceá igual que listas. Modificarlos crea nuevos.
2. **f-strings es la forma moderna.** `f"valor: {x}"`. Acepta expresiones, format specifiers, y es legible.
3. **7 métodos esenciales:** `split`, `join`, `strip`, `lower`, `replace`, `find`, `startswith`. Combinálos con chains.
4. **UTF-8 siempre.** Especifícalo cuando abras archivos.

## 8. Preguntas de auto-evaluación

1. ¿Por qué `nombre[0] = "K"` falla?
2. ¿Qué imprime `f"{0.123456:.2f}"`?
3. Diferencia entre `"abc".find("z")` y `"abc".index("z")`.
4. Tienes `"hola, mundo, python".split(",")`. ¿Qué obtienes?
5. ¿Por qué deberías usar `"".join(lista_de_strings)` en lugar de un bucle con `+=`?
6. ¿Qué es un encoding? ¿Por qué `UTF-8` es la respuesta correcta el 99% del tiempo?
7. Escribe una línea que tome `"  Hola Mundo  "` y devuelva `"hola-mundo"` (lowercase, sin espacios al borde, espacios internos como `-`).

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md) — y prepárate para cerrar el M1 con el primer hito del integrador.
