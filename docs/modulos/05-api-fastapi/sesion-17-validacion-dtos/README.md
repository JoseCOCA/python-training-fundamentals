# S17 — Validación con pydantic, DTOs, manejo de errores HTTP

> **Sesión 2h.** ~45 min lectura + ~75 min ejercicios. En S16 viste que un `BaseModel` en la firma del handler valida la entrada. Hoy le agregamos disciplina: **modelos distintos para entrada y salida** (request DTO ≠ response DTO ≠ ORM model), validaciones más finas con `Field` y validators, errores HTTP idiomáticos y un **exception handler** que traduce excepciones de tu dominio a respuestas HTTP apropiadas. Con esto la API se vuelve **un contrato claro** que clientes y servidor respetan, y los errores dejan de ser sorpresas.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Diseñar **tres modelos paralelos** para una misma entidad: el modelo de **persistencia** (ORM), el modelo de **request** (lo que el cliente manda) y el modelo de **response** (lo que el servidor devuelve).
- Justificar por qué los tres son distintos — no es duplicación, es separación de responsabilidades.
- Usar `Field` con validaciones (`min_length`, `gt`, `pattern`, `examples`, `description`) y `field_validator` para reglas de dominio.
- Configurar `model_config` para `from_attributes=True` y mapear directo desde objetos ORM.
- Capturar errores de validación pydantic y devolverlos al cliente con el detalle por campo.
- Definir **exception handlers globales** con `@app.exception_handler(...)` para convertir excepciones de tu dominio (`ProductoNoEncontrado`, `IntegracionError`) en respuestas HTTP correctas.
- Decidir el **status code** correcto para cada situación (200 / 201 / 204 / 400 / 404 / 409 / 422 / 500).

## 2. Prerequisitos

- [S16 — FastAPI fundamentos](../sesion-16-fastapi-fundamentos/README.md). Tenés que tener fluidez con rutas y `BaseModel` en la firma.
- [S11 — pydantic v2](../../03-tipado-calidad/sesion-11-pydantic-ruff/README.md). Vamos a hacer pydantic más serio: `Field`, validators, `model_config`.
- [S15 — SQLAlchemy v2](../../04-async-http-persistencia/sesion-15-sqlalchemy/README.md). Vamos a mapear request DTO ↔ ORM ↔ response DTO.

## 3. Conceptos clave

1. **DTO (Data Transfer Object).** Modelo cuyo único propósito es viajar **entre dos capas** de tu sistema (cliente ↔ API ↔ DB). No tiene métodos de negocio, no tiene ORM, no tiene relaciones complejas — solo campos.
2. **Request DTO vs Response DTO.** El cliente manda **menos campos** de los que recibe (no manda `id`, no manda `creado_en`). El response trae campos calculados o relaciones.
3. **`from_attributes=True`.** Configuración de pydantic que permite construir un modelo desde un **objeto** (ORM) leyendo atributos, no desde un `dict`. Antes se llamaba `orm_mode = True` (v1).
4. **Exception handler.** Función decorada con `@app.exception_handler(ExceptionClass)` que recibe la excepción y devuelve una `JSONResponse`. Es la forma idiomática de convertir errores de dominio a errores HTTP.
5. **Idempotencia.** `GET`, `PUT`, `DELETE` son idempotentes (ejecutarlos N veces tiene el mismo efecto que ejecutarlos 1 vez). `POST` no lo es. Un buen diseño REST honra esa convención.

## 4. Teoría

### 4.1. Por qué tres modelos para una sola entidad

Tomá `Producto`. Si tuviste un solo modelo para todo, terminás con:

```python
class Producto(BaseModel):
    id: int                      # ¿quién lo asigna? El servidor. → no debería estar en el request.
    nombre: str
    categoria: str
    precio: float
    stock: int = 0
    creado_en: datetime           # ídem.
    creado_por: str               # campo interno, NO debería viajar al cliente.
    descripcion_seo: str           # solo se setea desde el admin.
```

Cuando el cliente hace `POST /productos`, ¿manda `id`? ¿manda `creado_en`? ¿manda `creado_por`? Si declarás un solo modelo, o son **opcionales en todos lados** (y bugs aparecen al asumir que están), o **el cliente manda basura** que ignorás silenciosamente, o **filtrás campos internos al cliente** sin querer.

