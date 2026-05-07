# S16 — Ejercicios

> **Tiempo estimado:** ~75 min. Tres bloques: ejercicio guiado armando una mini-API de notas desde cero, libres para entrenar query params / body / status codes / errores, y reto con paginación + filtros.

> **Sin aporte al integrador hoy.** El integrador empieza a migrar a FastAPI en S17.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m05-api-fastapi/sesion-16/`. Si todavía no lo corriste:

```bash
cd code/m05-api-fastapi/sesion-16
uv sync
uv run uvicorn main:app --reload
```

Abrí `http://localhost:8000/docs` en el browser. Vas a ver el Swagger UI con tres rutas. Confirmá que cada una responde y después regresá a este documento.

(En otra terminal podés correr `uv run mypy .` y `uv run ruff check .` mientras el server corre.)

## 1. Ejercicio guiado — Mini-API de notas, en cinco pasos

Vas a construir una API en memoria (sin DB) para entrenar las piezas del README. Crea `notas.py` (no lo llames `main.py` para no chocar con el del sandbox):

### Paso 1.1 — Setup mínimo

```python
from fastapi import FastAPI

app = FastAPI(title="Notas API")


@app.get("/")
def root() -> dict[str, str]:
    return {"servicio": "notas", "version": "0.1.0"}
```

```bash
uv run uvicorn notas:app --reload --port 8001
```

Probá `http://localhost:8001/` y `http://localhost:8001/docs`.

### Paso 1.2 — Listar y obtener (GET con path/query)

```python
NOTAS: dict[int, dict[str, str | int]] = {
    1: {"id": 1, "titulo": "Comprar pan", "tags": "casa,urgente"},
    2: {"id": 2, "titulo": "Pagar luz", "tags": "casa"},
    3: {"id": 3, "titulo": "Estudiar FastAPI", "tags": "curso"},
}


@app.get("/notas")
def listar(tag: str | None = None) -> list[dict[str, str | int]]:
    if tag is None:
        return list(NOTAS.values())
    return [n for n in NOTAS.values() if tag in str(n["tags"]).split(",")]


@app.get("/notas/{nota_id}")
def obtener(nota_id: int) -> dict[str, str | int]:
    return NOTAS[nota_id]            # ← provoca KeyError si no existe — lo arreglamos ya
```

Probá:
- `GET /notas` → todas.
- `GET /notas?tag=casa` → solo "casa".
- `GET /notas/2` → la nota 2.
- `GET /notas/999` → tu server explota con un 500 (porque KeyError sin manejar).
- `GET /notas/abc` → 422 automático (FastAPI valida `nota_id: int`).

### Paso 1.3 — 404 propio con HTTPException

```python
from fastapi import HTTPException, status


@app.get("/notas/{nota_id}")
def obtener(nota_id: int) -> dict[str, str | int]:
    if nota_id not in NOTAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"nota {nota_id} no existe",
        )
    return NOTAS[nota_id]
```

Probá `GET /notas/999` ahora. 404 con mensaje claro.

### Paso 1.4 — Crear con body validado y status 201

```python
from pydantic import BaseModel, Field


class NotaNueva(BaseModel):
    titulo: str = Field(min_length=1, max_length=120)
    tags: str = ""


_proximo_id = 4


@app.post("/notas", status_code=status.HTTP_201_CREATED)
def crear(nueva: NotaNueva) -> dict[str, str | int]:
    global _proximo_id
    nota = {"id": _proximo_id, "titulo": nueva.titulo, "tags": nueva.tags}
    NOTAS[_proximo_id] = nota
    _proximo_id += 1
    return nota
```

Probá desde el `/docs`:
- POST con `{"titulo": "Nueva nota", "tags": "test"}` → 201.
- POST con `{"titulo": ""}` → 422 (validación fallida).
- POST con `{}` → 422 (titulo es obligatorio).

### Paso 1.5 — Response model que filtra

Imaginá que tu modelo interno tiene un campo "secreto" que no querés exponer:

