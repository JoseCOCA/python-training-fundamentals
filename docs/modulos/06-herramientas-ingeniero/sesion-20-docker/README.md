# S20 — Docker y docker-compose: empaquetar la app

> **Sesión 2h.** ~50 min lectura + ~70 min ejercicios. **Segunda sesión del Módulo 6.** En S19 te peleaste con git. Hoy entra el segundo pilar de la cocina: **Docker**. Es la herramienta que separa "esto corre en mi máquina" de "esto corre en cualquier máquina con Docker, igual a como corre acá". Vamos a entender qué problema resuelve, cómo construir una imagen, cómo orquestar varios servicios con `docker-compose`, y a aplicarlo a TiendaPro Lite.

---

## 1. Objetivos de aprendizaje

Al terminar esta sesión vas a poder:

- Explicar qué problema resuelve Docker (entornos reproducibles, aislamiento) y qué problema **no** resuelve (no es una VM ni un sustituto de tests).
- Distinguir **imagen** (artefacto inmutable) de **contenedor** (instancia ejecutándose).
- Escribir un `Dockerfile` para una app Python (FastAPI/uv) entendiendo cada instrucción y por qué su orden importa.
- Aprovechar el **cache de capas** ordenando instrucciones de menos a más volátiles (deps antes que código).
- Usar `.dockerignore` para mantener el build context chico y evitar leakear secretos.
- Construir y correr una imagen: `docker build`, `docker run`, `docker logs`, `docker exec`, `docker ps`.
- Definir un `docker-compose.yml` para correr la app + base de datos juntas con un solo comando.
- Persistir datos con **volúmenes** y entender la diferencia con **bind mounts**.
- Pasar configuración por **variables de entorno** (no hardcodearla en la imagen).
- Aplicar buenas prácticas: imagen base slim, usuario no-root, multi-stage builds, healthchecks.
- Dockerizar TiendaPro Lite con compose (app + Postgres), aprovechando que `pydantic-settings` ya lee de env vars.

## 2. Prerequisitos

- Tener Docker Desktop / Docker Engine instalado y corriendo. Verificalo con `docker run hello-world`.
- [S18 — pydantic-settings + logging](../../05-api-fastapi/sesion-18-config-logging/README.md): la app del integrador ya lee toda su config de variables de entorno, lo cual es **prerequisito** para dockerizarla.
- Conceptos básicos de redes (puerto, host, mapping). No hace falta más que entender que cuando exponés un puerto, podés acceder al servicio desde otra máquina.

## 3. Conceptos clave

1. **Imagen.** Snapshot inmutable de un sistema de archivos + metadata (qué comando correr, qué puertos expone). Identificada por un hash; etiquetable (`tiendapro:0.6.0`).
2. **Contenedor.** Una **instancia en ejecución** de una imagen. Aislado del host por kernel namespaces (procesos, red, filesystem). Borrar el contenedor no borra la imagen.
3. **Dockerfile.** Receta declarativa para construir una imagen. Cada instrucción crea una **capa** (layer) cacheada.
4. **Build context.** El conjunto de archivos que `docker build` empaqueta y manda al daemon. Si no usás `.dockerignore`, vas a mandar `__pycache__/`, `.venv/`, y otros megabytes inútiles (a veces, secretos).
5. **Layers y cache.** Docker reutiliza capas si la instrucción y sus inputs no cambiaron. El orden del Dockerfile determina cuántos rebuilds vas a tener.
6. **Volumen.** Almacenamiento persistente, gestionado por Docker, fuera del filesystem del contenedor. Sobrevive a `docker rm`.
7. **Bind mount.** Mapeo directo de un directorio del host al contenedor. Útil en desarrollo (cambios al código se ven al instante).
8. **Variables de entorno.** Mecanismo principal para configurar contenedores. `-e KEY=val` o `env_file:` en compose.
9. **Network.** Docker crea redes virtuales entre contenedores. En compose, dos servicios en el mismo `compose.yml` se ven entre sí por nombre (`db`, `app`) sin hardcodear IPs.
10. **`docker-compose`.** Herramienta para definir y correr aplicaciones multi-contenedor con un YAML. La forma estándar de levantar "la stack" (app + db + cache) en dev.

## 4. Teoría

### 4.1. ¿Qué problema resuelve Docker?

Antes de Docker, el problema clásico era:

> "En mi máquina funciona."

Tres causas típicas:

