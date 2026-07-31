import pytest

from fastapi.testclient import TestClient


def test_create_plan(
    client: TestClient,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/plan",
        json={
            "task": "Build a FastAPI authentication module",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "steps" in body


def test_task_decomposition(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/decompose",
        json={
            "task": "Create a production AI IDE",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "subtasks" in body


def test_execute_agent(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/execute",
        json={
            "goal": "Implement JWT Authentication",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    body = response.json()

    assert "workflow_id" in body


def test_workflow_status(
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


def test_pause_workflow(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/workflows/workflow-1/pause",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_resume_workflow(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/workflows/workflow-1/resume",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_cancel_workflow(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/workflows/workflow-1/cancel",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_retry_workflow(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/workflows/workflow-1/retry",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_human_approval(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/workflows/workflow-1/approve",
        json={
            "approved": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_agent_history(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/history",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_agent_logs(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_agent_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "completed_workflows" in body


def test_invalid_workflow(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/agents/workflows/invalid-id",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/agents/history",
    )

    assert response.status_code == 401


def test_invalid_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/agents/execute",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422