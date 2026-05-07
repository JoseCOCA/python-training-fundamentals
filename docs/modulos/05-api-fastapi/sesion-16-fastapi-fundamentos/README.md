# S16 — FastAPI fundamentos: rutas, request/response, async handlers

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. **Abre el Módulo 5.** Hasta acá fuiste el **cliente** de las APIs (en S13 con `httpx`). Hoy te das la vuelta y armás **el servidor**. FastAPI no es un framework arbitrario — es la consecuencia natural de combinar tres cosas que ya tenés: anotaciones de tipos (S10), validación con pydantic (S11) y `async/await` (S12). El framework toma esos tres y construye una API REST con docs automáticas y tipado de punta a punta.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué hace un framework web por vos: parsear el request, despachar a la función correcta, serializar el response.
- Crear una `FastAPI()` y montar rutas con `@app.get(...)`, `@app.post(...)`, `@app.put(...)`, `@app.delete(...)`.
- Distinguir **path parameters** (`/productos/{id}`), **query parameters** (`?q=...`), **headers** y **body** y declararlos en la firma del handler.
- Devolver objetos pydantic y dejar que FastAPI los serialice a JSON automáticamente.
- Decidir cuándo un handler debe ser `async def` y cuándo `def` regular.
- Levantar el servidor con `uvicorn` y entender qué hace.
- Leer la documentación interactiva (Swagger UI / ReDoc) que FastAPI genera sola.

## 2. Prerequisitos

- [S13 — httpx + JSON](../../04-async-http-persistencia/sesion-13-httpx-json/README.md). Si entendés "una request HTTP es método + URL + headers + body", ya tenés la mitad del modelo mental.
- [S11 — pydantic v2](../../03-tipado-calidad/sesion-11-pydantic-ruff/README.md). Vamos a usar `BaseModel` para validar entradas y serializar salidas.
- [S12 — asyncio](../../04-async-http-persistencia/sesion-12-asyncio/README.md). FastAPI es async-first: querés saber **cuándo** ese `async def` te ayuda y cuándo no aporta.
- [S10 — Type hints](../../03-tipado-calidad/sesion-10-type-hints-mypy/README.md). FastAPI lee los type hints en tiempo de carga — sin tipos, no hay validación.

## 3. Conceptos clave

1. **Framework web.** Software que se queda escuchando en un puerto, recibe requests HTTP, los **parsea**, decide qué función Python ejecutar (**routing**) y **serializa** el response. Vos solo escribís las funciones.
2. **Path operation.** Cada endpoint = combinación de **método HTTP** + **path**. `GET /productos/42` es una path operation distinta de `DELETE /productos/42`.
3. **Path parameter.** Variable dentro del path: `/productos/{id}`. FastAPI la inyecta como argumento de tu función.
4. **Query parameter.** Pares `?clave=valor&otra=x` al final de la URL. Se declaran como argumentos de la función con un default.
5. **Request body.** El payload que viene en `POST`/`PUT`/`PATCH`. Se declara tipándolo como `BaseModel`.
6. **Response model.** El esquema del response. Se declara con `response_model=...` o como tipo de retorno; FastAPI lo serializa y filtra.
7. **ASGI.** Asynchronous Server Gateway Interface. La especificación que FastAPI implementa. Servidores como `uvicorn` corren cualquier app ASGI.
8. **Swagger UI / OpenAPI.** A partir de los tipos y modelos, FastAPI genera el JSON Schema de la API y lo expone en `/docs` (interactivo) y `/redoc` (sólo lectura).

## 4. Teoría

### 4.1. Qué hace un framework web (sin la magia)

Toda API HTTP es esto:

```
   ┌──────┐                          ┌─────────────┐
   │ HTTP │                          │             │
   │ req  │ ──── parsea ──────────► │  servidor   │
   └──────┘                          │  (uvicorn   │
                                     │   + ASGI)   │
                                     │             │
                                     │  routing    │
                                     │     ▼       │
                                     │  handler    │  ← tu función Python
                                     │  Python     │
                                     │     ▼       │
                                     │ serializa   │
   ┌──────┐                          │             │
   │ HTTP │ ◄──── arma response ──── │             │
   │ res  │                          └─────────────┘
   └──────┘
```

