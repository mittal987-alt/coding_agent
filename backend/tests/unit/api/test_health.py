import pytest
from fastapi.testclient import TestClient
def test_health_endpoint(
    client: TestClient,
):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
def test_ready_endpoint(
    client: TestClient,
):
    response = client.get("/ready")

    assert response.status_code == 200

    body = response.json()

    assert body["ready"] is True
def test_live_endpoint(
    client: TestClient,
):
    response = client.get("/live")

    assert response.status_code == 200

    assert response.json()["alive"] is True


def test_openapi_schema(
    client: TestClient,
):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert "paths" in schema
def test_docs_endpoint(
    client: TestClient,
):
    response = client.get("/docs")

    assert response.status_code == 200
def test_redoc_endpoint(
    client: TestClient,
):
    response = client.get("/redoc")

    assert response.status_code == 200
def test_health_response_time(
    client: TestClient,
):
    import time

    start = time.perf_counter()

    response = client.get("/health")

    elapsed = time.perf_counter() - start

    assert response.status_code == 200

    assert elapsed < 1
def test_health_content_type(
    client: TestClient,
):
    response = client.get("/health")

    assert (
        response.headers["content-type"]
        == "application/json"
    )
@pytest.mark.parametrize(
    "method",
    [
        "post",
        "put",
        "delete",
        "patch",
    ],
)
def test_invalid_methods(
    client: TestClient,
    method,
):
    response = getattr(
        client,
        method,
    )("/health")

    assert response.status_code in (
        405,
        404,
    )
def test_health_schema(
    client: TestClient,
):
    response = client.get("/health")

    body = response.json()

    expected = {
        "status",
        "timestamp",
        "version",
    }

    assert expected.issubset(body.keys())