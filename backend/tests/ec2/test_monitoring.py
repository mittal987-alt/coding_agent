import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"monitor-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Monitoring User",
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


def test_prometheus_targets(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.get(
        "/api/v1/monitoring/prometheus/targets",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "targets" in body


def test_prometheus_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "http_requests_total" in response.text


def test_grafana_dashboards(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/grafana/dashboards",
        headers=auth_headers,
    )

    assert response.status_code == 200

    dashboards = response.json()

    assert isinstance(
        dashboards,
        list,
    )


def test_alertmanager_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/alertmanager",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "status" in body


def test_application_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/application",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "requests_per_second" in body
    assert "latency_ms" in body


def test_database_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/database",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "connections" in body
    assert "query_latency_ms" in body


def test_redis_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/redis",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "memory_usage" in body
    assert "connected_clients" in body


def test_vector_database_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/vector-db",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "index_size" in body
    assert "search_latency_ms" in body


def test_llm_provider_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/models",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "providers" in body


def test_agent_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/agents",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "active_agents" in body
    assert "queued_tasks" in body


def test_kubernetes_monitoring(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/kubernetes",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "nodes" in body
    assert "pods" in body


def test_sli_slo_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/slo",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "availability" in body
    assert "latency" in body
    assert "error_budget" in body


def test_alert_rules(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/alerts/rules",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_incident_reporting(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/incidents",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "active_incidents" in body


def test_monitoring_health(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/monitoring/health",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"