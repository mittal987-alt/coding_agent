import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"observability-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Observability User",
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

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_health_endpoint(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.get(
        "/api/v1/health",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"


def test_readiness_probe(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/health/ready",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert response.json()["ready"] is True


def test_liveness_probe(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/health/live",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert response.json()["alive"] is True


def test_prometheus_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "http_requests_total" in response.text


def test_open_telemetry_traces(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/traces",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "traces" in body


def test_request_trace(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/request-trace",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "trace_id" in body
    assert "span_id" in body


def test_structured_logs(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200

    logs = response.json()

    assert isinstance(
        logs,
        list,
    )


def test_log_correlation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/correlation",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "correlation_id" in body


def test_error_aggregation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/errors",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_errors" in body


def test_service_dependency_graph(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/dependencies",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "services" in body


def test_alert_generation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/alerts",
        headers=auth_headers,
    )

    assert response.status_code == 200

    alerts = response.json()

    assert isinstance(
        alerts,
        list,
    )


def test_dashboard_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/dashboard",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "cpu_usage" in body
    assert "memory_usage" in body
    assert "request_rate" in body


def test_trace_exporters(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/exporters",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "jaeger" in body
    assert "otlp" in body


def test_metrics_summary(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/observability/summary",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "metrics" in body
    assert "traces" in body
    assert "logs" in body