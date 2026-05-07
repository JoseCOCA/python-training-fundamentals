# S12 — asyncio: qué bloquea, cuándo usar async, runtime model

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Abre el Módulo 4.** Hasta ahora todo el código del curso ha sido **síncrono**: una línea espera a que termine la anterior. En esta sesión cambia la mentalidad: vas a aprender qué pasa cuando una operación **espera por algo externo** (red, disco, base de datos) y cómo `asyncio` te permite no quedarte parado mirándola. No es un tour de sintaxis — es entender **el modelo runtime** primero, y la sintaxis después.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar la diferencia entre **operación CPU-bound** y **operación I/O-bound** y por qué async solo ayuda en la segunda.
- Describir el **event loop** y entender qué significa "ceder el control".
- Definir corutinas con `async def` y consumirlas con `await`.
- Lanzar una corutina con `asyncio.run(...)`.
- Ejecutar varias corutinas concurrentemente con `asyncio.gather(...)` y con `asyncio.TaskGroup`.
- Reconocer las dos formas más comunes de "matar" la concurrencia sin querer (llamar funciones bloqueantes dentro de un `async def`, o `await`-ear una a una en lugar de en paralelo).
- Decidir, ante un código nuevo, si async aporta o si suma complejidad sin retorno.

## 2. Prerequisitos

- Funciones, scope, retornos (S04).
- Generadores y context managers (S09) — `async` reutiliza la intuición.
- Decoradores (S09) — `async def` es una variante de definición, no un decorador, pero la mentalidad de "este token cambia cómo se ejecuta la función" es la misma.

## 3. Conceptos clave

1. **CPU-bound vs I/O-bound.** CPU-bound: el cuello de botella es el procesador (ordenar millones de elementos, transformar un video). I/O-bound: el cuello de botella es esperar (red, disco, DB). Async **solo** ayuda con I/O-bound.
2. **Event loop.** Un único hilo que ejecuta corutinas y, cuando una de ellas dice "estoy esperando algo externo", la pausa y agarra otra. No es paralelismo real — es **concurrencia cooperativa**.
3. **Corutina.** Función definida con `async def`. Llamarla **no la ejecuta**; devuelve un objeto corutina que tienes que `await`-ear o entregarle a un `Task`.
4. **`await`.** Marca un punto donde la función puede ceder el control al event loop. Mientras "no hay nada que hacer en esta corutina", otra puede correr.
5. **Cooperative scheduling.** Las corutinas tienen que **cooperar** cediendo el control en `await`. Si no hay `await`, monopolizas el loop.
6. **`Task`.** Una corutina envuelta para que el event loop la ejecute en background. `asyncio.create_task(...)` o `TaskGroup`.

## 4. Teoría

### 4.1. Por qué necesitamos async: el problema real

Imagina que tu programa tiene que pedir cinco precios a una API externa, cada llamada tarda 200 ms. Sincrónicamente:

```python
def pedir_precios(skus: list[str]) -> list[float]:
    return [api.precio(sku) for sku in skus]   # 5 × 200 ms = 1000 ms
```

Mientras `api.precio("X")` espera la respuesta, **tu CPU no está haciendo nada**. Está bloqueada en una llamada de red. Es tiempo regalado al universo.

Con async:

```python
async def pedir_precios(skus: list[str]) -> list[float]:
    return await asyncio.gather(*[api.precio(sku) for sku in skus])   # ~200 ms
```

Las cinco llamadas se disparan a la vez. El event loop las pone a esperar **simultáneamente** y agarra la primera que vuelve.

**No estás ejecutando código en paralelo.** Estás aprovechando los huecos de espera. Con un solo hilo. Sin threads, sin procesos. Esa es la magia de async.

### 4.2. Cuándo NO usar async (esto importa más que cuándo sí)

```python
async def calcular_hash(datos: bytes) -> str:
    return sha256(datos).hexdigest()
```

Esto **no se beneficia de async**. `sha256` no espera nada — usa CPU. Marcarlo `async` no lo hace más rápido; solo le agrega ceremonia. Para CPU-bound necesitas **multiprocessing** o C extensions, no asyncio.

Tabla rápida:

| Operación | ¿async ayuda? | Por qué |
|---|---|---|
| Pedir respuesta HTTP | ✅ | Espera por red |
| Leer/escribir base de datos | ✅ | Espera por DB |
| Leer un archivo grande | ⚠️ depende | Si es de disco local SSD, casi nada. Red distribuida sí |
| Calcular un hash, parsear JSON, hacer matemática | ❌ | CPU-bound |
| Llamar a un script externo (subprocess) | ✅ | Espera por proceso |
| `time.sleep()` | ❌ y además bloquea el loop entero | Usa `asyncio.sleep` |

### 4.3. Sintaxis mínima

```python
import asyncio


async def saludar(nombre: str) -> str:
    await asyncio.sleep(0.5)         # simula I/O
    return f"Hola, {nombre}"


async def main() -> None:
    saludo = await saludar("Ana")
    print(saludo)


asyncio.run(main())
```