El framework te ahorra:

- **Parsear**: convertir el byte-string del body en un dict, los headers en mapping, la query string en pares.
- **Routing**: decidir qué función ejecutar para `GET /productos/42`.
- **Validación**: si declaraste que `id` es `int` y vino `"abc"`, el framework devuelve 422 antes de invocar tu función.
- **Serialización**: tomar tu objeto Python (un dict, un BaseModel, una lista) y convertirlo a JSON con headers correctos.

Tu función ya solo se preocupa por **lógica de dominio**.

### 4.2. Hola FastAPI

```python
from fastapi import FastAPI

app = FastAPI(title="TiendaPro API")


@app.get("/")
def saludar() -> dict[str, str]:
    return {"mensaje": "Hola, TiendaPro"}
```

Para correrlo:

```bash
uv add fastapi uvicorn
uv run uvicorn main:app --reload
```

`main:app` significa "el archivo `main.py` exporta una variable `app`". `--reload` recarga el server cuando cambian los archivos (solo desarrollo).

Probá:
```
http://localhost:8000/             → {"mensaje": "Hola, TiendaPro"}
http://localhost:8000/docs         → Swagger UI interactivo
http://localhost:8000/openapi.json → el schema completo
```

**Lo que pasó:** uvicorn (servidor ASGI) escucha en el puerto 8000. FastAPI registró el path `/` para método `GET`. La función devolvió un dict; FastAPI lo serializó a JSON.

### 4.3. Path parameters

```python
@app.get("/productos/{producto_id}")
def obtener_producto(producto_id: int) -> dict[str, int | str]:
    return {"id": producto_id, "nombre": f"Producto #{producto_id}"}
```

- `{producto_id}` en el path se conecta con el parámetro `producto_id: int` de la función.
- Si llega `/productos/abc`, FastAPI responde **422 Unprocessable Entity** **antes** de llamar tu función — el tipo no encaja.
- Si llega `/productos/42`, recibís `producto_id = 42` (no `"42"`). Conversión automática.

### 4.4. Query parameters

Cualquier argumento de la función que **no esté en el path** y **no sea un BaseModel** se interpreta como query param:

```python
@app.get("/productos")
def listar(
    categoria: str | None = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> list[dict[str, str | int]]:
    # ... filtrar y paginar ...
    return [{"id": 1, "nombre": "Cable USB"}]
```

URL ejemplos:
- `/productos` → `categoria=None, pagina=1, por_pagina=20`.
- `/productos?categoria=audio&pagina=2` → `categoria="audio", pagina=2, por_pagina=20`.

**Defaults son opcionales; sin default, el query param es obligatorio.**

### 4.5. Request body con `BaseModel`

Acá brilla pydantic. Declarás un modelo y lo poneás como argumento:

```python
from pydantic import BaseModel, Field


class ProductoNuevo(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)


@app.post("/productos")
def crear(producto: ProductoNuevo) -> dict[str, str | int]:
    # producto ya está validado: nombre no vacío, precio > 0, stock >= 0
    return {"id": 999, "nombre": producto.nombre}
```

Flujo:
1. Llega `POST /productos` con body JSON.
2. FastAPI lo parsea y se lo pasa a `ProductoNuevo.model_validate(...)`.
3. Si falla la validación → 422 con detalle por campo.
4. Si pasa → tu función recibe el `ProductoNuevo` ya tipado.

Lo mismo vale para `PUT`/`PATCH`/`DELETE` con body.

### 4.6. Response models

Hasta acá devolvíamos `dict`s. Para una API seria, declará el response como un `BaseModel`:

```python
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int


@app.get("/productos/{id}", response_model=ProductoResponse)
def obtener(id: int):
    # ... obtener de la DB ...
    return ProductoResponse(id=id, nombre="Cable", categoria="acc", precio=12.5, stock=3)
```

