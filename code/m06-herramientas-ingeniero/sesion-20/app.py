"""Mini-app FastAPI para practicar Docker.

Expone dos endpoints:
- GET /         → saludo, lee MODE de env var (sin/con docker)
- GET /health   → health check para que docker (y compose) sepa si está sana

Uso local (sin Docker):
    uv run uvicorn app:app --host 0.0.0.0 --port 8000

Uso con Docker:
    docker build -t mini-saludo:0.1.0 .
    docker run -p 8000:8000 mini-saludo:0.1.0
"""

from __future__ import annotations

import os
import socket

from fastapi import FastAPI

app = FastAPI(title="mini-saludo", version="0.1.0")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "hello": "docker",
        "mode": os.environ.get("MODE", "local"),
        "host": socket.gethostname(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"estado": "ok"}