Tres piezas:

1. `async def` define una **corutina**.
2. `await` ejecuta otra corutina y espera su resultado.
3. `asyncio.run(...)` arranca el event loop, ejecuta la corutina raíz y cierra el loop.

**Llamar a una corutina sin `await`** no la ejecuta:

```python
saludar("Ana")
# RuntimeWarning: coroutine 'saludar' was never awaited
```

Esto es uno de los errores más comunes al empezar.

### 4.4. Concurrencia: lanzar varias corutinas a la vez

#### `asyncio.gather`

```python
async def main() -> None:
    resultados = await asyncio.gather(
        saludar("Ana"),
        saludar("Bruno"),
        saludar("Carla"),
    )
    print(resultados)   # ["Hola, Ana", "Hola, Bruno", "Hola, Carla"]
```

`gather` recibe corutinas, las lanza en paralelo y devuelve los resultados en el mismo orden. Si una falla, por defecto cancela las otras y propaga la excepción.

#### `asyncio.TaskGroup` (Python 3.11+, recomendado)

```python
async def main() -> None:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(saludar("Ana"))
        t2 = tg.create_task(saludar("Bruno"))
        t3 = tg.create_task(saludar("Carla"))
    print([t1.result(), t2.result(), t3.result()])
```

La forma idiomática moderna. Si una task falla, el `TaskGroup` cancela las demás de forma limpia y propaga las excepciones agrupadas en un `ExceptionGroup`. Es lo que vas a usar en código nuevo.

### 4.5. El antipatrón que mata la concurrencia: await secuencial

```python
async def lento(skus: list[str]) -> list[float]:
    precios = []
    for sku in skus:
        precio = await api.precio(sku)        # ← uno por uno, esto NO es concurrente
        precios.append(precio)
    return precios
```

Sí, hay `async` y `await`. Pero estás **esperando una llamada antes de lanzar la siguiente**. Tarda igual que la versión síncrona.

La forma correcta:

```python
async def rapido(skus: list[str]) -> list[float]:
    return await asyncio.gather(*[api.precio(sku) for sku in skus])
```

**Regla:** `await` adentro de un `for` casi siempre es un olor a problema. Antes de aceptarlo, pregúntate si las llamadas son independientes — y si lo son, conviértelas a `gather` o `TaskGroup`.

### 4.6. El otro antipatrón: bloquear el event loop

```python
async def cargar_archivo() -> str:
    with open("grande.txt") as f:
        return f.read()                     # ← función SÍNCRONA dentro de async
```

`open(...).read()` es síncrono. Mientras esa línea ejecuta, **el event loop entero está parado**. Las otras corutinas tampoco corren.

Lo mismo con `time.sleep`, `requests.get`, computación pesada en Python puro, etc.

Soluciones:

- Usar la versión async cuando existe: `aiofiles` para archivos, `httpx.AsyncClient` para HTTP, drivers `asyncpg`/`aiosqlite` para DB.
- Si no hay versión async, despachar al thread pool: `await asyncio.to_thread(funcion_sincrona, args)`. El thread pool es un pool de hilos del sistema, no del event loop, así que no lo bloquea.

```python
async def cargar_archivo() -> str:
    return await asyncio.to_thread(_leer)


def _leer() -> str:
    with open("grande.txt") as f:
        return f.read()
```

### 4.7. Mental model: el restaurante

Imagina un mozo (event loop) atendiendo cinco mesas (cinco tasks).

- **Sincrónico:** el mozo toma el pedido de la mesa 1, **se queda parado** esperando que la cocina lo prepare, lo entrega, y recién después va a la mesa 2.
- **Async:** el mozo toma el pedido de la mesa 1, lo manda a la cocina (`await cocinar()`), e **inmediatamente** va a la mesa 2 a tomar pedido. Cuando la mesa 1 está lista, la cocina le avisa.

El mozo es **uno solo** — un solo hilo. Pero usa el tiempo muerto de cada mesa para atender otras. Eso es asyncio.

**El equivalente con threads** sería contratar cinco mozos. Es paralelismo real, pero te cuesta cinco salarios y los mozos pelean por la caja registradora (locks, race conditions). Por eso async es preferible cuando el trabajo es esperar, no cuando es procesar.

### 4.8. Errores y cancelación

```python
async def riesgosa() -> int:
    await asyncio.sleep(0.1)
    raise ValueError("algo salió mal")


async def main() -> None:
    try:
        await riesgosa()
    except ValueError as e:
        print(f"capturada: {e}")
```

Las excepciones cruzan `await` igual que cruzan `return` en código síncrono. Donde cambia el patrón es con concurrencia:

```python
async def main() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(riesgosa())
            tg.create_task(saludar("Ana"))
    except* ValueError as eg:
        for e in eg.exceptions:
            print(f"falló: {e}")
```

`TaskGroup` agrupa las excepciones en un `ExceptionGroup` y se capturan con `except*`. Si solo una task falló, igual recibes el grupo.

