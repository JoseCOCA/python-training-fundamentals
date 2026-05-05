# TiendaPro Lite — Proyecto integrador

API REST de e-commerce que vas a construir a lo largo del curso, módulo a módulo. Al final del curso queda lista para producción (testeada con pytest, empaquetada en Docker, persistida en PostgreSQL).

Es **el mismo producto** sobre el que arranca el curso 2 ([`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training)). Cuando termines este curso vas a tomar este código tal como está y empezar a sumarle capacidades de IA encima.

---

## Estado actual: hito M1

Lo que hace el código en este momento:

- Carga el catálogo desde `data/catalogo.json` (lista de productos con nombre, precio, stock, categoría).
- Filtra solo los productos con `stock > 0`.
- Los ordena por precio ascendente.
- Imprime una tabla legible.
- Calcula y muestra resumen: producto más barato, más caro, valor total del inventario.

**No** hay base de datos, **no** hay API REST, **no** hay tests todavía. Eso viene en módulos siguientes:

| Módulo | Hito | Capacidades agregadas |
|--------|------|----------------------|
| **M1 (aquí estamos)** | `proyecto-m1` | Lee JSON, filtra, ordena, imprime |
| M2 | `proyecto-m2` | Catálogo modelado con clases, errores manejados, código en módulos |
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
├── README.md            ← este archivo
├── pyproject.toml       ← proyecto uv
├── data/
│   └── catalogo.json    ← productos de TiendaPro
└── main.py              ← el script
```

## Cómo se construyó

Cada módulo agrega una capa. M1 establece las bases: leer datos, filtrarlos, ordenarlos, presentarlos. Todo con las herramientas básicas del lenguaje (variables, listas, dicts, funciones puras, f-strings). Sin librerías de terceros todavía — solo `json` y `pathlib` de la stdlib.

## Para los alumnos

Si estás cursando el M1 y todavía no llegaste a S05: **no leas `main.py` todavía**. Es la implementación de referencia. Primero impleméntala tú en `mi_solucion.py` siguiendo `docs/modulos/01-python-fundamentos/sesion-05-strings/ejercicios.md` § "Hito M1".

Después comparalas — vas a aprender más viendo las diferencias entre tu solución y la de referencia que mirando la referencia primero.
