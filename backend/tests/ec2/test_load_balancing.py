import concurrent.futures
import threading
import time

import pytest
from fastapi.testclient import TestClient


def create_user(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "load@example.com",
            "password": "Password123!",
            "full_name": "Load Test User",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "load@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_concurrent_api_requests(
    client: TestClient,
):
    headers = create_user(client)

    def worker():
        response = client.get(
            "/api/v1/health",
            headers=headers,
        )
        return response.status_code

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=25,
    ) as executor:
        results = list(
            executor.map(
                lambda _: worker(),
                range(100),
            )
        )

    assert all(
        status == 200
        for status in results
    )


def test_multiple_api_instances(
    client,
    auth_headers,
):
    responses = []

    for _ in range(20):
        response = client.get(
            "/api/v1/system/health",
            headers=auth_headers,
        )

        responses.append(response.status_code)

    assert all(
        status == 200
        for status in responses
    )


def test_session_affinity(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/session",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "session_id" in body


def test_background_job_distribution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/jobs",
        json={
            "type": "repository_index",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


def test_worker_queue_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/jobs/workers",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "workers" in body


def test_llm_request_distribution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/models/router",
        json={
            "prompt": "Explain dependency injection.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_vector_database_distribution(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/rag/cluster",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "nodes" in response.json()


def test_agent_distribution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/schedule",
        json={
            "goal": "Implement authentication module",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_parallel_chat_requests(
    client,
    auth_headers,
):
    results = []

    def send_message():
        response = client.post(
            "/api/v1/chat/message",
            json={
                "message": "Hello AI",
            },
            headers=auth_headers,
        )

        results.append(
            response.status_code,
        )

    threads = [
        threading.Thread(
            target=send_message,
        )
        for _ in range(30)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert all(
        code in (
            200,
            202,
        )
        for code in results
    )


def test_autoscaling_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/autoscaling",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "desired_replicas" in body
    assert "current_replicas" in body


def test_request_queue_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/queue",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "pending_jobs" in body
    assert "running_jobs" in body


def test_cluster_health(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/cluster",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "healthy_nodes" in body


def test_load_balancer_health(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/load-balancer",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "status" in body