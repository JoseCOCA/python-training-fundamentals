"""Mini-app FastAPI para practicar TestClient.

Dos endpoints:
- GET /saludo            → siempre devuelve {"mensaje": "hola"}
- GET /eco?msg=...       → responde con el mensaje recibido (422 si falta)
"""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="mini-api", version="0.1.0")


@app.get("/saludo")
def saludo() -> dict[str, str]:
    return {"mensaje": "hola"}


@app.get("/eco")
def eco(msg: str) -> dict[str, str]:
    return {"dijiste": msg}
