# S21 — Ejercicios

> **Tiempo estimado:** ~70 min. Tres bloques: ejercicio guiado en un sandbox (calculadora de descuentos + mini-API), libres para profundizar (coverage, fixtures con teardown, marks), y **CIERRE DEL HITO M6 y DEL CURSO**: suite de tests del integrador, README final, tag `proyecto-m6`.

---

## 0. Antes de empezar

Tu sandbox vive en `code/m06-herramientas-ingeniero/sesion-21/`. Adentro hay:

- `descuentos.py` — módulo con funciones puras para testear (calculadora de descuentos).
- `mini_api.py` — mini-app FastAPI con un par de endpoints.
- `tests/` — placeholder; los vas a llenar vos.

```bash
cd code/m06-herramientas-ingeniero/sesion-21
uv sync
uv run pytest          # debería decir "no tests ran" o similar — todavía no escribiste ninguno
```

## 1. Ejercicio guiado — Calculadora de descuentos + TestClient

### Paso 1.1 — Tu primer test unit

Creá `tests/test_descuentos.py`:

```python
from descuentos import aplicar_descuento


def test_aplicar_descuento_reduce_precio() -> None:
    final = aplicar_descuento(100.0, 20)
    assert final == 80.0


def test_aplicar_descuento_cero_devuelve_mismo_precio() -> None:
    final = aplicar_descuento(50.0, 0)
    assert final == 50.0
```

Corré:

```bash
uv run pytest -v
```

Deberías ver dos tests verdes. Mirá el output: pytest descubre el archivo (`test_*.py`), las funciones (`test_*`), y reporta cada una.

### Paso 1.2 — Test que falla a propósito

Sumale un caso con expectativa errónea:

```python
def test_descuento_excesivo_falla_a_proposito() -> None:
    final = aplicar_descuento(100.0, 50)
    assert final == 999.0     # falso adrede
```

Corré `uv run pytest -v`. Mirá el output del fallo: pytest te muestra el `assert`, los valores reales, y resalta la línea. Ese es el feedback que te enamora del `assert` plano.

Después borrá ese test (era para ver el error message).

### Paso 1.3 — `pytest.raises` para verificar excepciones

Sumá:

```python
import pytest


def test_porcentaje_negativo_levanta_value_error() -> None:
    with pytest.raises(ValueError, match="porcentaje"):
        aplicar_descuento(100.0, -5)


def test_porcentaje_mayor_a_100_levanta_value_error() -> None:
    with pytest.raises(ValueError):
        aplicar_descuento(100.0, 150)
```

Corré. Si `descuentos.aplicar_descuento` no valida el rango, los tests fallan — esa es tu pista para robustecer la función.

Mirá `descuentos.py`: la función ya valida. Los tests pasan.

### Paso 1.4 — Fixture para reutilizar setup

Cuando varios tests necesitan el mismo dato, una fixture evita repetirlo:

```python
import pytest

from descuentos import aplicar_descuento, Carrito


@pytest.fixture
def carrito_con_items() -> Carrito:
    c = Carrito()
    c.agregar("camisa", 50.0)
    c.agregar("pantalón", 80.0)
    return c


def test_carrito_total(carrito_con_items: Carrito) -> None:
    assert carrito_con_items.total() == 130.0


def test_carrito_aplica_descuento_al_total(carrito_con_items: Carrito) -> None:
    assert carrito_con_items.total_con_descuento(10) == 117.0
```

`pytest` descubre el parámetro `carrito_con_items`, busca una fixture con ese nombre, la corre y le pasa el resultado al test. Una vez por test (scope default).

### Paso 1.5 — Parametrizar para muchos casos

Probá la función con varios inputs en un solo test:

```python
@pytest.mark.parametrize("precio,porcentaje,esperado", [
    (100.0, 10, 90.0),
    (100.0, 25, 75.0),
    (100.0, 0, 100.0),
    (50.0, 50, 25.0),
    (200.0, 100, 0.0),
])
def test_aplicar_descuento_varios_casos(
    precio: float, porcentaje: int, esperado: float
) -> None:
    assert aplicar_descuento(precio, porcentaje) == esperado
```

