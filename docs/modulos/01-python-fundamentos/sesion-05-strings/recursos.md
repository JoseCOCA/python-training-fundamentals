# S05 — Recursos

---

## Documentación oficial

- **Python tutorial — Strings** — https://docs.python.org/3/tutorial/introduction.html#strings
  La introducción oficial. Cubre indexing, slicing, métodos básicos.

- **Python docs — `str` methods** — https://docs.python.org/3/library/stdtypes.html#string-methods
  Referencia exhaustiva de métodos. Cuando dudes "¿hay un método para X?", busca aquí.

- **Python docs — Format Spec Mini-Language** — https://docs.python.org/3/library/string.html#formatspec
  Referencia de los format specifiers de f-strings. Útil cuando necesites alineación, separadores de miles, etc.

- **PEP 498 — Literal String Interpolation (f-strings)** — https://peps.python.org/pep-0498/
  La PEP que introdujo f-strings. Histórica.

---

## Lecturas recomendadas

- **"Python's f-strings: An Improved String Formatting Syntax (Guide)"** — Real Python.
  Tutorial completo de f-strings con ejemplos avanzados (alineación, decimales, expresiones complejas).

- **"Unicode HOWTO"** — Python docs.
  https://docs.python.org/3/howto/unicode.html
  Si te interesa entender en profundidad cómo Python maneja Unicode, este es el doc oficial. Avanzado.

- **"What every programmer absolutely, positively needs to know about encodings and character sets to work with text"** — Joel Spolsky.
  https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/
  Artículo clásico de 2003 que sigue valiendo. Léelo cuando quieras entender por qué los encodings son un problema.

---

## Para AI Engineering específicamente

Cuando llegues al curso 2 vas a necesitar:

- **Tokenización** — partir un texto en "tokens" (sub-palabras). Las librerías de LLMs lo hacen por ti, pero entender qué hacen pasa por dominar `str`.
- **Templates de prompts** — strings con placeholders que reemplazas con datos dinámicos. f-strings son la base; después librerías como Jinja2 te dan más potencia.
- **Parseo de salida** — los LLMs devuelven texto. A veces JSON, a veces no. Dominio de `split`, `find`, `replace` es crítico.
- **Normalización de texto** — antes de embeddings: lowercase, strip, quitar acentos, quitar caracteres especiales. Todo lo de S05.

---

## Sobre regex (expresiones regulares)

No las cubrimos en M1 porque son un mundo aparte. Pero a partir de M2 las vas a ver. Brevemente:

```python
import re

# Buscar
re.search(r"\d+", "auriculares 89 dolares")    # encuentra "89"

# Reemplazar
re.sub(r"\s+", "-", "  hola  mundo  ")          # → "-hola-mundo-"

# Validar formato
re.match(r"^\w+@\w+\.\w+$", "ana@correo.com")  # email válido
```

Cuando llegues a un caso donde `replace`/`split` se quedan cortos, regex es la herramienta. https://docs.python.org/3/library/re.html

---

## Convenciones idiomáticas que vale la pena recordar

- **String vacío como falsy:** `if not nombre:` mejor que `if nombre == ""`.
- **Concatenación masiva:** `"".join(lista)` — siempre, no `+=` en bucle.
- **Multilínea:** `"""..."""` para docstrings y mensajes largos.
- **Raw strings:** `r"..."` para regex y rutas Windows.
- **Encoding explícito:** siempre `encoding="utf-8"` al abrir archivos.
