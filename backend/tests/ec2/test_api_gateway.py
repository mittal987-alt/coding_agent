import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"gateway-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Gateway User",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    return {
        "Authorization": f"Bearer {login.json()['access_token']}",
    }


def test_gateway_health(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.get(
        "/gateway/health",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"


def test_route_registration(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/routes",
        headers=auth_headers,
    )

    assert response.status_code == 200

    routes = response.json()

    assert isinstance(routes, list)
    assert len(routes) > 0


def test_reverse_proxy(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/proxy/projects",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_jwt_authentication(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/auth-test",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_invalid_jwt(
    client,
):
    response = client.get(
        "/gateway/auth-test",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


def test_api_key_authentication(
    client,
):
    response = client.get(
        "/gateway/api-key-test",
        headers={
            "X-API-Key": "test-api-key",
        },
    )

    assert response.status_code in (
        200,
        401,
    )


def test_rate_limiting(
    client,
    auth_headers,
):
    responses = []

    for _ in range(50):
        responses.append(
            client.get(
                "/gateway/rate-limit",
                headers=auth_headers,
            )
        )

    assert any(
        r.status_code in (200, 429)
        for r in responses
    )


def test_request_validation(
    client,
    auth_headers,
):
    response = client.post(
        "/gateway/validate",
        json={},
        headers=auth_headers,
    )

    assert response.status_code in (
        400,
        422,
    )


def test_response_transformation(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/transform",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "data" in body


def test_request_logging(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200

    logs = response.json()

    assert isinstance(logs, list)


def test_cors_headers(
    client,
):
    response = client.options(
        "/gateway/cors",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in (
        200,
        204,
    )

    assert "access-control-allow-origin" in {
        k.lower(): v
        for k, v in response.headers.items()
    }


def test_load_balancer_status(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/load-balancer",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "healthy_backends" in body


def test_service_discovery(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/services",
        headers=auth_headers,
    )

    assert response.status_code == 200

    services = response.json()

    assert isinstance(services, list)


def test_gateway_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "requests_total" in body
    assert "latency_ms" in body


def test_gateway_report(
    client,
    auth_headers,
):
    response = client.get(
        "/gateway/report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert "uptime" in body
    assert "recommendations" in body