La solución es **separar**:

```python
# 1. El modelo de DB (S15) — tiene tags relacionales, métodos lazy
class ProductoORM(Base):
    __tablename__ = "producto"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str]
    categoria: Mapped[str]
    precio: Mapped[float]
    stock: Mapped[int]
    creado_en: Mapped[datetime]
    creado_por: Mapped[str]


# 2. Lo que el CLIENTE puede mandar
class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str
    precio: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)


# 3. Lo que el SERVIDOR devuelve
class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int
    creado_en: datetime
```

`ProductoCrear` no tiene `id` (lo asigna el servidor) ni `creado_en`. `ProductoOut` no tiene `creado_por` (es interno). El ORM tiene todo.

**No es duplicación.** Cada modelo cumple una función distinta y representa una **frontera** distinta:

| Modelo | Frontera | Propósito |
|---|---|---|
| `ProductoORM` | DB ↔ Python | Persistir; relaciones; queries |
| `ProductoCrear` | Cliente → API | Validar entrada |
| `ProductoOut` | API → Cliente | Filtrar campos; documentar contrato |

### 4.2. `Field` para validar fino

```python
from pydantic import BaseModel, Field


class ProductoCrear(BaseModel):
    nombre: str = Field(
        min_length=1,
        max_length=120,
        description="Nombre visible del producto",
        examples=["Cable USB-C", "Mouse Inalámbrico"],
    )
    categoria: str = Field(
        pattern=r"^[a-záéíóúñ ]+$",
        description="Solo letras y espacios",
    )
    precio: float = Field(gt=0, le=1_000_000, description="En USD")
    stock: int = Field(ge=0, default=0)
```

Cada `Field`:
- Aplica la validación (FastAPI devuelve 422 si falla).
- Aparece en `/docs` con `description` y `examples`.
- Forma parte del JSON Schema generado.

### 4.3. `field_validator` para reglas de dominio

Para reglas que `Field` no expresa:

```python
from pydantic import field_validator


class ProductoCrear(BaseModel):
    nombre: str
    categoria: str
    precio: float

    @field_validator("nombre")
    @classmethod
    def nombre_normalizado(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("nombre no puede estar vacío")
        return v.title()        # Capitalize Words

    @field_validator("categoria")
    @classmethod
    def categoria_minuscula(cls, v: str) -> str:
        return v.strip().lower()
```

Patrón: el validator **normaliza Y valida**. Devuelve el valor limpio para que el resto del código no tenga que volver a normalizar.

### 4.4. `from_attributes=True`: mapear ORM → DTO

```python
class ProductoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    categoria: str
    precio: float
    stock: int


# en el handler:
@app.get("/productos/{id}")
def obtener(id: int) -> ProductoOut:
    orm = repositorio.obtener(id)        # ProductoORM
    return ProductoOut.model_validate(orm)
```

`from_attributes=True` le dice a pydantic: "si te pasan un objeto en lugar de un dict, leé los atributos por nombre". Sin esto, `model_validate(orm)` falla.

Lo mismo con listas:

```python
@app.get("/productos")
def listar() -> list[ProductoOut]:
    rows = repositorio.todos()                              # list[ProductoORM]
    return [ProductoOut.model_validate(r) for r in rows]
```

(Si tu pipeline siempre va `request DTO → ORM → response DTO`, podés extraer las conversiones a funciones libres y no contaminar los handlers.)

### 4.5. Validación: cuándo usar `Field` y cuándo `field_validator`

| Necesidad | Herramienta |
|---|---|
| `min_length`, `max_length`, `min_value`, `max_value` | `Field(...)` |
| Pattern regex simple (email, slug) | `Field(pattern=...)` |
| Validar contra una **lista enumerada** (`Literal["bajo", "medio", "alto"]`) | tipo `Literal` directo |
| Reglas que cruzan campos | `model_validator(mode="after")` |
| Normalización (strip, lowercase, title) | `field_validator(...)` |
| Reglas de negocio complejas (precio < 1000 si categoria == "X") | `model_validator` |

