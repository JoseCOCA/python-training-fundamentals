# S19 — Ejercicios

> **Tiempo estimado:** ~70 min. Tres bloques: ejercicio guiado en un sandbox de juguete (branches, conflicto, rebase interactivo), libres para profundizar (revert, stash, configuración), y una **revisión** del propio repo del curso (sin reescribir historia — solo notas).

---

## 0. Antes de empezar

Tu sandbox vive en `code/m06-herramientas-ingeniero/sesion-19/`. Ahí tenés un script y un README, pero los ejercicios de hoy se hacen sobre un **sub-repo de juguete** que vamos a crear dentro de `playground/`. Ese subdirectorio está en el `.gitignore` del repo del curso, así que podés crear y romper repos ahí sin contaminar el principal.

```bash
cd code/m06-herramientas-ingeniero/sesion-19
mkdir -p playground && cd playground
```

Verificá tu config de git antes de seguir:

```bash
git config user.name
git config user.email
```

Si están vacíos:

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@email.com"
```

Y un alias útil que vas a usar todo el tiempo:

```bash
git config --global alias.lg "log --oneline --graph --all --decorate"
```

## 1. Ejercicio guiado — Branches, conflicto y rebase interactivo

### Paso 1.1 — Crear un repo de juguete

Adentro de `playground/`:

```bash
mkdir tienda && cd tienda
git init
echo "# Tienda de prueba" > README.md
echo "producto,precio" > productos.csv
echo "manzana,10" >> productos.csv
git add .
git commit -m "feat: estructura inicial"
git lg
```

Vas a ver un único commit. Tu `HEAD` y tu branch (`main` o `master` según tu git default) apuntan a él.

### Paso 1.2 — Una branch de feature

```bash
git switch -c feature/agregar-pera
echo "pera,15" >> productos.csv
git add productos.csv
git commit -m "feat: agregar pera al catálogo"

echo "banana,8" >> productos.csv
git add productos.csv
git commit -m "feat: agregar banana al catálogo"

git lg
```

Tres commits ahora. Dos en `feature/agregar-pera`, uno compartido con `main`.

### Paso 1.3 — Cambio paralelo en `main` (genera el conflicto)

Mientras tanto, simulamos que en `main` alguien ya editó el mismo archivo:

```bash
git switch main
echo "manzana,12" > productos.csv     # OJO: > (no >>) — pisa el archivo
echo "uva,20" >> productos.csv
git add productos.csv
git commit -m "feat: subir precio de manzana, agregar uva"

git lg
```

Mirá el grafo: `main` y `feature/agregar-pera` divergieron.

### Paso 1.4 — Provocar el conflicto con merge

```bash
git merge feature/agregar-pera
```

Vas a ver:

```
Auto-merging productos.csv
CONFLICT (content): Merge conflict in productos.csv
Automatic merge failed; fix conflicts and then commit the result.
```

Abrí `productos.csv`. Vas a ver algo así:

```
producto,precio
<<<<<<< HEAD
manzana,12
uva,20
=======
manzana,10
pera,15
banana,8
>>>>>>> feature/agregar-pera
```

Decidí qué querés (lo razonable: precio actualizado de manzana + las tres frutas nuevas):

```
producto,precio
manzana,12
pera,15
banana,8
uva,20
```

Borrá los marcadores `<<<<<<<`, `=======`, `>>>>>>>`. Después:

```bash
git status                          # vas a ver el archivo en "Unmerged paths"
git add productos.csv               # le decís a git "ya está"
git status                          # ahora dice "All conflicts fixed but you are still merging"
git merge --continue                # o git commit, te abre editor con mensaje de merge
git lg
```

Mirá el grafo: ahora hay un commit de merge con dos padres.

### Paso 1.5 — Repetí el escenario, esta vez con rebase

Volvé al estado pre-merge:

```bash
git reset --hard HEAD~1     # tira el merge commit (estamos en sandbox, --hard es ok acá)
git lg
```

Mirá: `main` y `feature/agregar-pera` divergidas otra vez. Ahora rebaseamos:

```bash
git switch feature/agregar-pera
git rebase main
```

Te aparece el mismo conflicto, **pero la historia resultante va a ser distinta** — no habrá merge commit, sino tus dos commits **reaplicados** sobre `main`.

Resolvé el conflicto igual que antes (editá `productos.csv`, dejá lo correcto, borrá marcadores):

```bash
git add productos.csv
git rebase --continue
```

Te puede pedir confirmar el mensaje de cada commit. Aceptá los que están.

```bash
git lg
```

Mirá: tus dos commits ahora aparecen **encima** del último de `main`. Lineal, sin merge commit. Esa es la diferencia visible entre merge y rebase.

### Paso 1.6 — Mergear `feature` a `main` con fast-forward

Como ahora `feature/agregar-pera` es descendiente directo de `main`:

```bash
git switch main
git merge feature/agregar-pera
```

Va a decir `Fast-forward`. La branch `main` simplemente avanza al commit de `feature`. Sin merge commit.

```bash
git lg
git branch -d feature/agregar-pera
```

Eliminás la branch (es solo un puntero, los commits siguen vivos).

### Paso 1.7 — Rebase interactivo: limpiá una historia ruidosa

Vamos a generar historia "sucia" a propósito y limpiarla.

```bash
git switch -c feature/limpiar-csv