O —forma más moderna— usá el tipo de retorno de la función:

```python
@app.get("/productos/{id}")
def obtener(id: int) -> ProductoResponse:
    ...
```

Beneficios:
- **Filtra campos**: si tu objeto interno tiene `password_hash`, no se filtra al response.
- **Documenta**: el `/docs` muestra exactamente la forma del response.
- **Valida en la salida también**: si por error devolvés algo que no encaja, FastAPI lo detecta.

### 4.7. Status codes

Por default, `GET` devuelve 200, `POST` devuelve 200 (sí, 200). Para `POST` lo correcto es 201:

```python
from fastapi import status


@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear(producto: ProductoNuevo) -> ProductoResponse:
    ...
```

Status codes que vas a usar:

- `status.HTTP_200_OK` — default para GET/PUT/PATCH/DELETE con body.
- `status.HTTP_201_CREATED` — POST que crea un recurso.
- `status.HTTP_204_NO_CONTENT` — DELETE sin body.
- `status.HTTP_400_BAD_REQUEST` — la request tiene un problema.
- `status.HTTP_404_NOT_FOUND` — el recurso no existe.
- `status.HTTP_422_UNPROCESSABLE_ENTITY` — falla validación pydantic (FastAPI lo emite solo).
- `status.HTTP_500_INTERNAL_SERVER_ERROR` — explotaste vos.

### 4.8. Errores: `HTTPException`

```python
from fastapi import HTTPException, status


@app.get("/productos/{id}")
def obtener(id: int) -> ProductoResponse:
    producto = repo.obtener(id)
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"producto {id} no existe",
        )
    return producto
```

`HTTPException` es la forma idiomática de "responder con un error y un mensaje". FastAPI lo convierte a la respuesta HTTP correcta. **No uses excepciones de tu dominio directamente en handlers** — vamos a ver cómo "traducir" excepciones de dominio a HTTPException con un exception handler en S17.

### 4.9. `async def` vs `def` — la decisión

FastAPI corre **ambos**. La regla es:

- **`async def`** cuando dentro vas a hacer I/O **async** (`httpx.AsyncClient`, `AsyncSession` de SQLAlchemy, `aiofiles`). Ahí aprovechás el event loop.
- **`def`** cuando hacés operaciones síncronas (DB sync, archivo, computación). FastAPI las despacha al **thread pool** automáticamente para no bloquear el loop.

**Lo importante:** si tu handler es `async def` y adentro hacés `time.sleep(2)` o `requests.get(...)`, **bloqueás el event loop entero**. Eso es el antipatrón de S12 reincidiendo. O todo el handler es sync, o usás versiones async.

Para el integrador del módulo, vamos a usar `def` regular y SQLAlchemy sync — más simple, igualmente correcto. Async se justifica cuando demostradamente necesitás concurrencia (cientos de requests simultáneos).

### 4.10. uvicorn y ASGI

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

- **`uvicorn`** es un servidor ASGI escrito en Rust (vía `uvloop`) y Python. Es rapidísimo.
- **ASGI** = la versión async de WSGI (el viejo estándar de Django/Flask). Permite que un servidor sirva apps async.
- **`--reload`** solo en desarrollo. En producción usá `gunicorn -k uvicorn.workers.UvicornWorker` con varios workers, o `uvicorn` directo con `--workers N`.
- **`--host 0.0.0.0`** acepta conexiones de fuera del contenedor. Por default es `127.0.0.1`.

Para el curso siempre `--reload` y `127.0.0.1` (default).

### 4.11. La doc automática es real

Apenas levantás el server, `http://localhost:8000/docs` te da:

- Lista de endpoints agrupados por tag.
- Schemas (los BaseModel) con cada campo documentado.
- Botón "Try it out" que te deja mandar requests reales desde el browser.
- Genera el JSON Schema OpenAPI 3.x — exportable a Postman, Insomnia, generadores de SDKs.

**No es un extra**. Es **el mismo código** ejecutado dos veces — una para servir requests, otra para introspectarse y exponer el contrato. Esa es la propuesta de FastAPI.