### 4.9. Cuándo async es la decisión correcta

✅ Vale la pena cuando:

- Tu programa hace muchas llamadas I/O independientes (10+ requests HTTP a distintos servicios, leer cientos de filas con queries paralelas, etc.).
- Estás escribiendo un servidor (FastAPI, en M5) que tiene que atender muchos clientes concurrentes.
- Trabajas con streams largos: WebSockets, server-sent events, polling.

❌ No vale la pena cuando:

- El programa hace una o dos llamadas I/O en total. La complejidad de async no se justifica.
- El trabajo es CPU-bound.
- Es un script que corre una vez y termina.
- Estás aprendiendo y todavía no dominas la versión sync. **Aprende sync primero.** async se construye encima.

### 4.10. Lo que viene en el módulo

- **S13:** `httpx.AsyncClient` — el primer caso real donde async paga: lanzar requests HTTP en paralelo y leer respuestas con pydantic.
- **S14:** SQL puro — vamos a entender la base de datos antes que el ORM.
- **S15:** SQLAlchemy v2 — sessions, modelos, queries. Veremos su versión async también.

El integrador del módulo (M4) usa async donde de verdad ayuda y sync donde async sería ceremonia.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `await asyncio.gather(*tareas)` para lanzar en paralelo | `for x in xs: await ...` (secuencial enmascarado) |
| `asyncio.TaskGroup` (Python 3.11+) en código nuevo | `gather` cuando ya estás en 3.11+ y no necesitas el orden estricto |
| `await asyncio.sleep(...)` | `time.sleep(...)` adentro de `async def` |
| `httpx.AsyncClient`, `aiosqlite`, `asyncpg` | `requests.get(...)`, `sqlite3.connect(...)` adentro de async |
| `await asyncio.to_thread(funcion_sync)` para piezas sync inevitables | Llamar la función sync directo y romper el loop |
| `asyncio.run(main())` como punto de entrada | Llamar a `asyncio.get_event_loop()` manualmente |
| Async donde hay I/O concurrente real | Async porque "es moderno" o "FastAPI lo usa" |
| Empezar el archivo con `import asyncio` y mantener la cadena `async def` hasta el borde | Mezclar sync/async sin pensar dónde corta |

## 6. Conexión con el proyecto integrador

Hoy **no tocamos el integrador todavía** — primero viene la teoría. En S13 vas a usar `httpx.AsyncClient` para enriquecer el catálogo desde una "API externa" (veremos cómo simularla). En S15 conectaremos con la DB. El cierre de M4 (`proyecto-m4`) va al final.

Lo único que cambia hoy en tu cabeza es la **respuesta a una pregunta**: ¿esta operación está esperando algo externo? Si sí, async puede ayudar. Si no, déjala síncrona.

## 7. Resumen

1. **Async ayuda con I/O-bound, no con CPU-bound.** Si no hay espera, no hay ganancia.
2. **El event loop es un solo hilo** que va alternando entre corutinas en sus puntos de espera (`await`).
3. **`async def` define una corutina; `await` la ejecuta.** Llamarla sin `await` no hace nada.
4. **`asyncio.run` arranca todo, `gather` y `TaskGroup` lanzan en paralelo.** En 3.11+ prefiere `TaskGroup`.
5. **`await` dentro de un `for` es casi siempre un bug de diseño.** Si las llamadas son independientes, paralelízalas.
6. **Funciones síncronas bloqueantes adentro de `async def` matan al loop.** Usa la versión async o `asyncio.to_thread`.
7. **No metas async donde no aporta.** La complejidad se paga con código que es más difícil de leer.

## 8. Preguntas de auto-evaluación

1. Define con tus palabras la diferencia entre CPU-bound y I/O-bound. Da un ejemplo de cada uno.
2. ¿Por qué `async` no acelera una función que calcula el SHA-256 de un archivo en memoria?
3. ¿Qué hace exactamente `asyncio.run(main())`? ¿Por qué normalmente solo se llama una vez en todo el programa?
4. Tienes una lista de 100 SKUs y una función `precio(sku) -> float` que es async. Escribe el snippet que pide los 100 precios en paralelo y devuelve la lista.
5. ¿Cuál es la diferencia entre `await foo()` y `asyncio.create_task(foo())`?
6. ¿Por qué `time.sleep(1)` adentro de un `async def` es un bug? ¿Qué usas en su lugar?
7. Tienes que llamar a una librería sync que no tiene versión async. ¿Cómo la integras al loop sin bloquearlo?
8. Diferencia entre `asyncio.gather` y `asyncio.TaskGroup`. ¿Cuándo eliges una sobre la otra?
9. Mira este código y di si hay un bug:
   ```python
   async def total(skus: list[str]) -> float:
       precios = []
       for sku in skus:
           precios.append(await api.precio(sku))
       return sum(precios)
   ```
10. ¿Qué pasa si dentro de un `TaskGroup` una task levanta `ValueError` y otra `TimeoutError`? ¿Cómo las capturas?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).