- Versión distinta del runtime (Python 3.10 local, 3.12 en server).
- Dependencias del sistema (libpq, openssl) instaladas a mano y olvidadas.
- Variables de entorno o paths que cada uno tiene distintos.

Docker resuelve esto **empaquetando todo**: runtime, deps del SO, deps de Python, código de tu app, configuración por defecto. Si la imagen corre en tu laptop, va a correr **igual** en CI, en staging y en prod.

Lo que Docker NO resuelve:

- **No te da tests.** Una imagen mal construida también puede tener bugs.
- **No es una VM.** No virtualiza hardware; usa el kernel del host con namespaces. Más liviano que una VM pero menos aislado (un escape de container puede tocar el host).
- **No es magia para producción.** Hace falta orquestación (Kubernetes, ECS, Docker Swarm) para alta disponibilidad real. Docker solo no es producción seria.

### 4.2. Imagen vs contenedor

```
┌────────────────┐       docker run        ┌──────────────────┐
│   IMAGEN       │ ─────────────────────►  │   CONTENEDOR     │
│  (artefacto    │                         │   (instancia en  │
│   inmutable)   │                         │    ejecución)    │
│                │       docker rm         │                  │
│  tiendapro:    │ ◄─────────────────────  │                  │
│   0.6.0        │       docker stop       │                  │
└────────────────┘                         └──────────────────┘
```

Una imagen puede tener N contenedores corriendo a la vez (cada uno aislado). Borrar todos los contenedores no toca la imagen. Borrar la imagen sí pierde el artefacto (`docker rmi`).

Comandos básicos:

```bash
docker images                       # lista imágenes locales
docker ps                           # lista contenedores corriendo
docker ps -a                        # incluye los detenidos
docker run -d --name api tiendapro:0.6.0   # corre la imagen, modo daemon, le pone nombre
docker logs api                     # ve los logs
docker exec -it api bash            # entra al contenedor a un shell
docker stop api                     # frena
docker rm api                       # borra el contenedor
docker rmi tiendapro:0.6.0          # borra la imagen
```

### 4.3. Tu primer Dockerfile

Imaginá una app Python mínima:

```python
# app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root() -> dict[str, str]:
    return {"hello": "docker"}
```

Un Dockerfile básico:

```dockerfile
# 1. Base
FROM python:3.12-slim

# 2. Working directory dentro del contenedor
WORKDIR /app

# 3. Instalar deps primero (layer cacheada)
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

# 4. Copiar el código (layer que cambia más seguido)
COPY app.py ./

# 5. Documentar el puerto
EXPOSE 8000

# 6. Comando default
CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Por qué cada instrucción**:

- **`FROM python:3.12-slim`**: imagen base oficial. `slim` es la versión mínima de Debian con Python — ~150MB en lugar de los ~1GB de `python:3.12`. **No uses `alpine`** para Python en producción — la libc distinta (musl) rompe wheels precompilados (numpy, pandas) y termina compilando desde fuente, lento e inseguro.
- **`WORKDIR /app`**: cualquier comando posterior corre desde `/app`. Crea el directorio si no existe.
- **`COPY pyproject.toml uv.lock ./`**: copia **solo** los archivos de deps. Si `pyproject.toml` no cambia, esta capa se reusa del cache.
- **`RUN pip install ... && uv sync --frozen --no-dev`**: instala uv, después sincroniza las deps según el lockfile, sin las de dev. El `&&` mete todo en una sola capa (menos overhead).
- **`COPY app.py ./`**: ahora sí copiás el código. Si **solo** cambia el código, las capas anteriores (deps) se reusan y el rebuild es instantáneo.
- **`EXPOSE 8000`**: documentación, no abre el puerto. Sirve para `docker inspect` y compose.
- **`CMD [...]`**: el comando que corre cuando el contenedor arranca. La forma "exec" (lista de strings) es preferible a la "shell" porque hace que las señales (SIGTERM) lleguen directo al proceso.

Para construir y correr:

```bash
docker build -t mi-app:0.1.0 .
docker run -p 8000:8000 mi-app:0.1.0
```

`-p 8000:8000`: mapea el puerto del **host** (el primero) al **contenedor** (el segundo).

### 4.4. El cache de capas y por qué el orden importa

Docker hashea cada instrucción + sus inputs. Si nada cambió, reutiliza la capa. Si algo cambia, esa capa **y todas las siguientes** se invalidan.

Mal orden:

```dockerfile
COPY . .
RUN uv sync --frozen --no-dev    # invalidás esta capa cada vez que cambiás un archivo
```

Cualquier cambio mínimo en el código invalida la instalación de deps. Build de 30 segundos cada vez.

Buen orden (el que usamos arriba):

```dockerfile
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev    # esta capa solo se invalida si cambian las deps
COPY . .                          # esta es la única que se invalida en cambios de código
```

Build de 2 segundos cuando solo cambia código.

**Regla**: ordená de menos a más volátil. Lo que cambia poco arriba; lo que cambia siempre, abajo.

### 4.5. `.dockerignore`: el `.gitignore` del build context

Cuando hacés `docker build .`, Docker manda **todo el directorio actual** al daemon. Si tenés un `.venv/` de 800MB, lo manda. Si tenés un `.env` con secretos, lo manda (y termina dentro de la imagen si hacés `COPY . .`).

Solución: `.dockerignore` en la raíz, lista de patrones a excluir.

```dockerignore
.git/
.venv/
__pycache__/
*.pyc
.mypy_cache/
.ruff_cache/
.pytest_cache/

