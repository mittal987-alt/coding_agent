import pytest

from fastapi.testclient import TestClient


def test_multi_agent_workflow(
    client: TestClient,
):
    # ---------------------------------------------------------
    # Register User
    # ---------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "multiagent@example.com",
            "password": "Password123!",
            "full_name": "Multi Agent User",
        },
    )

    assert register.status_code == 201

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "multiagent@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # ---------------------------------------------------------
    # Create Project
    # ---------------------------------------------------------
    project = client.post(
        "/api/v1/projects",
        json={
            "name": "AI CRM",
            "description": "Multi Agent Test",
            "repository_url": "https://github.com/example/crm.git",
            "language": "Python",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ---------------------------------------------------------
    # Planner Agent
    # ---------------------------------------------------------
    planner = client.post(
        "/api/v1/agents/planner",
        json={
            "project_id": project_id,
            "goal": "Build JWT authentication system",
        },
        headers=headers,
    )

    assert planner.status_code == 200

    workflow_id = planner.json()["workflow_id"]

    # ---------------------------------------------------------
    # Research Agent
    # ---------------------------------------------------------
    research = client.post(
        f"/api/v1/agents/{workflow_id}/research",
        headers=headers,
    )

    assert research.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Architecture Agent
    # ---------------------------------------------------------
    architecture = client.post(
        f"/api/v1/agents/{workflow_id}/architecture",
        headers=headers,
    )

    assert architecture.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Coding Agent
    # ---------------------------------------------------------
    coding = client.post(
        f"/api/v1/agents/{workflow_id}/coding",
        headers=headers,
    )

    assert coding.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Testing Agent
    # ---------------------------------------------------------
    testing = client.post(
        f"/api/v1/agents/{workflow_id}/testing",
        headers=headers,
    )

    assert testing.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Review Agent
    # ---------------------------------------------------------
    review = client.post(
        f"/api/v1/agents/{workflow_id}/review",
        headers=headers,
    )

    assert review.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Documentation Agent
    # ---------------------------------------------------------
    docs = client.post(
        f"/api/v1/agents/{workflow_id}/documentation",
        headers=headers,
    )

    assert docs.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Git Agent
    # ---------------------------------------------------------
    git = client.post(
        f"/api/v1/agents/{workflow_id}/git",
        headers=headers,
    )

    assert git.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Workflow Status
    # ---------------------------------------------------------
    status = client.get(
        f"/api/v1/agents/workflows/{workflow_id}",
        headers=headers,
    )

    assert status.status_code == 200

    body = status.json()

    assert "status" in body

    # ---------------------------------------------------------
    # Workflow Logs
    # ---------------------------------------------------------
    logs = client.get(
        f"/api/v1/agents/workflows/{workflow_id}/logs",
        headers=headers,
    )

    assert logs.status_code == 200

    assert isinstance(
        logs.json(),
        list,
    )

    # ---------------------------------------------------------
    # Workflow Metrics
    # ---------------------------------------------------------
    metrics = client.get(
        f"/api/v1/agents/workflows/{workflow_id}/metrics",
        headers=headers,
    )

    assert metrics.status_code == 200

    body = metrics.json()

    assert "completed_tasks" in body

    # ---------------------------------------------------------
    # Final Result
    # ---------------------------------------------------------
    result = client.get(
        f"/api/v1/agents/workflows/{workflow_id}/result",
        headers=headers,
    )

    assert result.status_code == 200

    body = result.json()

    assert "artifacts" in body

    # ---------------------------------------------------------
    # Cleanup
    # ---------------------------------------------------------
    delete = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )

    assert delete.status_code in (
        200,
        204,
    )