Como dijo S11: **`Field` para forma, validators para semántica**.

### 4.6. Errores HTTP idiomáticos

| Status | Cuándo | Quién lo emite |
|---|---|---|
| **422** | Validación pydantic falla | FastAPI automático |
| **400** | Request "rara" pero parsea bien (querys mal combinados, formato distinto) | Vos con `HTTPException(400)` |
| **401** | Falta autenticación | Middleware o dep de auth |
| **403** | Autenticado pero sin permiso | `HTTPException(403)` |
| **404** | El recurso no existe | `HTTPException(404)` |
| **409** | Conflicto: el recurso ya existe, o estado incompatible | `HTTPException(409)` |
| **500** | Bug del servidor | Excepciones no controladas (FastAPI emite 500 con detalle) |
| **502 / 503** | Tu servicio depende de otro que falló | Vos al traducir `IntegracionError` |

`HTTPException`:

```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="ya existe un producto con ese nombre",
)
```

### 4.7. Exception handlers: la pieza que ata todo

Tu código de **dominio** lanza excepciones de dominio (`ProductoNoEncontrado`, `IntegracionError`, ...). Tus handlers no deberían convertir cada uno a `HTTPException` a mano. Mejor:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

from tiendapro import IntegracionError, ProductoNoEncontrado, TiendaProError


@app.exception_handler(ProductoNoEncontrado)
async def producto_no_encontrado_handler(
    request: Request, exc: ProductoNoEncontrado
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(IntegracionError)
async def integracion_handler(
    request: Request, exc: IntegracionError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": "servicio externo no disponible", "info": str(exc)},
    )


@app.exception_handler(TiendaProError)            # fallback genérico
async def tiendapro_handler(
    request: Request, exc: TiendaProError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )
```

Ahora tu handler queda limpio:

```python
@app.get("/productos/{id}")
def obtener(id: int) -> ProductoOut:
    orm = repositorio.obtener(id)        # puede tirar ProductoNoEncontrado
    return ProductoOut.model_validate(orm)
```

**Sin `try/except` en cada handler.** El exception handler global cacha la excepción y arma el response. Esto es **separación de responsabilidades** real: el dominio levanta, la API traduce.

### 4.8. Personalizar el handler de validación

FastAPI ya devuelve 422 con el detalle de los errores de pydantic, pero a veces querés un formato distinto (más amigable, con códigos de tu dominio):

```python
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validacion_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errores = [
        {
            "campo": ".".join(str(x) for x in e["loc"][1:]),
            "mensaje": e["msg"],
            "tipo": e["type"],
        }
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "datos inválidos", "errores": errores},
    )
```

Antes:
```json
{"detail": [{"loc": ["body", "precio"], "msg": "Input should be greater than 0", "type": "..."}]}
```

Después:
```json
{"detail": "datos inválidos", "errores": [{"campo": "precio", "mensaje": "Input should be greater than 0", "tipo": "..."}]}
```

Útil cuando integrás con clientes (mobile, frontend) que prefieren tu formato.

### 4.9. Idempotencia: el matiz que separa una API correcta

| Método | Idempotente | Crea recurso |
|---|---|---|
| `GET` | ✅ | ❌ |
| `POST` | ❌ | ✅ |
| `PUT` | ✅ | A veces (con id sugerido) |
| `PATCH` | depende | ❌ |
| `DELETE` | ✅ | ❌ |

**Idempotente** = ejecutar 5 veces es lo mismo que ejecutarlo 1 vez. Por eso un cliente que pierde la respuesta de un `GET` o `DELETE` puede reintentar sin miedo. Un `POST` no — podés crear el mismo pedido cinco veces.

En la práctica: si tu cliente reintenta `POST /pedidos` y dos veces se procesa, tenés un pedido duplicado. El antídoto es la **idempotency key**: el cliente manda un header `Idempotency-Key: <uuid>` y el servidor garantiza que dos requests con la misma key producen el mismo efecto. (No lo cubrimos en el curso pero quedá la idea.)

### 4.10. Lo mínimo a recordar

```
Cliente → API
         ↓ Request DTO   (validación, normalización)
         ↓ → función de dominio (puede lanzar excepción de dominio)
         ↓ → ORM (persistencia)
         ↓ ← función de dominio (devuelve ORM)
         ↓ ← Response DTO  (filtra, agrega computados)
         ↓
