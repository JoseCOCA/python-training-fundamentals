# Sandbox de S19 — Git en serio

Sandbox para practicar branches, rebase, conflictos y Conventional Commits.

## Qué hay

- `main.py` — script Python que inspecciona tu config local de git y te dice qué te falta setear.
- `playground/` — directorio para crear repos de juguete durante los ejercicios. **Ignorado** por git (este sandbox tiene su propio `.gitignore`), así podés crear y romper repos sin contaminar el repo del curso.

## Cómo correr el inspector

Desde dentro de este directorio:

```bash
uv sync
uv run python main.py
```

Ejemplo de salida:

```
────────────────────────────────────────────────────────────
Inspector de setup de git
────────────────────────────────────────────────────────────
  ✓ user.name       Tu Nombre
  ✓ user.email      tu@email.com
  ✗ pull.rebase     (sin setear)
       sugerencia: git config --global pull.rebase true
  ✗ alias.lg        (sin setear)
       sugerencia: git config --global alias.lg "log --oneline --graph --all --decorate"
────────────────────────────────────────────────────────────
Te faltan 2 item(s). Corré los comandos sugeridos y volvé.
```

Corré los comandos sugeridos hasta que todo dé `✓`. Después seguí con [`ejercicios.md`](../../../docs/modulos/06-herramientas-ingeniero/sesion-19-git/ejercicios.md).

## Cómo arrancar los ejercicios

```bash
mkdir -p playground && cd playground
mkdir tienda && cd tienda
git init
# ... seguí los pasos del ejercicio guiado ...
```

Todo lo que hagas dentro de `playground/` queda **fuera** del repo del curso (gracias al `.gitignore` local). Borralo cuando termines:

```bash
rm -rf playground
```
