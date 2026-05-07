# S12 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado donde ves la diferencia sync vs async cronometrada, libres para entrenar `gather` / `TaskGroup` / `to_thread`, reto con un mini-pool concurrente.

> **Hoy no hay aporte al integrador** — la sesión es teórica/calibración. El integrador entra en S13 y cierra en el hito M4 al final del módulo.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m04-async-http-persistencia/sesion-12/`. Si todavía no lo corriste:

```bash
cd code/m04-async-http-persistencia/sesion-12
uv sync
uv run python main.py
uv run mypy .
uv run ruff check .
```

Confirma que las cuatro demos imprimen, mypy pasa limpio, ruff no reporta nada. Después regresa a este documento.

## 1. Ejercicio guiado — Sync vs Async, cronometrado

Vamos a medir lo que el README explica con palabras.

### Paso 1.1 — La versión síncrona

Crea un archivo `cronometro_sync.py`:

```python
import time


def llamada_simulada(nombre: str) -> str:
    """Simula una llamada I/O que tarda 0.5 s."""
    time.sleep(0.5)
    return f"respuesta de {nombre}"


def correr_sincrono(n: int) -> list[str]:
    return [llamada_simulada(f"servicio-{i}") for i in range(n)]


if __name__ == "__main__":
    inicio = time.perf_counter()
    resultados = correr_sincrono(5)
    duracion = time.perf_counter() - inicio
    print(f"Síncrono: {len(resultados)} respuestas en {duracion:.2f}s")
```

Esperado: ~2.5 s.

```bash
uv run python cronometro_sync.py
```

### Paso 1.2 — La versión async (mal hecha)

Crea `cronometro_async_mal.py`:

```python
import asyncio
import time


async def llamada_simulada(nombre: str) -> str:
    await asyncio.sleep(0.5)
    return f"respuesta de {nombre}"


async def correr_secuencial(n: int) -> list[str]:
    resultados = []
    for i in range(n):
        resultados.append(await llamada_simulada(f"servicio-{i}"))
    return resultados


async def main() -> None:
    inicio = time.perf_counter()
    resultados = await correr_secuencial(5)
    duracion = time.perf_counter() - inicio
    print(f"Async secuencial: {len(resultados)} respuestas en {duracion:.2f}s")


asyncio.run(main())
```

Esperado: **también ~2.5 s**. Tienes `async/await` pero las llamadas se hacen una tras otra. Es la trampa del README.

### Paso 1.3 — La versión async correcta

Crea `cronometro_async_bien.py`:

```python
import asyncio
import time


async def llamada_simulada(nombre: str) -> str:
    await asyncio.sleep(0.5)
    return f"respuesta de {nombre}"


async def correr_concurrente(n: int) -> list[str]:
    return await asyncio.gather(
        *[llamada_simulada(f"servicio-{i}") for i in range(n)]
    )


async def main() -> None:
    inicio = time.perf_counter()
    resultados = await correr_concurrente(5)
    duracion = time.perf_counter() - inicio
    print(f"Async concurrente: {len(resultados)} respuestas en {duracion:.2f}s")


asyncio.run(main())
```

Esperado: ~0.5 s. Las cinco llamadas se disparan a la vez y el loop espera a la última.

### Paso 1.4 — Reflexionar

| Variante | Tiempo | Por qué |
|---|---|---|
| Síncrona | ~2.5 s | Cinco esperas de 0.5 s en serie |
| Async secuencial | ~2.5 s | Mismo motivo: `await` en el `for` espera una a una |
| Async concurrente | ~0.5 s | Las cinco esperas se solapan |

**Lección:** la palabra clave `async` no hace nada por sí sola. Lo que paraleliza es lanzar varias corutinas y esperarlas con `gather` o `TaskGroup`.

## 2. Ejercicios libres

### 2.1. Migrar de `gather` a `TaskGroup`

Toma `cronometro_async_bien.py` y reescríbelo usando `asyncio.TaskGroup` en vez de `gather`. Captura el resultado de cada task con `task.result()` después del bloque `async with`.

Pista:

```python
async with asyncio.TaskGroup() as tg:
    tasks = [tg.create_task(llamada_simulada(f"servicio-{i}")) for i in range(n)]