echo "kiwi,18" >> productos.csv
git add productos.csv && git commit -m "wip"

echo "frutilla,25" >> productos.csv
git add productos.csv && git commit -m "más fruta"

echo "ananá,30" >> productos.csv
git add productos.csv && git commit -m "."

git lg
```

Tres commits con mensajes basura. Vamos a fusionarlos en uno solo bien escrito:

```bash
git rebase -i HEAD~3
```

Te abre el editor con:

```
pick a1b2c3d wip
pick d4e5f6g más fruta
pick 7h8i9j0 .
```

Cambiá las dos últimas líneas a `fixup` (o `f`):

```
pick a1b2c3d wip
fixup d4e5f6g más fruta
fixup 7h8i9j0 .
```

Guardá y cerrá. Ahora cambiá el mensaje del commit resultante con `reword`:

```bash
git rebase -i HEAD~1
```

Cambiá `pick` por `reword` (o `r`). Cerrá; te va a abrir un nuevo editor con el mensaje del commit. Reescribilo:

```
feat(catalogo): agregar kiwi, frutilla y ananá
```

Guardá. Mirá:

```bash
git lg
```

Un solo commit, mensaje claro. Eso es lo que verá el reviewer.

### Paso 1.8 — Reflexión

Antes de seguir, contestá mentalmente:

- ¿Por qué un rebase reescribe los SHAs de los commits?
- Si `feature/limpiar-csv` ya estuviera pushada y otra persona la hubiera bajado, ¿qué problema tendrías al hacer este último rebase?
- ¿Cuándo te conviene `merge --no-ff` (fuerza un merge commit aunque sea fast-forward)?

(Las respuestas no las escribís — son para internalizar. Si una no te sale, releé la sección 4.4 del README.)

## 2. Ejercicios libres

### 2.1. `git revert` vs `git reset`

En el mismo repo de juguete:

```bash
git switch main
echo "PROBLEMA INTRODUCIDO" >> README.md
git add README.md && git commit -m "feat: cambio que vamos a revertir"
git lg
```

Probá las dos formas de deshacerlo:

```bash
# Opción A — revert (commit nuevo que invierte el cambio)
git revert HEAD            # te abre editor con mensaje "Revert ..."
git lg                     # ahora hay DOS commits: el malo + el revert

# Volvé al estado anterior para probar la otra opción
git reset --hard HEAD~2

# Repetí el commit malo
echo "PROBLEMA INTRODUCIDO" >> README.md
git add README.md && git commit -m "feat: cambio que vamos a revertir"

# Opción B — reset (reescribe historia)
git reset --hard HEAD~1
git lg                     # el commit malo desapareció
```

Pregunta: ¿en cuál de las dos podrías recuperar el commit "malo" si te arrepentís? Respuesta: en ambas, mirando `git reflog` — pero la opción A lo deja **explícito** en la historia. La B obliga a pelearse con `reflog`.

### 2.2. `git stash`

Estás editando algo y aparece un fix urgente:

```bash
echo "WIP cambios sin terminar" >> productos.csv
git status                  # ves el cambio sin commitear

git stash push -m "wip refactor"
git status                  # working tree limpio

# ... harías el fix urgente acá ...

