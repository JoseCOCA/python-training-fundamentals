"""Integration tests del manejo de errores HTTP."""

from fastapi.testclient import TestClient


def test_payload_invalido_devuelve_422_con_formato_propio(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={"nombre": "", "categoria": "x", "precio": -1.0},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "datos inválidos"
    assert isinstance(body.get("errores"), list)
    assert len(body["errores"]) >= 1
    error = body["errores"][0]
    assert {"campo", "mensaje", "tipo"} <= set(error.keys())


def test_campo_extra_es_rechazado(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={
            "nombre": "X",
            "categoria": "c",
            "precio": 1.0,
            "color": "rojo",
        },
    )
    assert response.status_code == 422


def test_precio_excesivo_devuelve_422(client: TestClient) -> None:
    response = client.post(
        "/productos",
        json={"nombre": "X", "categoria": "c", "precio": 9_999_999.0},
    )
    assert response.status_code == 422


def test_metodo_no_permitido_devuelve_405(client: TestClient) -> None:
    response = client.put("/health")
    assert response.status_code == 405
