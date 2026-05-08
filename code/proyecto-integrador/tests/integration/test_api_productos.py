"""Integration tests de la API de productos contra una DB SQLite efímera."""

from fastapi.testclient import TestClient


def test_health_responde_200(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["estado"] == "ok"
    assert body["servicio"] == "tiendapro"
    assert isinstance(body["productos_en_db"], int)


def test_listar_productos_devuelve_array(client: TestClient) -> None:
    response = client.get("/productos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_crear_producto_devuelve_201(client: TestClient) -> None:
    payload = {
        "nombre": "Producto Test",
        "categoria": "test",
        "precio": 9.99,
        "stock": 5,
    }
    response = client.post("/productos", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Producto Test"
    assert body["precio"] == 9.99
    assert body["stock"] == 5


def test_producto_creado_aparece_en_listado(client: TestClient) -> None:
    client.post(
        "/productos",
        json={
            "nombre": "Producto Persistido",
            "categoria": "test",
            "precio": 1.0,
            "stock": 1,
        },
    )
    listado = client.get("/productos").json()
    nombres = {p["nombre"] for p in listado}
    assert "Producto Persistido" in nombres


def test_filtro_por_categoria(client: TestClient) -> None:
    client.post(
        "/productos",
        json={"nombre": "Auricular A", "categoria": "audio", "precio": 50.0, "stock": 2},
    )
    client.post(
        "/productos",
        json={"nombre": "Cable X", "categoria": "cables", "precio": 5.0, "stock": 10},
    )

    audio = client.get("/productos", params={"categoria": "audio"}).json()
    assert all(p["categoria"] == "audio" for p in audio)
    nombres = {p["nombre"] for p in audio}
    assert "Auricular A" in nombres
    assert "Cable X" not in nombres


def test_filtro_solo_disponibles(client: TestClient) -> None:
    client.post(
        "/productos",
        json={"nombre": "Sin stock", "categoria": "x", "precio": 1.0, "stock": 0},
    )
    client.post(
        "/productos",
        json={"nombre": "Con stock", "categoria": "x", "precio": 1.0, "stock": 3},
    )

    disponibles = client.get("/productos", params={"solo_disponibles": "true"}).json()
    nombres = {p["nombre"] for p in disponibles}
    assert "Con stock" in nombres
    assert "Sin stock" not in nombres


def test_response_trae_x_request_id_header(client: TestClient) -> None:
    response = client.get("/health")
    headers_lower = {k.lower() for k in response.headers}
    assert "x-request-id" in headers_lower
