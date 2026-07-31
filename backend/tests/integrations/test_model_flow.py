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


def test_register_model(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/models",
        json={
            "name": "custom-model",
            "provider": "ollama",
            "context_window": 32768,
            "supports_chat": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "custom-model"


def test_model_health(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/custom-model/health",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "healthy" in body


def test_model_capabilities(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/custom-model/capabilities",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "chat" in body


def test_provider_list(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/providers",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_model_routing(
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


def test_streaming_generation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/models/generate",
        json={
            "model": "custom-model",
            "prompt": "Write a FastAPI endpoint",
            "stream": True,
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_token_usage(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/usage",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_tokens" in body


def test_cost_tracking(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/costs",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_cost" in body


def test_failover(
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


def test_disable_model(
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


def test_model_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/models/unknown-model",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/models",
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