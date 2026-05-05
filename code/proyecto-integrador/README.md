# TiendaPro Lite — Proyecto integrador

API REST de e-commerce que vas a construir a lo largo del curso, módulo a módulo. Al final del curso queda lista para producción (testeada con pytest, empaquetada en Docker, persistida en PostgreSQL).

Es **el mismo producto** sobre el que arranca el curso 2 ([`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training)). Cuando termines este curso vas a tomar este código tal como está y empezar a sumarle capacidades de IA encima.

---

## Estado actual: hito M2

Lo que hace el código en este momento (mismo comportamiento observable que M1, pero con una arquitectura sustancialmente mejor):

- Carga el catálogo desde `data/catalogo.json` con manejo correcto de archivos (`with`).
- Modela cada producto como `@dataclass(frozen=True)` — tipado, inmutable, comparable.
- Filtra los disponibles con un **generador** lazy.
- Los ordena por precio ascendente y los imprime en tabla.
- Calcula y muestra resumen: producto más barato, más caro, valor total del inventario.
- **Falla bien:** si el archivo no existe, el JSON está mal formado, la estructura no es la esperada o un producto está incompleto, lanza una excepción de dominio (`CatalogoInvalido`) con un mensaje útil. `main.py` la captura y muestra al usuario un error legible en lugar de un traceback.

**No** hay base de datos, **no** hay API REST, **no** hay tests todavía. Eso viene en módulos siguientes:

| Módulo | Hito | Capacidades agregadas |
|--------|------|----------------------|
| M1 | `proyecto-m1` | Lee JSON, filtra, ordena, imprime |
| **M2 (aquí estamos)** | `proyecto-m2` | Catálogo modelado con dataclasses, errores de dominio, código en paquete |
| M3 | `proyecto-m3` | Tipado con pydantic, mypy + ruff pasan limpio |
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

## Estructura

```
proyecto-integrador/
├── README.md                       ← este archivo
├── pyproject.toml                  ← proyecto uv configurado como paquete
├── data/
│   └── catalogo.json               ← productos de TiendaPro
├── main.py                         ← punto de entrada con manejo de errores
└── src/
    └── tiendapro/
        ├── __init__.py             ← re-exports públicos
        ├── modelos.py              ← Producto, Cliente (dataclasses)
        ├── errores.py              ← TiendaProError + sub-clases
        ├── catalogo.py             ← cargar (con `with`), disponibles (generador), ordenar
        └── presentacion.py         ← imprimir_tabla, imprimir_resumen
```

## Cómo se construyó

Cada módulo agrega una capa.

- **M1** estableció las bases: leer datos, filtrarlos, ordenarlos, presentarlos. Todo con las herramientas básicas del lenguaje y un único `main.py`.
- **M2 (este hito)** transforma ese script en un paquete real: modelos como dataclasses inmutables (S08), excepciones de dominio (S07) que reemplazan returns silenciosos, manejo correcto de archivos con `with` (S09) y generadores donde tienen sentido. El código pasa de "script" a "biblioteca".

## Para los alumnos

Si estás cursando el módulo y todavía no llegaste al final, **no leas el código de `src/tiendapro/` todavía**. Es la implementación de referencia. Primero implementa tú tu propia versión siguiendo los ejercicios del módulo correspondiente.

Después compárala con la referencia — vas a aprender más viendo las diferencias entre tu solución y la de referencia que mirando la referencia primero.
