# TiendaPro Lite — Proyecto integrador

API REST de e-commerce que vas a construir a lo largo del curso, módulo a módulo. Al final del curso queda lista para producción (testeada con pytest, empaquetada en Docker, persistida en PostgreSQL).

Es **el mismo producto** sobre el que arranca el curso 2 ([`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training)). Cuando termines este curso vas a tomar este código tal como está y empezar a sumarle capacidades de IA encima.

---

## Estado actual: hito M4

A partir del hito M4 TiendaPro Lite **persiste en una base de datos** y **habla HTTP** con un servicio externo:

- **Persistencia con SQLAlchemy v2** (SQLite local en `tiendapro.db`, Postgres-ready: solo cambia la URL).
- **Modelos ORM** en `src/tiendapro/orm.py` con `DeclarativeBase`, `Mapped[T]` y `mapped_column`.
- **Modelos pydantic** mantenidos como DTOs de **borde** en `src/tiendapro/modelos.py` (Producto, Cliente, EnriquecimientoExterno).
- **`src/tiendapro/repositorio.py`** es el ÚNICO módulo que conoce SQLAlchemy. El resto del paquete trabaja con DTOs.
- **`src/tiendapro/db.py`** encapsula el engine y el `obtener_sesion()` (context manager con commit/rollback automáticos).
- **Cliente HTTP con `httpx.AsyncClient`** en `src/tiendapro/integraciones.py` que enriquece productos contra una "API externa" (mockeada con `httpx.MockTransport`).
- **asyncio + semáforo** limitan la concurrencia del enriquecimiento a 5 llamadas en vuelo.
- **mypy estricto** y **ruff** siguen pasando limpio.

Lo que **todavía no tiene** y se agrega en módulos siguientes:

| Módulo | Hito | Capacidades agregadas |
|--------|------|----------------------|
| M1 | `proyecto-m1` | Lee JSON, filtra, ordena, imprime |
| M2 | `proyecto-m2` | Catálogo modelado con dataclasses, errores de dominio, código en paquete |
| M3 | `proyecto-m3` | Validación pydantic, mypy estricto, ruff + pre-commit |
| **M4 (aquí estamos)** | `proyecto-m4` | SQLAlchemy v2 + httpx + asyncio donde aporta |
| M5 | `proyecto-m5` | API REST con FastAPI, validación, configuración |
| M6 | `proyecto-m6` | Tests con pytest, Dockerfile, README final |

---

## Cómo correrlo

Desde dentro de este directorio:

```bash
uv sync --all-groups        # solo la primera vez (instala httpx, sqlalchemy, etc.)
uv run python main.py
```

La primera ejecución crea `tiendapro.db` y siembra los productos desde `data/catalogo.json`. Las siguientes ejecuciones leen directamente de la DB.

**Para resetear la DB:**

```bash
rm tiendapro.db
```

(El archivo está en `.gitignore` por la regla `*.db`.)

## Salida esperada

```
Productos en DB: 10

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

Enriquecimiento (API externa):
  Teclado Mecánico             ★4.7  Teclado mecánico con switches azules
  Auriculares Bluetooth        ★4.4  Auriculares con cancelación activa de ruido
  Monitor 4K                   ★4.5  Monitor 27" 4K UHD con HDR
```

(Los productos `Cable HDMI 2m` y `Webcam HD` no aparecen — su stock es 0. Solo tres productos vienen enriquecidos por la API mock; los demás se silencian con 404, que en este flujo es esperado.)

## Verificación de calidad

```bash
uv run mypy src/ main.py        # cero issues
uv run ruff check .              # cero issues
uv run ruff format --check .     # formato correcto
```

Los tres son la línea base de cualquier commit.

## Estructura

```
proyecto-integrador/
├── README.md                       ← este archivo
├── pyproject.toml                  ← deps + tool.ruff + tool.mypy
├── data/
│   └── catalogo.json               ← seed inicial (se importa una sola vez)
├── tiendapro.db                    ← SQLite local (no versionado)
├── main.py                         ← entry async + bootstrap + enriquecimiento
└── src/
    └── tiendapro/
        ├── __init__.py             ← re-exports públicos
        ├── modelos.py              ← DTOs pydantic (Producto, Cliente, Enriquecimiento)
        ├── errores.py              ← TiendaProError + sub-clases (incluye IntegracionError)
        ├── orm.py                  ← modelos SQLAlchemy v2 (ProductoORM, ClienteORM, ...)
        ├── db.py                   ← engine + obtener_sesion() context manager
        ├── repositorio.py          ← API de acceso a datos (único módulo con SQLAlchemy)
        ├── integraciones.py        ← cliente httpx para enriquecimiento
        ├── catalogo.py             ← API que el resto consume; delega en repositorio
        └── presentacion.py         ← imprimir_tabla, imprimir_resumen
```

## Cómo se construyó

Cada módulo agrega una capa.

- **M1** estableció las bases: leer datos, filtrarlos, ordenarlos, presentarlos.
- **M2** transformó el script en un paquete real: dataclasses inmutables (S08), excepciones de dominio (S07), `with` y generadores (S09).
- **M3** lo blindó con calidad: validación runtime con pydantic, mypy estricto, ruff y pre-commit.
- **M4 (este hito)** lo conecta con el mundo: persistencia con SQLAlchemy v2, integración HTTP con httpx, asyncio donde de verdad aporta. La separación **DTO pydantic (borde) ↔ ORM SQLAlchemy (DB)** es la pieza arquitectónica clave que vas a usar todo el camino restante.

## Para los alumnos

Si estás cursando el módulo y todavía no llegaste al final, **no leas el código de `src/tiendapro/` todavía**. Es la implementación de referencia. Primero implementa tú tu propia versión siguiendo los ejercicios del módulo correspondiente.

Después compárala con la referencia — vas a aprender más viendo las diferencias entre tu solución y la de referencia que mirando la referencia primero.
