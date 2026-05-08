"""Inspector de la config local de git.

Útil para verificar que tu setup esté bien antes de empezar los ejercicios:
- user.name y user.email seteados.
- pull.rebase configurado a true (recomendación de la sesión).
- Alias `lg` (sugerido en el README).

Uso:
    uv run python main.py
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    label: str
    valor: str | None
    ok: bool
    sugerencia: str | None = None


def _git_config(key: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "config", "--get", key],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    valor = out.stdout.strip()
    return valor or None


def chequear_setup() -> list[CheckResult]:
    if shutil.which("git") is None:
        return [
            CheckResult(
                label="git instalado",
                valor=None,
                ok=False,
                sugerencia="Instalá git: https://git-scm.com/downloads",
            )
        ]

    nombre = _git_config("user.name")
    email = _git_config("user.email")
    pull_rebase = _git_config("pull.rebase")
    alias_lg = _git_config("alias.lg")

    return [
        CheckResult(
            label="user.name",
            valor=nombre,
            ok=nombre is not None,
            sugerencia='git config --global user.name "Tu Nombre"',
        ),
        CheckResult(
            label="user.email",
            valor=email,
            ok=email is not None,
            sugerencia='git config --global user.email "tu@email.com"',
        ),
        CheckResult(
            label="pull.rebase",
            valor=pull_rebase,
            ok=pull_rebase == "true",
            sugerencia="git config --global pull.rebase true",
        ),
        CheckResult(
            label="alias.lg",
            valor=alias_lg,
            ok=alias_lg is not None,
            sugerencia=(
                'git config --global alias.lg '
                '"log --oneline --graph --all --decorate"'
            ),
        ),
    ]


def imprimir(checks: list[CheckResult]) -> None:
    print("─" * 60)
    print("Inspector de setup de git")
    print("─" * 60)
    for c in checks:
        marca = "✓" if c.ok else "✗"
        valor = c.valor or "(sin setear)"
        print(f"  {marca} {c.label:<14} {valor}")
        if not c.ok and c.sugerencia:
            print(f"       sugerencia: {c.sugerencia}")
    print("─" * 60)
    fallidos = sum(1 for c in checks if not c.ok)
    if fallidos == 0:
        print("Todo en orden. Vení a leer ejercicios.md y arrancá el ejercicio guiado.")
    else:
        print(f"Te faltan {fallidos} item(s). Corré los comandos sugeridos y volvé.")


def main() -> None:
    imprimir(chequear_setup())


if __name__ == "__main__":
    main()
