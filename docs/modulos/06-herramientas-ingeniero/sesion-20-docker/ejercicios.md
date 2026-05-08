# S20 — Ejercicios

> **Tiempo estimado:** ~70 min. Tres bloques: ejercicio guiado dockerizando una mini-app FastAPI + compose con Postgres, libres para refinar (multi-stage, healthcheck, usuario no-root), y **aporte al integrador**: Dockerfile + docker-compose.yml de TiendaPro Lite (sin cerrar el módulo todavía — eso ocurre en S21).

---

## 0. Antes de empezar

Verificá que Docker está corriendo:

```bash
docker run hello-world
```

Si te tira `permission denied` (Linux) probablemente tu usuario no está en el grupo `docker`. Solución temporal: `sudo docker ...`. Solución persistente: `sudo usermod -aG docker $USER` y volver a iniciar sesión.

Tu sandbox vive en `code/m06-herramientas-ingeniero/sesion-20/`. Adentro hay una app FastAPI mínima (`app.py`) que vas a dockerizar.

```bash
cd code/m06-herramientas-ingeniero/sesion-20
ls
# .dockerignore  app.py  docker-compose.yml  Dockerfile  pyproject.toml  README.md  uv.lock
```

(Si todavía no hay `uv.lock`, corré `uv sync` desde el raíz del repo.)

## 1. Ejercicio guiado — Dockerizar la mini-app

### Paso 1.1 — Verificá que la app corre **fuera** de Docker

```bash
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

En otra terminal:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Frenala con `Ctrl+C`.

### Paso 1.2 — Mirá el Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalamos uv una sola vez en una capa estable
RUN pip install --no-cache-dir uv

# Layer de deps (se reutiliza si pyproject.toml/uv.lock no cambian)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Layer de código (cambia siempre)
COPY app.py ./

# Usuario no-root
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Leelo de arriba abajo. Identificá:

- ¿Cuál es la capa que más se va a reutilizar?
- ¿Qué pasa si invertís `COPY pyproject.toml uv.lock ./` con `COPY app.py ./`? Pensá la respuesta antes de probarlo.

### Paso 1.3 — Construir y correr

```bash
docker build -t mini-saludo:0.1.0 .
```

Mirá la salida: cada `Step N/M` corresponde a una instrucción del Dockerfile. La primera vez todas las capas son nuevas; la segunda corrida (sin cambios) usa el cache para todas (`Using cache`).

```bash
docker run -d --name saludo -p 8000:8000 mini-saludo:0.1.0
docker ps                              # ¿está corriendo?
docker logs saludo                     # ¿cómo arrancó?
curl http://localhost:8000/
curl http://localhost:8000/health
docker exec -it saludo bash           # entrá al contenedor
ls /app                                # mirá la estructura adentro
exit
docker stop saludo
docker rm saludo
```

### Paso 1.4 — Aprovechá el cache

Editá `app.py` y cambiá el mensaje del endpoint `/`:

```python
return {"hello": "docker world"}
```

Volvé a buildear:

```bash
docker build -t mini-saludo:0.2.0 .
```

Mirá la salida: las capas hasta `COPY app.py ./` van a aparecer como `CACHED`. La capa de código y las posteriores se rebuildean. Build de ~2 segundos vs los ~30 de la primera vez. **Eso es el valor del orden correcto.**

Ahora editá `pyproject.toml` (sumá una dependencia que no necesitás, ej `httpx>=0.27`) y rebuildeá:

```bash
docker build -t mini-saludo:0.2.1 .
```

Mirá: cambia la capa de deps **y todas las posteriores se invalidan**. Build largo otra vez. Por eso el orden importa.

Volvé el `pyproject.toml` a como estaba.

### Paso 1.5 — Levantar con docker-compose

El `docker-compose.yml` del sandbox suma un Postgres como ejemplo (la mini-app no lo usa, pero practicamos la orquestación):

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      MODE: compose
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: demo
      POSTGRES_PASSWORD: demo
      POSTGRES_DB: demo
    volumes:
      - demo-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U demo"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  demo-data:
```

Levantá la stack:

```bash
docker compose up --build -d
docker compose ps                    # ambos servicios "running"; db debería decir "healthy"
docker compose logs -f api           # tail de logs (Ctrl+C para salir)
```

Probá la API:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Probá entrar al Postgres:

```bash
docker compose exec db psql -U demo -d demo -c "SELECT 1;"
```

Bajá la stack:

```bash
docker compose down                  # contenedores fuera, volumen demo-data CONSERVADO
docker volume ls | grep demo         # sigue el volumen
docker compose down -v               # ahora sí, borra TODO
```

### Paso 1.6 — Reflexión

Pensá:

- ¿Por qué `db:5432` desde el servicio `api` funciona sin saber la IP?
- Si `condition: service_healthy` no estuviera, ¿qué podría pasar la primera vez que `api` arranca?
- ¿Por qué los datos de Postgres sobreviven a `docker compose down` pero no a `docker compose down -v`?

## 2. Ejercicios libres

### 2.1. Multi-stage build

Modificá el Dockerfile a dos stages: uno `builder` que tenga `uv` y haga el `sync`, y uno `runtime` que solo copie el `.venv` y el código. Verificá:

```bash
docker images mini-saludo --format "{{.Tag}} {{.Size}}"
```

¿Cuánto bajó la imagen? (En este caso, la diferencia es chica porque la app no tiene deps con C extensions. Cuando metas Pillow o numpy, te ahorrás cientos de MB.)

Plantilla:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app.py ./
ENV PATH="/app/.venv/bin:${PATH}"
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.2. Healthcheck en el Dockerfile

Sumalo:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1
```

Reconstruí, corré, y mirá:

```bash
docker run -d --name saludo -p 8000:8000 mini-saludo:0.1.0
sleep 10
docker inspect --format='{{.State.Health.Status}}' saludo
# debería ser "healthy"
docker stop saludo && docker rm saludo
```

### 2.3. Bind mount para desarrollo

Modificá `docker-compose.yml` para mapear `./app.py` al contenedor y agregá `--reload` al `CMD` (vía `command:` en el yaml para no reconstruir):

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app.py:/app/app.py
    command: ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

Levantá la stack, editá `app.py` desde tu editor y mirá los logs del contenedor: uvicorn debería detectar el cambio y recargar. Hot-reload sin rebuild.

### 2.4. Pin completo de la imagen base

Cambiá `FROM python:3.12-slim` a un tag con SHA explícito (lo encontrás en [hub.docker.com/_/python](https://hub.docker.com/_/python)):

```dockerfile
FROM python:3.12.5-slim-bookworm@sha256:<sha>
```

Build determinístico para siempre. Si el upstream cambia el tag, el tuyo no se mueve.

### 2.5. `docker compose run --rm` para tareas one-off

Imaginá que tu app necesita un comando de inicialización (como `alembic upgrade head` en una migración). Probá ejecutar un comando aislado:

```bash
docker compose run --rm api python -c "print('hola desde un container efímero')"
```

`--rm` borra el contenedor después de salir. Útil para tasks de mantenimiento.

### 2.6. Inspeccionar layers

```bash
docker history mini-saludo:0.1.0
```

Ves cada capa con su tamaño. Si una capa es desproporcionadamente grande, sabés dónde optimizar.

## 3. Aporte al proyecto integrador (preparación M6 — sin cerrar todavía)

**No** vamos a tagear `proyecto-m6` hoy. Eso pasa al final de S21 cuando sumemos tests. Hoy preparamos la dockerización.

### 3.1. `Dockerfile` para TiendaPro Lite

Creá `code/proyecto-integrador/Dockerfile`:

```dockerfile
# Single-stage por ahora — la app no tiene deps con compilación pesada
FROM python:3.12-slim

# Setea env vars para Python correr como debería en contenedores
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN pip install --no-cache-dir uv

# Layer de deps
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Layer de código y datos
COPY src/ ./src/
COPY data/ ./data/
COPY main.py ./

# Usuario no-root
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Defaults razonables (override por env vars en runtime)
ENV TIENDAPRO_LOG_LEVEL=INFO

EXPOSE 8000

# Healthcheck contra /health
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uv", "run", "uvicorn", "tiendapro.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Tres comentarios:

- **`PYTHONUNBUFFERED=1`** y **`PYTHONDONTWRITEBYTECODE=1`**: estándar para Python en contenedores. Logs sin buffer (los ves al instante) y sin generar `.pyc` que ensucian el filesystem del contenedor.
- **`COPY data/`**: necesario porque el `lifespan` de la app en S18 lee `data/catalogo.json` para el seed.
- **No hay `.env`**: las env vars vienen del orquestador (docker compose en este caso).

### 3.2. `.dockerignore` para TiendaPro Lite

Creá `code/proyecto-integrador/.dockerignore`:

```dockerignore
# Git
.git/
.gitignore

# Python
__pycache__/
*.pyc
*.pyo
.venv/
.mypy_cache/
.ruff_cache/
.pytest_cache/
*.egg-info/

# Docker
Dockerfile
docker-compose.yml
.dockerignore

# Datos locales y secretos
*.db
*.sqlite
.env
.env.*

# Editor / OS
.vscode/
.idea/
.DS_Store

# Documentación / tests (si hubieran)
README.md
docs/
tests/
```

### 3.3. `docker-compose.yml` con Postgres

Creá `code/proyecto-integrador/docker-compose.yml`:

```yaml
services:
  api:
    build: .
    image: tiendapro:dev
    ports:
      - "8000:8000"
    environment:
      TIENDAPRO_DATABASE_URL: postgresql+psycopg://tienda:tienda@db:5432/tienda
      TIENDAPRO_LOG_LEVEL: INFO
      TIENDAPRO_DEBUG: "false"
      TIENDAPRO_API_KEY: cambia-esto-en-prod
      TIENDAPRO_ENABLE_ENRICHMENT: "true"
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: tienda
      POSTGRES_PASSWORD: tienda
      POSTGRES_DB: tienda
    ports:
      - "5432:5432"     # útil en dev para conectarte con DBeaver/psql desde el host
    volumes:
      - tienda-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tienda"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  tienda-data:
```

### 3.4. Sumar driver de Postgres

`pydantic-settings` lee la URL, pero SQLAlchemy necesita el driver instalado. Editá `code/proyecto-integrador/pyproject.toml` y sumá `psycopg`:

```toml
dependencies = [
    "pydantic>=2.6",
    "httpx>=0.27",
    "sqlalchemy>=2.0",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic-settings>=2.4",
    "psycopg[binary]>=3.2",
]
```

`psycopg[binary]` trae el driver precompilado (no requiere `libpq-dev` ni gcc en la imagen). Es lo correcto en producción para 99% de los casos.

```bash
cd code/proyecto-integrador
uv sync --all-groups
```

### 3.5. Actualizar `env.example`

Sumale al `code/proyecto-integrador/env.example` un comentario con la URL para Postgres:

```ini
TIENDAPRO_DEBUG=true
# Local SQLite (default):
TIENDAPRO_DATABASE_URL=sqlite:///tiendapro.db
# Para correr con docker compose (Postgres):
# TIENDAPRO_DATABASE_URL=postgresql+psycopg://tienda:tienda@db:5432/tienda
TIENDAPRO_API_KEY=cambia-esto-en-prod
TIENDAPRO_LOG_LEVEL=DEBUG
TIENDAPRO_ENABLE_ENRICHMENT=true
TIENDAPRO_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 3.6. Buildear y levantar

```bash
cd code/proyecto-integrador
docker compose up --build -d
docker compose ps
docker compose logs -f api
```

En otra terminal, probá:

```bash
curl -i http://localhost:8000/health
curl -s http://localhost:8000/productos | head -c 300

curl -X POST http://localhost:8000/productos \
    -H "Content-Type: application/json" \
    -d '{"nombre":"Producto Docker","categoria":"docker","precio":12.5,"stock":3}'

curl -s "http://localhost:8000/productos?categoria=docker"
```

Mirá los logs: cada request loguea con `request_id`, latencia, status. **Mismos logs que en S18, pero ahora dentro de Docker apuntando a Postgres.** Eso es lo que da Docker: el código no cambia.

Probá `psql` adentro del db:

```bash
docker compose exec db psql -U tienda -d tienda -c "SELECT id, nombre, precio FROM productos LIMIT 5;"
```

### 3.7. Bajá la stack (sin perder datos)

```bash
docker compose down                  # bajan los contenedores, volumen tienda-data CONSERVADO
docker compose up -d                 # los datos siguen
```

Si querés empezar limpio:

```bash
docker compose down -v               # borra el volumen también
```

### 3.8. Verificar que también corre **sin** Docker (modo local)

Esto es importante: la dockerización **no rompió** el modo local. Probá:

```bash
docker compose down
unset TIENDAPRO_DATABASE_URL              # por las dudas
uv run uvicorn tiendapro.api:app --reload --port 8000
```

Debe seguir levantando contra SQLite local. Lo bueno de hacer toda la config por env vars: la misma app corre en tres modos (local SQLite, compose con Postgres, prod) sin tocar código.

### 3.9. Verificar calidad

```bash
uv run mypy src/ main.py
uv run ruff check .
uv run ruff format --check .
```

Los tres deberían seguir limpios. Hoy no tocaste código de la app.

### 3.10. Commit (sin tag — tag viene en S21)

```bash
git add code/proyecto-integrador/Dockerfile \
        code/proyecto-integrador/.dockerignore \
        code/proyecto-integrador/docker-compose.yml \
        code/proyecto-integrador/pyproject.toml \
        code/proyecto-integrador/uv.lock \
        code/proyecto-integrador/env.example
git commit -m "feat(proyecto-integrador): dockerizar app con Dockerfile + compose (Postgres)"
```

**No** taguees `proyecto-m6`. El cierre del módulo viene en S21.

---

Cuando termines, volvé al [README](README.md) y respondé las preguntas de auto-evaluación. Si todas se contestan sin dudar, pasá a [S21 — Testing con pytest](../sesion-21-pytest/README.md) — la última sesión del curso.