Corré con `-v`: vas a ver **cinco** tests, uno por tupla. Si uno falla, los demás siguen. Eso es valor concreto sobre copy-paste.

### Paso 1.6 — Mock con `monkeypatch`: aislar dependencias

`descuentos.py` tiene una función `precio_con_iva` que llama a una "tasa actual" externa. En tests no querés depender de la tasa real; la mockeás:

```python
import pytest

from descuentos import precio_con_iva


def test_precio_con_iva_usa_tasa_mockeada(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange — pisamos la función que devuelve la tasa
    monkeypatch.setattr("descuentos.tasa_iva_actual", lambda: 0.21)

    # Act
    resultado = precio_con_iva(100.0)

    # Assert
    assert resultado == 121.0
```

`monkeypatch.setattr` parcha y revierte automáticamente al final del test. Si hicieras `descuentos.tasa_iva_actual = lambda: 0.21` directo, te quedaría pisado para los siguientes tests — ahí salen los flakies.

### Paso 1.7 — `TestClient` de FastAPI

Probá `mini_api.py` levantándola normal:

```bash
uv run uvicorn mini_api:app --port 8001 --reload
# en otra terminal:
curl http://localhost:8001/saludo
curl http://localhost:8001/eco?msg=hola
```

Frenala con `Ctrl+C`. Ahora testealo **sin** servidor:

Creá `tests/test_mini_api.py`:

```python
from fastapi.testclient import TestClient
from mini_api import app

client = TestClient(app)


def test_saludo_devuelve_200() -> None:
    response = client.get("/saludo")
    assert response.status_code == 200
    assert response.json() == {"mensaje": "hola"}


def test_eco_repite_el_mensaje() -> None:
    response = client.get("/eco", params={"msg": "ping"})
    assert response.status_code == 200
    assert response.json()["dijiste"] == "ping"


def test_eco_sin_param_devuelve_422() -> None:
    response = client.get("/eco")
    assert response.status_code == 422
```

Corré `uv run pytest -v`. Tres tests más, todos verdes. **Ningún uvicorn corriendo, ningún puerto abierto.** TestClient ejecuta la app en proceso.

### Paso 1.8 — Reflexión

Antes de seguir:

- ¿Por qué usar `monkeypatch` en lugar de pisar el atributo a mano?
- ¿Por qué `TestClient` es preferible a levantar uvicorn y pegarle con `httpx`?
- ¿Qué ganás parametrizando un test sobre escribir cinco tests separados?

## 2. Ejercicios libres

### 2.1. Coverage local

```bash
uv add --dev pytest-cov
uv run pytest --cov=descuentos --cov=mini_api --cov-report=term-missing
```

Mirá la salida. ¿Hay líneas en `Missing`? ¿Qué casos te falta cubrir? Sumalos como tests (o decidí que ese branch no merece test y dejá un comentario).

### 2.2. Fixture con `yield` y teardown

Si tu test necesita un archivo temporal, podés usar la fixture builtin `tmp_path`:

```python
from pathlib import Path


def test_lee_archivo(tmp_path: Path) -> None:
    archivo = tmp_path / "datos.txt"
    archivo.write_text("hola")
    contenido = archivo.read_text()
    assert contenido == "hola"
    # tmp_path se borra solo al terminar el test
```

O hacela vos mismo con `yield`:

```python
import pytest
from collections.abc import Iterator
from pathlib import Path


@pytest.fixture
def archivo_de_config(tmp_path: Path) -> Iterator[Path]:
    path = tmp_path / "config.json"
    path.write_text('{"key": "value"}')
    yield path
    # teardown automático: tmp_path se limpia, no hace falta borrar manualmente
```

### 2.3. Marks: `skip`, `xfail`, `slow`

```python
import pytest


@pytest.mark.skip(reason="no implementado todavía")
def test_a_implementar() -> None:
    assert False


@pytest.mark.skipif(not_disponible(), reason="depende de un binario externo")
def test_solo_si_hay_binario() -> None:
    ...


@pytest.mark.xfail(reason="bug conocido, esperando el fix")
def test_esperado_a_fallar() -> None:
    assert 1 == 2
```