Cliente ← API

Si algo falla, exception handler global → JSON con status apropiado.
```

Ese pipeline es la columna del integrador del módulo.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| Tres modelos: ORM, RequestDTO, ResponseDTO | Un solo `Producto` que vale para todo |
| `from_attributes=True` para mapear desde ORM | Construir el DTO campo por campo en cada handler |
| `Field(min_length=..., gt=..., pattern=...)` | Validaciones a mano dentro del handler |
| `field_validator` para normalización | Normalizar dos veces (al recibir y al guardar) |
| Excepciones de dominio + exception handler global | `try/except HTTPException` en cada handler |
| `HTTPException(404)` para "no existe" | Devolver `{"error": "..."}` con status 200 |
| Status codes correctos (201/204/409) | Todo 200 con `{"ok": false}` |
| `Idempotency-Key` en POST críticos (futuro) | Reintentos ciegos en POST |
| Documentar `examples=[...]` en `Field` | Docs vacías, "el cliente que adivine" |
| Modelos `frozen=True` cuando aplique | Modelos mutables que se modifican entre capas |

## 6. Conexión con el proyecto integrador

Hoy sí tocamos el integrador, parcialmente:

1. Crear `code/proyecto-integrador/src/tiendapro/api/` — un sub-paquete con la API.
2. Definir `dtos.py` con `ProductoCrear`, `ProductoOut`, `ProductoListaOut`.
3. Crear `app.py` con la `FastAPI()` y un endpoint mínimo (`GET /productos`).
4. Configurar exception handlers que traducen `TiendaProError` → HTTP.

**No cerramos el hito M5 todavía** — eso ocurre en S18 con `pydantic-settings` y logging estructurado.

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **Tres modelos por entidad**: ORM (DB), RequestDTO (entrada), ResponseDTO (salida).
2. **`Field` valida forma; `field_validator` valida (y normaliza) semántica.**
3. **`from_attributes=True`** te deja construir un DTO directo desde un objeto ORM.
4. **`HTTPException`** para errores con status code y mensaje.
5. **`@app.exception_handler(...)`** convierte excepciones de tu dominio a respuestas HTTP. Tu handler queda **sin `try/except`**.
6. **Status codes idiomáticos**: 201 al crear, 204 al borrar, 404 cuando no existe, 409 en conflictos, 422 en validación pydantic, 4xx vos, 5xx servidor o servicio externo.
7. **Idempotencia**: GET/PUT/DELETE seguros para reintentar; POST no — usá `Idempotency-Key` en producción.
8. **El pipeline es siempre el mismo**: RequestDTO → dominio → ORM → ResponseDTO. Excepciones del dominio se traducen automáticamente.

## 8. Preguntas de auto-evaluación

1. ¿Por qué tener `ProductoCrear` y `ProductoOut` separados, en vez de un solo `Producto`? Da dos razones.
2. ¿Qué hace `model_config = ConfigDict(from_attributes=True)` y cuándo lo usás?
3. Diferencia entre validar con `Field(...)` y `field_validator`. Da un ejemplo de cada caso.
4. ¿Qué status code devolverías para cada uno? POST que crea, DELETE exitoso, recurso no encontrado, validación pydantic falló, conflicto al crear, error en un servicio externo del que dependés.
5. ¿Qué hace `@app.exception_handler(ProductoNoEncontrado)` y qué evita escribir en cada handler?
6. ¿Cómo escribís un handler que lanza `ProductoNoEncontrado` y devuelve 404? ¿Cuántas líneas son?
7. ¿Qué métodos HTTP son idempotentes? ¿Por qué importa?
8. Tu API recibe `{"precio": -10}` en un POST. ¿Quién y cómo detecta el error? ¿Qué status code llega al cliente?
9. Cuando devolvés un `ProductoORM` desde un handler tipado `-> ProductoOut`, ¿qué hace FastAPI por vos?
10. ¿Por qué evitamos `try/except` adentro de los handlers?

Cuando puedas responder todas, pasa a [`ejercicios.md`](ejercicios.md).