```python
class NotaInterna(BaseModel):
    id: int
    titulo: str
    tags: str
    creada_por: str = "admin"            # campo que NO querés filtrar al cliente


class NotaResponse(BaseModel):
    id: int
    titulo: str
    tags: str


@app.get("/notas/{nota_id}/segura", response_model=NotaResponse)
def obtener_segura(nota_id: int) -> NotaInterna:
    # Devolvemos la NotaInterna pero el response_model filtra creada_por
    if nota_id not in NOTAS:
        raise HTTPException(status_code=404, detail="no existe")
    raw = NOTAS[nota_id]
    return NotaInterna(
        id=int(raw["id"]),
        titulo=str(raw["titulo"]),
        tags=str(raw["tags"]),
        creada_por="admin",
    )
```

Confirmá en `/docs` que la respuesta **no incluye** `creada_por`. Aunque tu función la devuelve, el `response_model` la filtra. Esa es la separación entre "modelo interno" y "modelo expuesto".

## 2. Ejercicios libres

### 2.1. PUT y DELETE

Agregá:

```python
@app.put("/notas/{nota_id}")
def reemplazar(nota_id: int, nueva: NotaNueva) -> dict[str, str | int]:
    ...


@app.delete("/notas/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar(nota_id: int) -> None:
    ...
```

Reglas:
- `PUT` reemplaza por completo. Si la nota no existe → 404.
- `DELETE` elimina y responde 204 sin body. Si la nota no existe → 404.

### 2.2. Validación con `Field` y `Query`

Cambiá `tag: str | None = None` por una validación más estricta usando `Query`:

```python
from fastapi import Query


@app.get("/notas")
def listar(
    tag: str | None = Query(default=None, min_length=2, max_length=20, pattern=r"^[a-z]+$"),
) -> list[...]:
    ...
```

Probá `?tag=A` → 422. Probá `?tag=cas` → ok. Probá `?tag=cas@` → 422.

### 2.3. Múltiples query params

Hacé que `listar` acepte:
- `tag: str | None = None` (filtro).
- `q: str | None = None` (búsqueda en el título — `q.lower() in titulo.lower()`).
- `limit: int = Query(default=10, ge=1, le=100)`.

Probá combinaciones desde `/docs`.

### 2.4. Headers

```python
from fastapi import Header


@app.get("/notas/whoami")
def whoami(x_user: str | None = Header(default=None)) -> dict[str, str]:
    return {"usuario": x_user or "anónimo"}
```

Probá con `curl`:
```bash
curl http://localhost:8001/notas/whoami -H "X-User: ana"
```

FastAPI normaliza headers a snake_case (`X-User` ↔ `x_user`). Es magia pero predecible.

### 2.5. Tags y agrupación en `/docs`

Si tenés muchas rutas, agrupalas:

```python
@app.get("/notas", tags=["notas"])
def listar(...): ...


@app.post("/notas", tags=["notas"])
def crear(...): ...
```

Recargá `/docs`. Las rutas aparecen colapsables bajo "notas".

## 3. Reto — Paginación con Page + sort

Implementá `GET /notas` con paginación seria:

- Query params: `page: int = 1`, `per_page: int = 20`, `sort: str = "id"` (puede ser `"id"`, `"titulo"`, `"-id"`, `"-titulo"` con `-` para descendente).
- Response: un `BaseModel` con `total`, `page`, `per_page`, `items: list[NotaResponse]`.
- Validá:
  - `page >= 1`, `per_page` entre 1 y 100 con `Query(ge=..., le=...)`.
  - `sort` debe estar en el set permitido — si no, 422 con `HTTPException`.
- Para datos: cargá 250 notas falsas al arrancar la app (`@app.on_event("startup")` o un `lifespan` moderno; para hoy `@app.on_event` está bien).

Pista del response model:

```python
class PageNotas(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[NotaResponse]
```

**Por qué este patrón importa:** cualquier API REST seria devuelve listas paginadas. La forma — `page`+`per_page` o `cursor` — varía pero la idea (no devolver 100k filas en una sola response) es universal. Y el `BaseModel` envoltorio te permite agregar metadata (`total`, `next_cursor`, `links`) sin romper a los clientes que ignoran lo que no conocen.

## 4. Sin aporte al integrador hoy

Esta sesión es práctica de framework. La S17 introduce DTOs Request/Response separados, exception handlers que traducen excepciones de dominio a HTTP, y entonces sí empezamos a ver el integrador con FastAPI encima.

---

Cuando termines, vuelve al README y responde las preguntas de auto-evaluación. Si todas se contestan sin dudar, S16 está consolidada y puedes pasar a [S17 — Validación + DTOs + errores HTTP](../sesion-17-validacion-dtos/README.md).