Y para tags propios:

```python
@pytest.mark.slow
def test_que_tarda() -> None:
    ...
```

Filtrar:

```bash
uv run pytest -m "not slow"     # corre todo menos los slow
uv run pytest -m slow           # solo los slow
```

(Necesitás registrar el mark en `pyproject.toml` para que no haya warnings: `markers = ["slow: tests lentos"]`.)

### 2.4. `conftest.py` para fixtures compartidas

Si las mismas fixtures las usás en dos archivos de test, moverlas a `tests/conftest.py` las hace disponibles **automáticamente** sin import:

```python
# tests/conftest.py
import pytest
from descuentos import Carrito


@pytest.fixture
def carrito_vacio() -> Carrito:
    return Carrito()
```

Y en cualquier `test_*.py` debajo de `tests/` podés pedirla por nombre. Cero import, pytest la encuentra sola.

### 2.5. Configuración de pytest en `pyproject.toml`

Agregá al `pyproject.toml` del sandbox:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
markers = [
    "slow: tests lentos",
]
```

`--strict-markers` hace que pytest falle si usás un mark no declarado. Útil contra typos.

## 3. Aporte al proyecto integrador — CIERRE DEL HITO M6 Y DEL CURSO

**Hoy cierra el Módulo 6 y el curso completo.** Vamos a sumar la suite de tests, generar coverage, actualizar el README final del integrador y taguear `proyecto-m6`.

### 3.1. Sumar pytest al integrador

Editá `code/proyecto-integrador/pyproject.toml` y sumá las deps de testing:

```toml
[dependency-groups]
dev = [
    "ruff>=0.6.0",
    "mypy>=1.11.0",
    "pytest>=8.3.0",
    "pytest-cov>=5.0.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q --strict-markers"
pythonpath = ["src"]
```

```bash
cd code/proyecto-integrador
uv sync --all-groups
```

`pythonpath = ["src"]` le dice a pytest "los imports tipo `from tiendapro.modelos import ...` se resuelven desde `src/`". Sin esto, los tests no encuentran el paquete (porque `src/` no está en el path por default de pytest).

### 3.2. `tests/conftest.py` — fixtures compartidas

Creá `code/proyecto-integrador/tests/__init__.py` vacío y después `code/proyecto-integrador/tests/conftest.py`:

```python
"""Fixtures compartidas para toda la suite del integrador."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from tiendapro.api.app import app
from tiendapro.config import Settings, get_settings
from tiendapro.modelos import Producto
from tiendapro.orm import Base


# ---------------------------------------------------------------------------
# Settings de test (DB en memoria, sin enriquecimiento HTTP)
# ---------------------------------------------------------------------------


@pytest.fixture
def settings_test() -> Settings:
    return Settings(
        app_name="TiendaPro-test",
        debug=True,
        database_url="sqlite:///:memory:",
        log_level="WARNING",
        enable_enrichment=False,
        cors_origins=["http://test"],
    )


# ---------------------------------------------------------------------------
# Engine y sesión SQLAlchemy con SQLite en memoria
# ---------------------------------------------------------------------------


@pytest.fixture
def engine() -> Iterator[Engine]:
    e = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(e)
    yield e
    e.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    s = Session(engine)
    try:
        yield s
    finally:
        s.rollback()
        s.close()


# ---------------------------------------------------------------------------
# Cliente HTTP en proceso para integration tests de la API
# ---------------------------------------------------------------------------


@pytest.fixture
def client(
    settings_test: Settings, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[TestClient]:
    # Aislamos la DB de cada test usando un archivo temporal — SQLite en memoria
    # NO se comparte entre conexiones distintas, lo que rompería el lifespan.
    db_path = tmp_path / "test.db"
    settings_aislado = settings_test.model_copy(
        update={"database_url": f"sqlite:///{db_path}"}
    )

    app.dependency_overrides[get_settings] = lambda: settings_aislado
    monkeypatch.setattr("tiendapro.config.get_settings", lambda: settings_aislado)

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Datos de dominio
# ---------------------------------------------------------------------------


@pytest.fixture
def producto_base() -> Producto:
    return Producto(
        nombre="Cable USB-C",
        categoria="cables",
        precio=15.0,
        stock=10,
    )
```

### 3.3. Tests unit

Creá `code/proyecto-integrador/tests/unit/__init__.py` (vacío) y `code/proyecto-integrador/tests/unit/test_modelos.py`:

```python
"""Tests unit del modelo de dominio Producto."""

import pytest
from pydantic import ValidationError

from tiendapro.modelos import Producto


class TestProductoValidaciones:
    def test_se_construye_con_datos_validos(self) -> None:
        p = Producto(nombre="Cable", categoria="cables", precio=10.0, stock=1)
        assert p.nombre == "Cable"
        assert p.precio == 10.0

    def test_es_inmutable(self) -> None:
        p = Producto(nombre="Cable", categoria="cables", precio=10.0, stock=1)
        with pytest.raises(ValidationError):
            p.precio = 99.0  # type: ignore[misc]

    def test_rechaza_precio_negativo(self) -> None:
        with pytest.raises(ValidationError, match="precio"):
            Producto(nombre="X", categoria="c", precio=-1.0, stock=1)

    def test_rechaza_precio_cero(self) -> None:
        with pytest.raises(ValidationError, match="precio"):
            Producto(nombre="X", categoria="c", precio=0.0, stock=1)

    def test_rechaza_stock_negativo(self) -> None:
        with pytest.raises(ValidationError, match="stock"):
            Producto(nombre="X", categoria="c", precio=10.0, stock=-1)

    def test_rechaza_nombre_vacio(self) -> None:
        with pytest.raises(ValidationError):
            Producto(nombre="   ", categoria="c", precio=10.0, stock=1)

    def test_rechaza_campos_extra(self) -> None:
        with pytest.raises(ValidationError):
            Producto(  # type: ignore[call-arg]
                nombre="X", categoria="c", precio=10.0, stock=1, color="rojo"
            )


class TestProductoComportamiento:
    @pytest.mark.parametrize("stock,esperado", [(5, True), (1, True), (0, False)])
    def test_disponible(self, stock: int, esperado: bool) -> None:
        p = Producto(nombre="X", categoria="c", precio=10.0, stock=stock)
        assert p.disponible() is esperado

    def test_valor_inventario_es_precio_por_stock(self) -> None:
        p = Producto(nombre="X", categoria="c", precio=12.5, stock=4)
        assert p.valor_inventario() == 50.0

    def test_default_moneda_usd(self) -> None:
        p = Producto(nombre="X", categoria="c", precio=1.0, stock=1)
        assert p.moneda == "USD"
```

Y `code/proyecto-integrador/tests/unit/test_dtos.py`:

```python
"""Tests unit de los DTOs de la API."""

import pytest
from pydantic import ValidationError

from tiendapro.api.dtos import HealthOut, ProductoCrear, ProductoOut


class TestProductoCrear:
    def test_acepta_input_minimo_valido(self) -> None:
        dto = ProductoCrear(nombre="Cable", categoria="cables", precio=10.0)
        assert dto.stock == 0  # default

    def test_normaliza_espacios_en_nombre(self) -> None:
        dto = ProductoCrear(nombre="  Cable  ", categoria="cables", precio=10.0)
        assert dto.nombre == "Cable"

    def test_rechaza_precio_cero(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=0.0)

    def test_rechaza_precio_negativo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=-1.0)

    def test_rechaza_precio_excesivo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=10_000_000.0)

    def test_rechaza_stock_negativo(self) -> None:
        with pytest.raises(ValidationError):
            ProductoCrear(nombre="X", categoria="c", precio=1.0, stock=-1)


def test_producto_out_serializa_correctamente() -> None:
    dto = ProductoOut(nombre="Cable", categoria="cables", precio=10.0, stock=5)
    assert dto.model_dump() == {
        "nombre": "Cable",
        "categoria": "cables",
        "precio": 10.0,
        "stock": 5,
    }


def test_health_out_acepta_estado_y_servicio() -> None:
    h = HealthOut(servicio="tiendapro", estado="ok", productos_en_db=42)
    assert h.estado == "ok"
    assert h.productos_en_db == 42
```

Y `code/proyecto-integrador/tests/unit/test_errores.py`:

```python
"""Tests unit de la jerarquía de excepciones de dominio."""

from tiendapro.errores import (
    CatalogoInvalido,
    IntegracionError,
    ProductoNoEncontrado,
    TiendaProError,
)


def test_jerarquia_completa_es_subclase_de_tiendapro_error() -> None:
    assert issubclass(CatalogoInvalido, TiendaProError)
    assert issubclass(ProductoNoEncontrado, TiendaProError)
    assert issubclass(IntegracionError, TiendaProError)


def test_tiendapro_error_es_subclase_de_exception() -> None:
    assert issubclass(TiendaProError, Exception)


def test_se_pueden_levantar_y_capturar() -> None:
    try:
        raise CatalogoInvalido("seed roto")
    except TiendaProError as e:
        assert str(e) == "seed roto"
```

### 3.4. Tests integration

Creá `code/proyecto-integrador/tests/integration/__init__.py` (vacío) y `code/proyecto-integrador/tests/integration/test_api_productos.py`:

```python
"""Integration tests de la API de productos contra una DB SQLite efímera."""

from fastapi.testclient import TestClient


def test_health_responde_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["estado"] == "ok"
    assert body["servicio"] == "tiendapro"
    assert isinstance(body["productos_en_db"], int)


def test_listar_productos_devuelve_array(client: TestClient) -> None:
    response = client.get("/productos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_crear_producto_ok(client: TestClient) -> None:
    payload = {
        "nombre": "Producto Test",
        "categoria": "test",
        "precio": 9.99,
        "stock": 5,
    }
    response = client.post("/productos", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Producto Test"
    assert body["precio"] == 9.99
    assert body["stock"] == 5

    # Verificación: ahora aparece en GET /productos
    listado = client.get("/productos").json()
    nombres = {p["nombre"] for p in listado}
    assert "Producto Test" in nombres


def test_crear_y_filtrar_por_categoria(client: TestClient) -> None:
    client.post(
        "/productos",
        json={"nombre": "Auricular A", "categoria": "audio", "precio": 50.0, "stock": 2},
    )
    client.post(
        "/productos",
        json={"nombre": "Auricular B", "categoria": "audio", "precio": 80.0, "stock": 1},
    )
    client.post(
        "/productos",
        json={"nombre": "Cable X", "categoria": "cables", "precio": 5.0, "stock": 10},
    )

    audio = client.get("/productos", params={"categoria": "audio"}).json()
    assert len(audio) >= 2
    assert all(p["categoria"] == "audio" for p in audio)


def test_filtro_solo_disponibles(client: TestClient) -> None:
    client.post(
        "/productos",
        json={"nombre": "Sin stock", "categoria": "x", "precio": 1.0, "stock": 0},
    )
    client.post(
        "/productos",
        json={"nombre": "Con stock", "categoria": "x", "precio": 1.0, "stock": 3},
    )

    disponibles = client.get("/productos", params={"solo_disponibles": "true"}).json()
    nombres = {p["nombre"] for p in disponibles}
    assert "Con stock" in nombres
    assert "Sin stock" not in nombres


def test_response_trae_x_request_id(client: TestClient) -> None:
    response = client.get("/health")
    assert "x-request-id" in {k.lower() for k in response.headers}
```

Y `code/proyecto-integrador/tests/integration/test_api_errores.py`:

```python
"""Integration tests del manejo de errores HTTP."""

from fastapi.testclient import TestClient


def test_payload_invalido_devuelve_422_con_formato_propio(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={"nombre": "", "categoria": "x", "precio": -1.0},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "datos inválidos"
    assert "errores" in body
    assert isinstance(body["errores"], list)
    assert len(body["errores"]) >= 1
    error = body["errores"][0]
    assert {"campo", "mensaje", "tipo"} <= set(error.keys())


def test_campo_extra_es_rechazado(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={
            "nombre": "X",
            "categoria": "c",
            "precio": 1.0,
            "color": "rojo",  # campo extra
        },
    )
    assert response.status_code == 422


def test_precio_excesivo_es_422(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={"nombre": "X", "categoria": "c", "precio": 9_999_999.0},
    )
    assert response.status_code == 422
```

### 3.5. Correr la suite

```bash
cd code/proyecto-integrador
uv run pytest
```

Si hay fallos, leé el output, ajustá. **No avances con la suite roja.**

Cuando todo esté verde:

```bash
uv run pytest --cov=src/tiendapro --cov-report=term-missing
```

Mirá el porcentaje. Apuntá a >80% en módulos importantes (`modelos`, `dtos`, `repositorio`, `api`). Las líneas **Missing** son los caminos que ningún test ejercita — podés sumar tests extra o aceptar el hueco con justificación.

### 3.6. Verificar todo (mypy + ruff + pytest)

```bash
uv run mypy src/ main.py
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Los cuatro tienen que pasar limpio.

### 3.7. Actualizar el README del integrador

Editá `code/proyecto-integrador/README.md` para reflejar el cierre del curso. Cambios principales:

- Sección **Estado actual** ahora habla de M6 (no M5).
- Tabla de hitos: `M6 (aquí estamos)`.
- Lista de capacidades: sumá "tests con pytest", "Dockerfile + docker-compose", "coverage >80%".
- Sección **Verificación** incluye `uv run pytest` y `uv run pytest --cov=...`.
- Una sección final **"¿Qué sigue?"** que apunta al curso 2 (`python-ai-engineer-training`).

Ejemplo de bloque para el final:

```markdown
## ¿Qué sigue?

**Felicitaciones — terminaste el curso `python-training-fundamentals`.**

Ahora pasás a [`python-ai-engineer-training`](https://github.com/JoseCOCA/python-ai-engineer-training),
donde TiendaPro Lite (este mismo proyecto) deja de ser un e-commerce de juguete y se
convierte en un sistema con capacidades de IA: búsqueda semántica de productos,
recomendaciones por embeddings, agentes que orquestan llamadas a LLMs sobre el
catálogo, RAG sobre la documentación interna.

La disciplina que construiste acá — config por entorno, logs estructurados, tests,
Docker, git limpio — es **el fundamento** sobre el que se va a parar todo eso. Sin
ella, el código de IA es un script de demo que se rompe en producción a las 1000
requests.
```

### 3.8. Actualizar curriculum

En `docs/00-curriculum.md`:

```markdown
- [x] Módulo 6 — Herramientas del ingeniero (3 sesiones) — tag `proyecto-m6`
```

### 3.9. Commit final + tag — CIERRE M6 Y CIERRE DEL CURSO

```bash
git add code/proyecto-integrador docs/00-curriculum.md
git commit -m "feat(proyecto-integrador): cierra M6 con tests pytest (proyecto-m6)"
git tag proyecto-m6
git push origin main
git push origin proyecto-m6
```

### 3.10. Felicitaciones

**Terminaste el curso.**

TiendaPro Lite ahora es:

- Una **API REST funcional** con CRUD de productos, filtros y health check.
- **Configurable por entorno** sin tocar código (pydantic-settings + .env).
- Con **logging estructurado** y `request_id` por request.
- Con **exception handling** que traduce excepciones de dominio a HTTP correctos.
- **Dockerizada** y orquestable con compose (app + Postgres).
- **Cubierta por tests** unit + integration con pytest.
- Con **mypy estricto** y **ruff** limpios.
- Con **historia de git** legible y Conventional Commits.

Eso es **código de producción**. Llevátelo a un equipo, pasá la entrevista mostrándolo, ponelo de portfolio. **Es trabajo serio.**

Y desde acá arranca el curso 2.

---

Cuando termines, volvé al [README](README.md) y respondé las preguntas de auto-evaluación. Si todas se contestan sin dudar, **estás listo para `python-ai-engineer-training`**.
