# S01 — Ejercicios

Práctica en tu computadora. Para todos los ejercicios usa el REPL (modo interactivo) o crea un archivo `.py` y ejecútalo con `uv run python archivo.py`. Algunos ejercicios pueden hacerse en cualquiera de los dos modos — usa el que te resulte más cómodo.

> **Recordatorio:** abre el REPL con `uv run python` desde dentro de un proyecto inicializado con uv (puedes reutilizar `mi-hola-mundo` de S00.2).

---

## Ejercicio 1 — Tipos en el REPL (10 min)

Abre el REPL y experimenta con tipos. Para cada línea, **predice mentalmente** qué va a salir antes de presionar Enter. Si tu predicción falla, revisa por qué.

```python
>>> type(42)
>>> type(42.0)
>>> type("42")
>>> type(True)
>>> type(None)
>>> type(42 + 0.0)
>>> type(int("42"))
>>> type(str(42))
```

**Pregunta:** ¿qué te dice `type(42 + 0.0)`? ¿Por qué Python decidió ese tipo y no `int`?

---

## Ejercicio 2 — Convertir y romper conversiones (10 min)

Crea un archivo `conversiones.py` con el siguiente contenido y ejecútalo:

```python
print(int("100"))
print(float("3.14"))
print(str(42) + " manzanas")
print(int(3.99))
print(bool(0))
print(bool(""))
print(bool("False"))
```

**Pregunta antes de ejecutar:** ¿cuál crees que va a ser la salida de `bool("False")`? ¿Por qué?

Ahora añade estas líneas al final y ejecútalo de nuevo. Lee el error que sale **completo**:

```python
print(int("3.14"))
print(float("3,14"))
```

**Pregunta:** ¿qué tipo de error es? ¿Cómo lo solucionarías?

---

## Ejercicio 3 — Aritmética y la división (10 min)

En el REPL:

```python
>>> 10 / 3
>>> 10 // 3
>>> 10 % 3
>>> 2 ** 10
>>> 7 / 2
>>> 7 // 2
>>> -7 // 2
```

**Pregunta:** ¿qué da `-7 // 2`? ¿Por qué? (Pista: Python siempre redondea hacia abajo, no hacia cero.)

---

## Ejercicio 4 — Operadores booleanos y short-circuit (10 min)

Predice la salida de cada línea **antes** de ejecutarla:

```python
>>> True and False
>>> True or False
>>> not True
>>> True and "hola"
>>> False or "mundo"
>>> 0 or 5
>>> "" or "default"
>>> None and "esto no se evalúa"
```

**Para reflexionar:** los operadores `and` y `or` no devuelven solo `True` o `False` — devuelven el valor de uno de los operandos. Esto se usa para escribir defaults: `nombre = nombre_usuario or "anónimo"`. ¿Entiendes por qué funciona?

---

## Ejercicio 5 — Cálculo de TiendaPro (15 min)

Crea un archivo `precio_descuento.py` y escribe un programa que:

1. Define las variables:
   ```python
   nombre_producto = "Auriculares Bluetooth"
   precio_unitario = 89.99
   cantidad = 3
   descuento_porcentaje = 0.15  # 15%
   ```
2. Calcula el subtotal (precio × cantidad).
3. Calcula el descuento total (subtotal × descuento_porcentaje).
4. Calcula el total final (subtotal − descuento).
5. Imprime cada paso de forma legible. Ejemplo de salida esperada:

   ```
   Producto:  Auriculares Bluetooth
   Cantidad:  3 × $89.99
   Subtotal:  $269.97
   Descuento: -$40.50 (15%)
   Total:     $229.47
   ```

**Pista:** para imprimir números con dos decimales usa `f"{numero:.2f}"`.

**Reto adicional:** modifica el script para que, si el subtotal supera $200, aplique un descuento adicional del 5%. Usa un `if` (lo veremos en detalle en S02 — aquí basta con que lo pruebes).

---

## Ejercicio 6 — La trampa del float (5 min)

Ejecuta este script:

```python
a = 0.1 + 0.2
b = 0.3

print(f"a = {a}")
print(f"b = {b}")
print(f"a == b → {a == b}")
print(f"abs(a - b) < 1e-9 → {abs(a - b) < 1e-9}")
```

**Pregunta:** ¿qué imprime cada línea? ¿Por qué el primer `==` da `False` aunque parezca que `a` y `b` son lo mismo?

---

## Ejercicio 7 — `None` no es `False` (5 min)

```python
respuesta = None

print(respuesta == False)
print(respuesta == 0)
print(respuesta == "")
print(respuesta is None)
```

**Pregunta:** los primeros tres dan `False`, pero el cuarto da `True`. ¿Cuál es la diferencia entre `==` e `is` cuando trabajas con `None`?

> **Convención de Python:** siempre usa `is None` o `is not None` para comparar con `None`, no `== None`. Es la forma correcta y ruff te avisaría si lo escribes mal.

---

## Reto opcional — Calculadora de propinas (15 min)

Sin usar funciones todavía (las vemos en S04), escribe un script `propinas.py` que:

1. Pida al usuario el monto de la cuenta (con `input()`).
2. Pida el porcentaje de propina (10, 15, 20).
3. Pida cuántas personas dividen la cuenta.
4. Imprima:
   - Monto de la propina total.
   - Total a pagar (cuenta + propina).
   - Monto que pone cada persona.

**Restricciones técnicas:**
- `input()` siempre devuelve `str` — convierte (con `float` o `int`) lo que necesites.
- Maneja números con dos decimales en la salida.
- No te preocupes por validar inputs raros — eso lo cubrimos en S07 (manejo de errores).

---

## Aporte al proyecto integrador

Esta sesión todavía no agrega código al integrador. La sesión que cierra el M1 es S05 (strings) y allí vamos a integrar todo lo aprendido en M1 escribiendo el primer hito de TiendaPro Lite (`proyecto-m1`): leer un JSON con productos y mostrarlos ordenados por precio.

---

## Antes de pasar a S02

- ✅ Hiciste los ejercicios 1-7 ejecutándolos en tu computadora (no solo leyéndolos).
- ✅ Las preguntas de auto-evaluación del README te resultan claras.
- ✅ Sabes usar el REPL para probar expresiones rápidas.

Si los tres están listos, sigue con [S02 — Control de flujo](../sesion-02-control-flujo/README.md) (próximamente).
