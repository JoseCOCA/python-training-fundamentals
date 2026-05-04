# 01 — Setup del entorno (referencia rápida)

> **Si nunca has hecho este setup**, no uses esta página — usa [`modulos/00-setup-mentalidad/sesion-00.2-setup-entorno/`](modulos/00-setup-mentalidad/sesion-00.2-setup-entorno/) que es la sesión completa con explicaciones.
>
> Esta página es la **referencia condensada** — los comandos sin explicación, útil cuando reinstalas en otra computadora o cuando tienes que recordar la secuencia exacta.

---

## Requerimientos

- Linux, macOS, o Windows con WSL2.
- Permisos de administrador.
- Conexión a internet para las descargas.

## Pasos

### 1. Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cierra la terminal y abre una nueva. Verifica:

```bash
uv --version
```

### 2. Instalar Python 3.12

```bash
uv python install 3.12
uv python list
```

### 3. Clonar el repo del curso

```bash
git clone https://github.com/JoseCOCA/python-training-fundamentals.git
cd python-training-fundamentals
```

### 4. Sincronizar dependencias del curso

```bash
uv sync
```

Esto crea un virtual environment local (`.venv/`) e instala las dependencias de tooling (ruff, mypy, pytest).

### 5. Verificar el tooling

```bash
uv run python --version    # → Python 3.12.x
uv run ruff --version
uv run mypy --version
uv run pytest --version
```

Los cuatro comandos deben responder sin error.

### 6. Configurar el archivo de entorno

```bash
cp env.example .env
```

Edita `.env` solo cuando un módulo lo requiera (M4 en adelante). Para M0-M3 no necesitas tocarlo.

### 7. Instalar VS Code y extensiones

1. Descarga e instala VS Code desde https://code.visualstudio.com/.
2. Abre el repo con:
   ```bash
   code .
   ```
3. Instala las extensiones obligatorias:
   - **Python** (Microsoft).
   - **Pylance** (Microsoft).
   - **Ruff** (Astral).

---

## Verificación final

Abre la terminal integrada de VS Code (`Ctrl+ñ` o View → Terminal) y ejecuta:

```bash
uv run python -c "import sys; print(f'Python {sys.version.split()[0]} desde uv funcionando.')"
```

Si imprime la versión sin error, el setup está completo.

---

## Reset rápido (si algo se rompe)

```bash
rm -rf .venv uv.lock
uv sync
```

Esto borra el virtual environment y el lockfile, y vuelve a instalar todo desde cero. Suele resolver el 90% de los problemas raros.

---

## Troubleshooting

Para problemas concretos durante el setup, ver [`modulos/00-setup-mentalidad/sesion-00.2-setup-entorno/recursos.md`](modulos/00-setup-mentalidad/sesion-00.2-setup-entorno/recursos.md), sección "Troubleshooting".
