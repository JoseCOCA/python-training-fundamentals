# S20 — Recursos

## Documentación oficial

- **Docker Get Started** ([docs.docker.com/get-started/](https://docs.docker.com/get-started/)). Tutorial oficial. Cubre los conceptos básicos (image, container, registry) en orden.
- **Dockerfile reference** ([docs.docker.com/engine/reference/builder/](https://docs.docker.com/engine/reference/builder/)). La referencia de cada instrucción. La consultás cada vez que dudes sobre `CMD` vs `ENTRYPOINT`, `ADD` vs `COPY`, etc.
- **Compose Specification** ([compose-spec.io](https://compose-spec.io/)). El spec del `docker-compose.yml`. Más actualizado que la doc histórica de Compose v2.
- **Best practices for writing Dockerfiles** ([docs.docker.com/develop/develop-images/dockerfile_best-practices/](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)). Lectura corta y obligatoria. Cubre cache, multi-stage, entry points y más.
- **Docker security best practices** ([docs.docker.com/engine/security/](https://docs.docker.com/engine/security/)). Para cuando tu imagen vaya a producción seria.

## Lecturas guiadas

- **Production-ready Dockerfiles for Python apps** (varios autores en [pythonspeed.com](https://pythonspeed.com/articles/)). Itamar Turner-Trauring tiene una serie de blog posts cortos y prácticos. Empezá por "The best Docker base image for your Python application".
- **Docker for Beginners** ([docker-curriculum.com](https://docker-curriculum.com/)). Tutorial gratuito muy completo.
- **The Twelve-Factor App** ([12factor.net](https://12factor.net/)). Releelo: factor V (Build/Release/Run), VI (Processes), VIII (Concurrency), XI (Logs). Docker lo encarna casi línea por línea.
- **Multi-stage builds** ([docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/)). Profundizá cuando llegues a apps con build deps reales (numpy, Pillow, lxml).
- **Why Alpine is bad for Python** ([pythonspeed.com/articles/alpine-docker-python/](https://pythonspeed.com/articles/alpine-docker-python/)). Argumento contundente para evitar `python:alpine`.

## Para profundizar

- **Docker Deep Dive** (Nigel Poulton). El libro de referencia. Cubre internals (cgroups, namespaces, layers). Para ingenieros que quieren entender por dentro.
- **Container Security** (Liz Rice). Cómo se aísla un contenedor, qué garantías ofrece, qué escapes existen. Lectura obligatoria si vas a deployar en multi-tenant.
- **Efficient Linux at the Command Line** (Daniel Barrett). Indirecto pero útil: para hacer Dockerfiles realmente buenos, conviene saber lo que hacen los comandos shell que metés adentro.
- **Distroless images** ([github.com/GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless)). Imágenes Google que llevan al extremo "menos es mejor": ni shell, ni gestor de paquetes. Más seguras pero más difícil de debuggear.
- **Kubernetes Up & Running** (Kelsey Hightower et al.). Cuando Docker solo no alcanza, k8s es el siguiente escalón.

## Herramientas que vale la pena conocer

- **`docker scout`** ([docs.docker.com/scout/](https://docs.docker.com/scout/)). Análisis de vulnerabilidades en tus imágenes. Integrado en Docker Desktop.
- **`hadolint`** ([github.com/hadolint/hadolint](https://github.com/hadolint/hadolint)). Linter para Dockerfiles. Te marca antipatrones (apt-get sin `--no-install-recommends`, capas innecesarias, etc.).
- **`dive`** ([github.com/wagoodman/dive](https://github.com/wagoodman/dive)). TUI para explorar las layers de una imagen. Útil para entender qué pesa.
- **`docker-slim`** ([github.com/slimtoolkit/slim](https://github.com/slimtoolkit/slim)). Toma tu imagen y la reduce drásticamente eliminando lo que no se ejecuta. Magia controvertida — usalo con cuidado.
- **`buildx`** y **BuildKit** — el motor de build moderno de Docker. Soporta builds multi-arch (`--platform=linux/amd64,linux/arm64`), cache distribuido y más. Activado por default en versiones recientes.
- **`podman`** ([podman.io](https://podman.io/)). Drop-in replacement de Docker que corre sin daemon (más seguro, no requiere root). Compatible con Dockerfiles.
- **Trivy / Grype** — escáneres de vulnerabilidades open source. Útil en pipelines de CI: corré contra la imagen antes de pushear al registry.
- **Lazydocker** — TUI para gestionar contenedores corriendo (logs, stats, exec). Si te gustó `lazygit`, te va a gustar.

## Referencias para resolver dudas puntuales

- **"`docker compose up` falla con 'permission denied' en el socket"** (Linux). Tu user no está en el grupo `docker`. `sudo usermod -aG docker $USER && newgrp docker` (o re-loguearte).
- **"Mi imagen pesa 1.2GB y la base era 150MB"**. Probablemente: layer de `apt-get install` sin `--no-install-recommends && rm -rf /var/lib/apt/lists/*`, o cache de `pip` no limpiado, o `.git/` colado por falta de `.dockerignore`. Inspeccionalo con `docker history` o `dive`.
- **"`COPY` no encuentra mi archivo"**. El `COPY` parte del **build context**, no del Dockerfile. Si tu archivo está en `../foo.txt` y vos hacés `docker build .` desde el directorio actual, no lo va a encontrar. Mové el archivo o cambiá el context.
- **"En el contenedor mi app no se conecta a la DB"**. ¿Estás usando `localhost` en la URL? Localhost dentro del contenedor es **el contenedor mismo**, no el host. Si la DB es otro contenedor en compose, el hostname es el nombre del servicio (`db`). Si la DB está en el host, usá `host.docker.internal` (Mac/Windows) o el bridge `172.17.0.1` (Linux).
- **"Mi healthcheck siempre falla"**. Generalmente: `curl` no está instalado en `python:slim`. Usá `python -c "import urllib.request; urllib.request.urlopen(url)"` que sí viene de fábrica.
- **"`docker compose down` me borró la DB"**. ¿Usaste `-v`? Esa flag borra volúmenes. Sin ella, los datos persisten.
- **"Cambios en mi código no se reflejan en el contenedor"**. Sin bind mount, el código va dentro de la imagen al hacer `build`. Necesitás rebuild (`docker compose up --build`) o bind mount (`volumes: - ./src:/app/src`).
- **"`uvicorn --reload` no detecta cambios dentro del contenedor"**. Probá agregar `--reload-dir /app/src` explícito. En algunos filesystems (especialmente Mac → bind mount → contenedor) los inotify events no llegan.
- **"Quiero correr un comando una sola vez (migrate, seed)"**. `docker compose run --rm api python -m mi_modulo.script`. El `--rm` borra el contenedor al terminar.
- **"Mi imagen funciona localmente pero no en otra arquitectura"**. Si construís en Mac M1/M2 (arm64) y deployás a un server x86 (amd64), tu imagen no corre. Solución: `docker buildx build --platform linux/amd64 -t ... .` o construí en CI sobre la arq destino.

## Errores comunes

- **`COPY . .` arriba de todo el Dockerfile**. Cualquier cambio de código invalida la cache de deps. Siempre: deps primero, código después.
- **Sin `.dockerignore`**. Build context con `.git/` (a veces gigas), `.venv/`, `__pycache__/`. Y peor: `.env` con secretos puede terminar dentro de la imagen.
- **`apt-get install` en una capa, sin limpiar el cache**:
  ```dockerfile
  # MAL — deja /var/cache/apt/ con megas innecesarios
  RUN apt-get update
  RUN apt-get install -y libpq-dev
  ```
  ```dockerfile
  # BIEN — todo en una capa, cache limpiada
  RUN apt-get update && \
      apt-get install -y --no-install-recommends libpq-dev && \
      rm -rf /var/lib/apt/lists/*
  ```
- **Hardcodear secrets en el Dockerfile**. `ENV API_KEY=xxx` queda **en la imagen** y la imagen va a un registry. Cualquiera con acceso al registry tiene la key. Pasala por env vars en runtime.
- **`FROM python:latest`** o sin tag. Build no reproducible — mañana puede ser otra versión. Pin: `python:3.12-slim` o más estricto.
- **Logs a archivo dentro del contenedor**. Se pierden al borrar el contenedor. Stdout/stderr es la convención.
- **No usar healthcheck**. Tu orquestador no sabe si tu app realmente sirve, solo si el proceso vive. Resultado: tráfico ruteado a una app rota.
- **Múltiples procesos en un contenedor (app + cron + nginx)**. Cada uno necesita su propio ciclo de vida. Si uno cae, el contenedor sigue vivo y el orquestador no reacciona.
- **Bind mount de todo el repo en producción**. Útil en dev; en prod es un anti-patrón (filesystem del host, permisos raros, no se replica al escalar).
- **Volumen y bind mount confundidos**. Volumen → gestionado por Docker, persistente, bueno para datos. Bind mount → mapeo directo del host, bueno para dev. No los mezcles sin pensar.
- **`docker run` sin `--rm` para tasks one-off**. Te llenás de contenedores parados. Salvo que lo necesites después, usá `--rm`.

## Si vas hacia el curso 2

En AI Engineering, Docker se vuelve **obligatorio**:

- **Modelos locales (Ollama, vLLM)** corren en contenedores con GPU passthrough.
- **Vector DBs (Qdrant, Weaviate, ChromaDB)** se levantan con compose en una línea.
- **Múltiples versiones de un agente** corren en paralelo en contenedores aislados — comparás resultados sin que se contaminen.
- **Reproducibilidad de experimentos**: tu compañera levanta `docker compose up` y obtiene exactamente la misma stack que vos. Cero "en mi máquina funciona".
- **Despliegue a Cloud Run / ECS / Modal**: todos consumen imágenes Docker. La disciplina de hoy se traduce directo a producción.

Cuando empieces a usar GPUs (entrenar pequeños modelos, embeddings con CUDA), la cosa se complica: imágenes base con CUDA (`nvidia/cuda`), `--gpus all` en docker run, sutilezas de drivers. Pero los fundamentos — Dockerfile, compose, healthchecks, env vars — siguen siendo los mismos.

La base que ponés hoy es transferible al 100%.