return [t.result() for t in tasks]
```

Confirma que el tiempo es similar (~0.5 s).

### 2.2. Mezcla de async y sync con `to_thread`

Dada esta función bloqueante:

```python
import time


def calcular_pesado(x: int) -> int:
    time.sleep(0.3)        # simula I/O en una librería sync vieja
    return x * x
```

Escribe una corutina `correr_pesados(valores: list[int]) -> list[int]` que:

1. Despache cada llamada a `asyncio.to_thread(calcular_pesado, v)`.
2. Las espere con `gather`.
3. Devuelva la lista de resultados.

Cronométralo. Con 10 valores debería tardar ~0.3 s (el thread pool usa varios hilos del sistema), no 3 s.

### 2.3. Detectar el antipatrón en código ajeno

Mira este snippet y di **dos cosas que están mal**:

```python
import asyncio
import requests


async def descargar_todo(urls: list[str]) -> list[str]:
    contenidos = []
    for url in urls:
        r = requests.get(url)            # ←
        contenidos.append(r.text)
    return contenidos


asyncio.run(descargar_todo(["https://a.com", "https://b.com"]))
```

Después escribe la versión correcta usando `httpx.AsyncClient` y `gather` (sin correrla todavía — eso es S13). Solo el snippet.

### 2.4. Cancelación con `TaskGroup`

Escribe una corutina `riesgosa(i: int)` que:

- Si `i == 3`, levante `ValueError("explotó la 3")`.
- Si no, espere 0.5 s y devuelva `i * 10`.

Llama cinco tasks (0..4) dentro de un `TaskGroup`. Captura el `ExceptionGroup` con `except*` y muestra:

- Cuántas tasks fallaron.
- Cuál(es) (i.e. qué mensaje trae cada excepción).

Observa que las tasks que aún no habían terminado se cancelaron solas.

### 2.5. Timeout

Usa `asyncio.timeout(...)` (3.11+) para correr una corutina con límite de tiempo:

```python
async def lenta() -> str:
    await asyncio.sleep(2.0)
    return "lista"


async def main() -> None:
    try:
        async with asyncio.timeout(0.5):
            print(await lenta())
    except TimeoutError:
        print("se canceló por timeout")


asyncio.run(main())
```

Después prueba con `asyncio.sleep(0.2)` adentro de `lenta` y observa que sí termina antes del timeout.

## 3. Reto — Mini-pool concurrente con límite

Imagina que tienes 50 SKUs para los que querés pedir precios. Si lanzas las 50 a la vez con `gather`, saturas la API. Si las haces una por una, tardás siglos.

**Construye una función `pedir_precios(skus: list[str], paralelismo: int) -> dict[str, float]`** que:

1. Use `asyncio.Semaphore(paralelismo)` para limitar cuántas corutinas pueden correr a la vez.
2. Defina internamente una corutina `_pedir_uno(sku)` que adquiera el semáforo, simule la "API" con `await asyncio.sleep(0.2)` + un valor calculado (por ejemplo `len(sku) * 1.5`), y libere.
3. Lance todas las llamadas con `gather` o `TaskGroup`.
4. Devuelva un dict `{sku: precio}`.

Cronométralo con 50 SKUs y `paralelismo = 5`. Esperado: alrededor de **2 s** (50 / 5 = 10 grupos × 0.2 s). Compáralo con `paralelismo = 1` (~10 s) y `paralelismo = 50` (~0.2 s).

**Por qué este patrón importa:** en el mundo real, las APIs tienen rate limits. La concurrencia sin límite no es ventaja, es DDoS auto-infligido. El semáforo es la pieza estándar para limitar el paralelismo en asyncio.

## 4. Sin aporte al integrador hoy

Esta sesión calibra la cabeza. El integrador no se toca. La S13 introduce httpx y ahí empieza el tejido real con TiendaPro.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, S12 está consolidada y puedes pasar a [S13 — httpx + JSON](../sesion-13-httpx-json/README.md).
