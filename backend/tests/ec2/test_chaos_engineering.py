import random
import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"chaos-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Chaos User",
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


def test_random_service_failure(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.post(
        "/api/v1/chaos/service-failure",
        json={
            "service": random.choice(
                [
                    "gateway",
                    "agent",
                    "workspace",
                    "rag",
                ]
            )
        },
        headers=headers,
    )

    assert response.status_code in (200, 202)


def test_network_latency_injection(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/network-latency",
        json={
            "latency_ms": 500,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_packet_loss_simulation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/packet-loss",
        json={
            "loss_percent": 20,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_database_failover(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/database-failover",
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_redis_failure(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/redis-outage",
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_vector_database_failure(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/vector-db-outage",
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_llm_provider_failure(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/llm-provider-outage",
        json={
            "provider": "openai",
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_agent_worker_crash(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/agent-crash",
        json={
            "workers": 3,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_kubernetes_pod_eviction(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/pod-eviction",
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_disk_pressure(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/disk-pressure",
        json={
            "usage_percent": 95,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_cpu_throttling(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/cpu-throttling",
        json={
            "cpu_percent": 90,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_memory_pressure(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chaos/memory-pressure",
        json={
            "memory_percent": 95,
        },
        headers=auth_headers,
    )

    assert response.status_code in (200, 202)


def test_recovery_verification(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chaos/recovery-status",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"


def test_system_stability_report(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chaos/report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "faults_injected" in body
    assert "recoveries" in body
    assert "availability" in body
    assert "recommendations" in body