### 4.12. Lo que viene en el módulo

- **S17**: separación entre modelos de **request** y **response**, exception handlers que traducen excepciones de dominio a HTTP, validación más fina con `Field`, errores 4xx/5xx idiomáticos.
- **S18**: configuración con `pydantic-settings` (env vars, `.env`), secretos, logging estructurado.
- **Hito M5**: TiendaPro pasa a ser una API REST real, con endpoints CRUD para productos.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `def handler(...) -> ResponseModel` con tipos en todo | `def handler(...)` sin tipos (pierdes validación y docs) |
| `async def` cuando vas a usar I/O async dentro | `async def` con `time.sleep` o `requests.get` adentro |
| `BaseModel` para body, response model con `-> Modelo` | Devolver dicts crudos en una API "seria" |
| `HTTPException(status_code=..., detail=...)` | `raise Exception("not found")` en un handler |
| `status_code=status.HTTP_201_CREATED` en POST que crea | POST que devuelve 200 (técnicamente válido, semánticamente flojo) |
| `Path`, `Query`, `Body` solo cuando necesitás validación extra | Usarlos en cada handler "por si acaso" |
| Una `app = FastAPI()` por proceso | Crearla varias veces o adentro de funciones |
| Probar con `/docs` mientras desarrollás | Probar con `curl` largo + flags |
| `--reload` solo en dev | `--reload` en producción |

## 6. Conexión con el proyecto integrador

**Hoy todavía no migramos el integrador a API.** Ese trabajo arranca en S17 y cierra en el hito M5. En esta sesión vas a construir una **API mini-tienda en el sandbox** para entrenar los reflejos: rutas básicas, query params, body con pydantic, response model, status codes.

Cuando llegue S18, ya vas a tener fluidez con los handlers y la conversación se centra en cómo conectar **el código del integrador** (repositorio, ORM, integraciones HTTP) detrás de las rutas — que es la parte interesante.

## 7. Resumen

1. **Un framework web parsea, rutea, valida y serializa.** Vos solo escribís funciones.
2. **`FastAPI()` + `@app.get/post/put/delete`** es todo lo que necesitás para empezar.
3. **Path params**: `/productos/{id}` ↔ argumento `id: int`. **Query params**: cualquier otro argumento simple. **Body**: argumento que es `BaseModel`.
4. **Response model**: declara el tipo de retorno (`-> Modelo`) o usá `response_model=...`. Filtra campos y documenta.
5. **`HTTPException` para errores con status code y mensaje.** No uses excepciones genéricas en handlers.
6. **`async def`** cuando vas a usar I/O async; **`def`** cuando vas síncrono. **Nunca mezcles** sync bloqueante adentro de un handler async.
7. **`uvicorn main:app --reload`** levanta el server. `/docs` es Swagger UI sin configuración.
8. **El tipado es la fuente de la verdad.** Los hints de Python son la documentación, la validación y el contrato de la API — todos al mismo tiempo.

## 8. Preguntas de auto-evaluación

1. ¿Qué cuatro cosas hace por vos un framework web como FastAPI?
2. ¿Qué pasa si declarás `def f(id: int)` y llega `/productos/abc`? ¿Qué status code devuelve FastAPI?
3. Diferencia entre **path parameter** y **query parameter**. Ejemplo de URL para cada uno.
4. ¿Cómo declarás un body JSON validado con pydantic? Mostrá el patrón completo (modelo + handler).
5. ¿Cuándo usarías `async def` vs `def` en un handler? ¿Qué pasa si bloqueás el loop adentro de un `async def`?
6. ¿Qué hace `response_model=ProductoResponse` además de documentar?
7. ¿Cómo respondés con un 404 cuando un recurso no existe?
8. ¿Por qué el POST típico debería devolver 201 y no 200?
9. ¿Qué genera FastAPI a partir de tus tipos y modelos? Nombrá tres cosas que aparecen en `/docs`.
10. ¿Qué es ASGI y por qué importa que FastAPI la implemente?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).
