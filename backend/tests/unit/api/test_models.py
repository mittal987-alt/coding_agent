import pytest

from fastapi.testclient import TestClient
def test_list_models(
    client: TestClient,
    auth_headers,
):

    response = client.get(
        "/api/v1/models",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    ) 
def test_get_model(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/gpt-5.5",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "gpt-5.5"
def test_register_model(
    client,
    auth_headers,
):

    payload = {
        "name": "custom-model",
        "provider": "ollama",
        "context_window": 32768,
        "supports_chat": True,
    }

    response = client.post(
        "/api/v1/models",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
def test_update_model(
    client,
    auth_headers,
):

    response = client.put(
        "/api/v1/models/custom-model",
        json={
            "enabled": False,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_delete_model(
    client,
    auth_headers,
):

    response = client.delete(
        "/api/v1/models/custom-model",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )
def test_model_health(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/gpt-5.5/health",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "healthy" in response.json()
def test_provider_list(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/providers",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_model_router(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/models/router",
        json={
            "task": "code_generation",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "selected_model" in body
def test_model_capabilities(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/gpt-5.5/capabilities",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_model_pricing(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/gpt-5.5/pricing",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_model_failover(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/models/failover",
        json={
            "primary": "gpt-5.5",
            "fallback": "claude-sonnet",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_invalid_model(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/models/unknown-model",
        headers=auth_headers,
    )

    assert response.status_code == 404
def test_model_auth_required(
    client,
):

    response = client.get(
        "/api/v1/models"
    )

    assert response.status_code == 401
def test_invalid_model_payload(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/models",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422