.env
.env.local
*.db
*.sqlite

.idea/
.vscode/

Dockerfile
docker-compose.yml
README.md
docs/
tests/
```

**Crítico**: agregalo el día 0. Sin `.dockerignore`, builds gigantes y filtraciones de secretos son la norma.

### 4.6. Multi-stage builds: imagen final más chica

Para apps Python complejas (con deps que requieren compilación), conviene **separar el build de la runtime**.

```dockerfile
# Stage 1: builder
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: runtime
FROM python:3.12-slim

WORKDIR /app

# Copiamos SOLO el venv del builder, no las herramientas de build
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY main.py ./

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000
CMD ["uvicorn", "tiendapro.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Ventajas:

- La imagen final no tiene `uv`, `pip`, ni los caches del build.
- Más chica → más rápida de descargar y arrancar.
- Menos superficie de ataque (menos binarios = menos CVEs).

Para apps tan simples como TiendaPro Lite hoy, single-stage está bien. Cuando metas deps con C extensions (psycopg2 con build, no binary; numpy en proyectos científicos), multi-stage paga.

### 4.7. Variables de entorno: la forma de configurar

Tres formas, en orden de preferencia para producción:

```bash
# 1. -e en docker run (puntual)
docker run -e TIENDAPRO_DEBUG=true -e TIENDAPRO_DATABASE_URL=... mi-app

# 2. --env-file en docker run (lee un archivo .env)
docker run --env-file .env mi-app

# 3. environment / env_file en docker-compose (declarativo, versionable)
```

**`pydantic-settings` ya lee de env vars**, así que no hace falta cambiar código: solo seteás las vars desde fuera.

**Importante**: `ENV` en el Dockerfile **se queda en la imagen**. Sirve para defaults razonables, no para secretos.

```dockerfile
ENV TIENDAPRO_LOG_LEVEL=INFO       # default razonable, queda en la imagen
# NO hagas: ENV TIENDAPRO_API_KEY=xxx
```

### 4.8. `docker-compose`: orquestar servicios

`docker run` con muchas flags es tedioso y no versionable. Para correr la app + base de datos juntas, `compose` es el estándar.

`docker-compose.yml`:

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      TIENDAPRO_DATABASE_URL: postgresql+psycopg://tienda:tienda@db:5432/tienda
      TIENDAPRO_LOG_LEVEL: INFO
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: tienda
      POSTGRES_PASSWORD: tienda
      POSTGRES_DB: tienda
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

Levantarlo:

```bash
docker compose up                  # foreground
docker compose up -d               # detached
docker compose logs -f api         # logs en vivo del servicio api
docker compose ps                  # qué está corriendo
docker compose down                # frena y borra contenedores (NO el volumen)
docker compose down -v             # frena, borra contenedores Y el volumen (¡pierde datos!)
```

**Cosas a mirar del YAML**:

- **`build: .`**: construye la imagen del directorio actual.
- **`depends_on` con `condition: service_healthy`**: la api espera al healthcheck del db antes de arrancar. Sin esto, el api puede arrancar mientras Postgres todavía no aceptó conexiones.
- **`db:5432`** en la URL: dentro de la red de compose, `db` es el hostname del servicio `db`. No hace falta IP.
- **`volumes: tienda-data:/var/lib/postgresql/data`**: el directorio de datos de Postgres se persiste en un volumen Docker. `docker compose down` lo conserva; solo `down -v` lo borra.

### 4.9. Volúmenes vs bind mounts

**Volumen** (gestionado por Docker, mejor para producción):

```yaml
volumes:
  - tienda-data:/var/lib/postgresql/data
```

Vive en `/var/lib/docker/volumes/`. Docker se encarga de permisos, backups, drivers. Persiste entre `up`s y `down`s.

**Bind mount** (mapea un dir del host, mejor para desarrollo):

```yaml
volumes:
  - ./src:/app/src                # cambios de código se reflejan al toque
```

Útil con `uvicorn --reload`: editás un archivo en tu editor, el código del contenedor cambia, uvicorn lo recarga. **No** uses bind mounts para datos de producción — son frágiles, dependen del host.

### 4.10. Buenas prácticas

#### Usuario no-root

Por defecto, los contenedores corren como root. Si una app comprometida ejecuta código arbitrario, lo hace como root **dentro** del contenedor. No es lo mismo que ser root del host (los namespaces aíslan), pero igual evitalo.

```dockerfile
RUN useradd --create-home --shell /bin/bash app
USER app
WORKDIR /home/app
```

#### Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD curl -f http://localhost:8000/health || exit 1
```

Le permite a Docker (y a compose, y a Kubernetes) saber si tu app está sana — no solo "el proceso vive" sino "responde correctamente".

#### Tag explícito de la imagen base

```dockerfile
FROM python:3.12-slim         # ✓ pin de la minor
# evitá:
FROM python:latest            # ✗ rompe builds reproducibles
```

Mejor todavía: pin completo (`python:3.12.5-slim-bookworm`) para builds 100% reproducibles. Te obligás a actualizar conscientemente, no por accidente.

#### Una preocupación por contenedor

Anti-patrón: meter app + db + cache + nginx **todo** en un contenedor. Cada uno tiene un ciclo de vida distinto, debe escalar independiente. Un contenedor = un proceso (idealmente).

#### Logs por stdout / stderr

Docker recolecta lo que tu app escribe a stdout/stderr. **No** loguees a archivos dentro del contenedor — los perdés cuando se borra. La librería `logging` de S18 ya escribe a stdout: vas bien.

### 4.11. Workflow típico de desarrollo con compose

```bash
# Día normal:
docker compose up -d              # levanta la stack
docker compose logs -f api        # tail de logs
# ... editás código ...
# Si tenés bind mount + uvicorn --reload, el cambio se aplica solo
# Si no, rebuild:
docker compose up -d --build api

# Para entrar a un contenedor y depurar:
docker compose exec api bash

# Para correr un comando one-off (ej: migrate de DB):
docker compose run --rm api python -m tiendapro.scripts.migrate

# Cuando termines:
docker compose down               # baja la stack, conserva el volumen
```

Memorizá `up`, `down`, `logs`, `exec`, `run --rm`. El resto lo googleás cuando lo necesites.

### 4.12. Cuándo Docker NO es la respuesta

- **Tu app es un script CLI que corre 10 segundos.** Docker es overhead innecesario. Un `uv tool install` o un `pipx install` alcanza.
- **Tenés un equipo de un par de personas en una sola máquina.** Si todos usan el mismo SO y Python, un `uv sync` es más simple que un Dockerfile.
- **Necesitás performance bare-metal extrema.** El overhead de namespaces es mínimo pero existe; en cargas muy específicas se nota.
- **Estás en producción seria.** Docker solo no alcanza — necesitás un orquestador (Kubernetes, ECS) o un PaaS encima (Fly.io, Railway, Render).

Docker es la herramienta correcta cuando: necesitás reproducibilidad entre máquinas, querés simular tu stack completa localmente (con DB, cache, etc.), o vas a deployar a un orquestador.

## 5. Patrones y antipatrones

| ✅ Patrón | ❌ Antipatrón |
|---|---|
| `FROM python:3.12-slim` con tag explícito | `FROM python:latest` o `FROM python` (no reproducible) |
| Capas ordenadas: deps antes que código | `COPY . .` arriba, `pip install` después (cache se rompe siempre) |
| `.dockerignore` desde el día 0 | Build context con `.venv/` y `.git/` adentro |
| ENV vars para config (la app las lee al startup) | Hardcodear URLs/keys en el Dockerfile |
| `pip install --no-cache-dir`, `uv sync --frozen` | `pip install` que deja cache de wheels en la imagen |
| Multi-stage cuando hay deps de build | Imagen final con compiladores y headers (~1GB innecesario) |
| Logs por stdout/stderr | Logs a archivo en `/var/log/app.log` (se pierden al borrar el contenedor) |
| `USER app` (no-root) | Todo corriendo como root |
| `HEALTHCHECK` configurado | Sin healthcheck → orquestador no sabe si tu app realmente sirve |
| Volúmenes para datos persistentes | Datos en el filesystem del contenedor (se pierden) |
| `compose.yml` con `depends_on: condition: service_healthy` | `depends_on` simple → race condition al startup |
| Imagen base `slim` (Debian) | `alpine` para apps Python serias (musl rompe wheels) |
| Un proceso = un contenedor | App + DB + nginx en un solo contenedor |
| `docker compose down` (preserva volumen) | `down -v` por inercia → perdiste la DB de dev |

## 6. Conexión con el proyecto integrador

En esta sesión **no agregás código de aplicación** al integrador, pero dejás listo el Dockerfile y el compose. El cierre real (`proyecto-m6` tag) llega en S21 cuando sumemos tests.

Lo que dejás en marcha hoy:

1. **`code/proyecto-integrador/Dockerfile`** que construye una imagen de TiendaPro Lite.
2. **`code/proyecto-integrador/.dockerignore`** que mantiene el build context chico.
3. **`code/proyecto-integrador/docker-compose.yml`** que levanta la app + Postgres juntos con un comando.
4. **`env.example` actualizado** con la URL de Postgres para el modo compose.

Vas a poder correr:

```bash
cd code/proyecto-integrador
docker compose up --build
# y en otra terminal:
curl http://localhost:8000/health
```

Y la API levanta apuntando a Postgres real, no a SQLite local. Sin tocar una línea de código de la app — porque desde S18 toda la config viene de env vars.

Detalles paso a paso en `ejercicios.md`.

## 7. Resumen

1. **Imagen = artefacto inmutable; contenedor = instancia en ejecución.** No los confundas.
2. **Dockerfile**: receta declarativa, cada instrucción es una capa cacheable.
3. **Orden importa**: deps arriba (cambian poco), código abajo (cambia siempre). Cache de capas te ahorra minutos.
4. **`.dockerignore` desde el día 0**, o vas a leakear secretos y mandar megabytes inútiles.
5. **`python:3.12-slim`** como base — `alpine` rompe wheels Python; `python:latest` rompe reproducibilidad.
6. **Multi-stage** cuando hay deps de build (psycopg2 from source, numpy desde fuente). Imagen final más chica y segura.
7. **Config por env vars**, no hardcodeada. `pydantic-settings` ya está listo para esto.
8. **`docker-compose`** orquesta varios servicios con un YAML versionable. `up`, `down`, `logs`, `exec`.
9. **Volúmenes** para datos persistentes; **bind mounts** para desarrollo (hot-reload).
10. **Buenas prácticas**: usuario no-root, healthcheck, logs a stdout, una preocupación por contenedor.

## 8. Preguntas de auto-evaluación

1. ¿Cuál es la diferencia entre una imagen y un contenedor? ¿Qué relación tienen con `docker run` y `docker rm`?
2. ¿Por qué este orden importa en un Dockerfile?
   ```dockerfile
   COPY pyproject.toml uv.lock ./
   RUN uv sync
   COPY . .
   ```
   ¿Qué pasa si lo invertís?
3. ¿Para qué sirve `.dockerignore`? ¿Qué riesgos hay si no lo tenés?
4. ¿Por qué no usar `FROM python:alpine` para una app Python con `numpy` o `pydantic` (que tiene C extensions)?
5. ¿Qué hace un multi-stage build? Da un ejemplo concreto donde tenga sentido y otro donde no.
6. ¿Cómo le pasás la `DATABASE_URL` al contenedor? Listá tres formas, en orden de preferencia para producción.
7. ¿Qué hace `EXPOSE 8000`? ¿Y `-p 8000:8000`? ¿Es lo mismo?
8. Diferencia entre **volumen** y **bind mount**. ¿Cuál usás para los datos de Postgres en producción y cuál para tu código en desarrollo?
9. En un `docker-compose.yml`, ¿por qué `depends_on: condition: service_healthy` es preferible a `depends_on:` solo?
10. Tu app loguea a `/var/log/app.log` adentro del contenedor. Después de un `docker compose down`, los logs no están. ¿Por qué? ¿Cómo lo arreglás?

Cuando puedas responder todas, pasá a [`ejercicios.md`](ejercicios.md) para construir el Dockerfile del integrador.
