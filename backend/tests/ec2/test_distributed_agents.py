import concurrent.futures
import threading
import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "distributed@example.com",
            "password": "Password123!",
            "full_name": "Distributed User",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "distributed@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_distributed_agent_workflow(
    client: TestClient,
):
    headers = authenticate(client)

    project = client.post(
        "/api/v1/projects",
        json={
            "name": "Distributed AI",
            "repository_url": "https://github.com/example/distributed.git",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    workflow = client.post(
        "/api/v1/agents/workflows",
        json={
            "project_id": project_id,
            "goal": "Build authentication service",
        },
        headers=headers,
    )

    assert workflow.status_code in (
        200,
        201,
    )

    workflow_id = workflow.json()["id"]

    roles = [
        "planner",
        "researcher",
        "architect",
        "coder",
        "reviewer",
        "tester",
        "documenter",
        "devops",
    ]

    responses = []

    def launch(role):
        response = client.post(
            f"/api/v1/agents/{workflow_id}/{role}",
            headers=headers,
        )

        responses.append(response.status_code)

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(roles),
    ) as executor:
        executor.map(launch, roles)

    assert all(
        status in (
            200,
            202,
        )
        for status in responses
    )


def test_agent_state_synchronization(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/workflows/workflow-1/state",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "completed_agents" in body


def test_inter_agent_messages(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/workflows/workflow-1/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_shared_memory(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/workflows/workflow-1/memory",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "entries" in body


def test_scheduler_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/scheduler",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "workers" in body


def test_worker_failover(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/failover",
        json={
            "worker": "worker-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_agent_reassignment(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/reassign",
        json={
            "workflow_id": "workflow-1",
            "agent": "coder",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_parallel_execution(
    client,
    auth_headers,
):
    statuses = []

    def worker():
        response = client.post(
            "/api/v1/agents/execute",
            json={
                "goal": "Generate CRUD APIs",
            },
            headers=auth_headers,
        )

        statuses.append(
            response.status_code,
        )

    threads = [
        threading.Thread(target=worker)
        for _ in range(10)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert all(
        status in (
            200,
            202,
        )
        for status in statuses
    )


def test_distributed_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "active_agents" in body
    assert "queued_tasks" in body
    assert "completed_tasks" in body


def test_workflow_completion(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/workflows/workflow-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "status" in body