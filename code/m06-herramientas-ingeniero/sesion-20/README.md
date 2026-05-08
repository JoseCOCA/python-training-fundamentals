# Sandbox de S20 — Docker

Mini-app FastAPI dockerizada. Sirve para practicar `docker build`, `docker run`, `docker compose up`, cache de capas y multi-stage builds.

## Qué hay

- `app.py` — FastAPI con dos endpoints (`/` y `/health`).
- `Dockerfile` — receta single-stage con orden correcto (deps antes que código), usuario no-root y healthcheck.
- `.dockerignore` — patrones para mantener el build context limpio.
- `docker-compose.yml` — levanta la app + un Postgres de juguete.
- `pyproject.toml` — solo `fastapi` y `uvicorn` como deps.

## Correr local (sin Docker)

```bash
uv sync
uv run uvicorn app:app --host 0.0.0.0 --port 8000
```

Verificá:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

## Correr con Docker

```bash
docker build -t mini-saludo:0.1.0 .
docker run -d --name saludo -p 8000:8000 mini-saludo:0.1.0
docker logs saludo
curl http://localhost:8000/
docker stop saludo && docker rm saludo
```

## Correr con docker-compose (app + Postgres)

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f api      # Ctrl+C para salir del tail
curl http://localhost:8000/
docker compose exec db psql -U demo -d demo -c "SELECT 1;"
docker compose down             # conserva el volumen demo-data
docker compose down -v          # borra el volumen también
```

## Ver el cache de capas en acción

1. `docker build -t mini-saludo:0.1.0 .` — primera vez, todas las capas son nuevas.
2. Editá `app.py` (cambiá un mensaje).
3. `docker build -t mini-saludo:0.2.0 .` — fijate cuáles capas dicen `CACHED` y cuáles se rebuildean.
4. Ahora editá `pyproject.toml` (sumá una dep que no necesitás).
5. `docker build -t mini-saludo:0.2.1 .` — ahora la capa de deps cambia y todas las posteriores se invalidan.

Pasos detallados en [`ejercicios.md`](../../../docs/modulos/06-herramientas-ingeniero/sesion-20-docker/ejercicios.md).
