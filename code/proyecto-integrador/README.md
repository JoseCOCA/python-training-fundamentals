# TiendaPro Lite — Proyecto integrador

API REST de e-commerce que vas a construir a lo largo del curso, módulo a módulo. Al final del curso queda lista para producción (testeada con pytest, empaquetada en Docker, persistida en PostgreSQL).

Es **el mismo producto** sobre el que arranca el curso 2 ([`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training)). Cuando termines este curso vas a tomar este código tal como está y empezar a sumarle capacidades de IA encima.

---

## Estado actual: hito M3

Mismo comportamiento observable que M1/M2, pero con todas las herramientas de calidad activadas:

- Modelos como **`pydantic.BaseModel`** inmutables, con `extra="forbid"` y validators (precio positivo, stock no negativo, nombre no vacío, email con formato).
- Carga del JSON pasa por `Producto.model_validate(...)`. Si los datos no encajan, `ValidationError` se traduce a `CatalogoInvalido` con mensaje detallado por campo.
- **mypy estricto** (`disallow_untyped_defs`, `no_implicit_optional`, plugin de pydantic) pasa limpio.
- **ruff** (`E/W/F/I/B/UP/RUF`) y **`ruff format`** pasan limpio.
- Filtrado lazy con generador, ordenamiento y presentación tipados.
- **Falla rápido y bien:** archivo inexistente, JSON malformado, estructura no-lista, producto que rompe una regla de negocio — todo se reporta con `CatalogoInvalido` legible. `main.py` la captura y devuelve código de salida 1.

**No** hay base de datos, **no** hay API REST, **no** hay tests todavía. Eso viene en módulos siguientes:

| Módulo | Hito | Capacidades agregadas |
|--------|------|----------------------|
| M1 | `proyecto-m1` | Lee JSON, filtra, ordena, imprime |
| M2 | `proyecto-m2` | Catálogo modelado con dataclasses, errores de dominio, código en paquete |
| **M3 (aquí estamos)** | `proyecto-m3` | Validación pydantic, mypy estricto, ruff + pre-commit |
| M4 | `proyecto-m4` | PostgreSQL + SQLAlchemy, modelos relacionales, cliente HTTP externo |
| M5 | `proyecto-m5` | API REST con FastAPI, validación, configuración |
| M6 | `proyecto-m6` | Tests con pytest, Dockerfile, README final |

---

## Cómo correrlo

Desde dentro de este directorio:

```bash
uv run python main.py
```

## Salida esperada

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

(Los productos `Cable HDMI 2m` y `Webcam HD` no aparecen — su stock es 0.)

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
│   └── catalogo.json               ← productos de TiendaPro
├── main.py                         ← punto de entrada con manejo de errores
└── src/
    └── tiendapro/
        ├── __init__.py             ← re-exports públicos
        ├── modelos.py              ← Producto, Cliente (BaseModel + validators)
        ├── errores.py              ← TiendaProError + sub-clases
        ├── catalogo.py             ← cargar (con `with`), disponibles (generador), ordenar
        └── presentacion.py         ← imprimir_tabla, imprimir_resumen
```

## Cómo se construyó

Cada módulo agrega una capa.

- **M1** estableció las bases: leer datos, filtrarlos, ordenarlos, presentarlos.
- **M2** transformó el script en un paquete real: dataclasses inmutables (S08), excepciones de dominio (S07), `with` y generadores (S09).
- **M3 (este hito)** lo blinda con calidad: validación runtime con pydantic y validators de dominio (S11), mypy estricto sobre todo el paquete (S10), ruff como linter y formatter del ecosistema, pre-commit para que nada de esto sea responsabilidad humana.

## Para los alumnos

Si estás cursando el módulo y todavía no llegaste al final, **no leas el código de `src/tiendapro/` todavía**. Es la implementación de referencia. Primero implementa tú tu propia versión siguiendo los ejercicios del módulo correspondiente.

Después compárala con la referencia — vas a aprender más viendo las diferencias entre tu solución y la de referencia que mirando la referencia primero.