git stash list              # listás lo que tenés guardado
git stash pop               # recuperás y borrás del stash
```

Probá también `git stash apply` (recupera pero **no borra** del stash) y `git stash drop` (borra).

### 2.3. `.gitignore` para Python

Creá un `.gitignore` en `tienda/`:

```gitignore
__pycache__/
*.pyc
.venv/
.env
*.db
.mypy_cache/
.ruff_cache/
.pytest_cache/
```

Verificá:

```bash
mkdir __pycache__ && touch __pycache__/test.pyc
echo "secret=hello" > .env
git status               # ninguno de los dos debería aparecer
```

### 2.4. Cuando `.env` ya estuvo trackeado

Simulalo:

```bash
echo "API_KEY=secreto" > config.env
git add config.env && git commit -m "config: settings"
# Ahora te das cuenta del error. Lo querés sacar del tracking pero conservar el archivo en disco.
git rm --cached config.env
echo "config.env" >> .gitignore
git add .gitignore
git commit -m "chore: deja de trackear config.env"

ls -la                  # config.env sigue en disco
git status              # untracked, ignorado
```

(En la vida real: si era un secreto **rotalo**, asumí filtración. La historia anterior conserva el archivo a menos que la reescribas.)

### 2.5. `git diff` con argumentos

Practicá las variantes:

```bash
git diff                           # working tree vs index
git diff --staged                  # index vs último commit (HEAD)
git diff HEAD                      # working tree vs último commit
git diff main..feature/X           # diferencia entre dos branches
git diff main..HEAD -- README.md   # diferencia solo en README.md
```

Cuanto más cómodo te sientas leyendo diffs en la terminal, menos vas a depender de un GUI y más rápido vas a iterar.

### 2.6. Un alias propio

Tu turno: agregá uno que te resulte útil. Sugerencias:

```bash
git config --global alias.s "status -sb"
git config --global alias.amend "commit --amend --no-edit"
git config --global alias.unstage "restore --staged"
git config --global alias.last "log -1 HEAD"
```

Después: `git s`, `git unstage archivo.py`, etc.

### 2.7. (Opcional) GitHub: PR sobre tu propio repo

Si tenés cuenta de GitHub, creá un repo `tienda-test`, pushá lo del playground, abrí una branch nueva, pushala, y abrí un PR a `main` desde la web. Mirá cómo se ve el grafo en GitHub vs `git lg` localmente. La interfaz visual ayuda a entender el modelo, pero todo lo que ves ahí lo podés ver desde la terminal.

```bash
gh repo create tienda-test --private --source=. --push
git switch -c feature/algo
echo "cambio" >> README.md
git add README.md && git commit -m "feat: cambio menor"
git push -u origin feature/algo
gh pr create --fill                # abre el PR
```

(Necesitás tener `gh` instalado y autenticado: `gh auth login`.)

## 3. Aporte al proyecto integrador

Esta sesión **no toca código del integrador**. El cierre del Módulo 6 (con tag `proyecto-m6`) viene en S21 después de sumar tests, Dockerfile y README final.

Lo que sí podés hacer hoy: un **mini-audit** de tu propia historia en el repo del curso.

```bash
cd /home/jose/Proyectos/python-training-fundamentals
git log --oneline | head -30
```

Hacete estas preguntas:

- ¿Hay commits con mensajes vagos (`wip`, `cambios`, `arreglo`)?
- ¿Hay commits que pegaron dos cambios no relacionados ("agregué endpoint y de paso refactoreé X")?
- ¿Algún commit tiene el formato Conventional Commits? ¿Cuáles?

**No reescribas la historia del repo del curso** — ya está pushada y no vale la pena. Pero anotá mentalmente qué harías distinto en el próximo repo. Eso es la diferencia entre alguien que aprendió Conventional Commits y alguien que los **practica**.

## 4. Limpieza

Cuando termines, podés borrar el playground:

```bash
cd /home/jose/Proyectos/python-training-fundamentals/code/m06-herramientas-ingeniero/sesion-19
rm -rf playground
```

Como `playground/` está en el `.gitignore` del sandbox, nada se versionó. Podés volver a crearlo cuando quieras practicar.

---

Cuando termines, volvé al [README](README.md) y respondé las preguntas de auto-evaluación. Si todas se contestan sin dudar, pasá a [S20 — Docker](../sesion-20-docker/README.md).
