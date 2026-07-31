import pytest

from fastapi.testclient import TestClient
def test_execute_agent(
    client: TestClient,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/execute",
        json={
            "goal": "Implement JWT authentication",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_create_plan(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/plan",
        json={
            "task": "Build REST API",
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
            "task": "Create an AI IDE",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json()["subtasks"],
        list,
    )
def test_workflow_execution(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/workflow",
        json={
            "workflow": "full_repository_analysis",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_agent_status(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/agents/status",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_cancel_execution(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/cancel/test-workflow",
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
        "/api/v1/agents/approve",
        json={
            "workflow_id": "workflow-1",
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
def test_agent_requires_auth(
    client,
):

    response = client.get(
        "/api/v1/agents/status",
    )

    assert response.status_code == 401
def test_invalid_workflow(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/retry/invalid-workflow",
        headers=auth_headers,
    )

    assert response.status_code == 404
def test_invalid_goal(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/agents/execute",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422