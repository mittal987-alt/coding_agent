import pytest

from fastapi.testclient import TestClient


def test_failure_recovery_workflow(
    client: TestClient,
):
    # ---------------------------------------------------------
    # Register User
    # ---------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "recovery@example.com",
            "password": "Password123!",
            "full_name": "Recovery User",
        },
    )

    assert register.status_code == 201

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "recovery@example.com",
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
            "name": "Failure Recovery",
            "repository_url": "https://github.com/example/project.git",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ---------------------------------------------------------
    # Simulate Repository Clone Failure
    # ---------------------------------------------------------
    clone = client.post(
        "/api/v1/projects/import",
        json={
            "project_id": project_id,
            "simulate_failure": True,
        },
        headers=headers,
    )

    assert clone.status_code in (
        500,
        503,
    )

    # ---------------------------------------------------------
    # Retry Repository Clone
    # ---------------------------------------------------------
    retry_clone = client.post(
        "/api/v1/projects/import",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert retry_clone.status_code in (
        200,
        201,
        202,
    )

    # ---------------------------------------------------------
    # Simulate Agent Failure
    # ---------------------------------------------------------
    agent = client.post(
        "/api/v1/agents/execute",
        json={
            "goal": "Generate authentication",
            "simulate_failure": True,
        },
        headers=headers,
    )

    assert agent.status_code in (
        500,
        503,
    )

    # ---------------------------------------------------------
    # Retry Agent
    # ---------------------------------------------------------
    retry_agent = client.post(
        "/api/v1/agents/retry",
        json={
            "goal": "Generate authentication",
        },
        headers=headers,
    )

    assert retry_agent.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Simulate Tool Failure
    # ---------------------------------------------------------
    tool = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "python",
            "arguments": {
                "simulate_failure": True,
            },
        },
        headers=headers,
    )

    assert tool.status_code in (
        500,
        503,
    )

    # ---------------------------------------------------------
    # Retry Tool
    # ---------------------------------------------------------
    retry_tool = client.post(
        "/api/v1/tools/retry",
        json={
            "execution_id": "tool-1",
        },
        headers=headers,
    )

    assert retry_tool.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Simulate LLM Provider Failure
    # ---------------------------------------------------------
    llm = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Explain JWT",
            "simulate_provider_failure": True,
        },
        headers=headers,
    )

    assert llm.status_code in (
        500,
        503,
    )

    # ---------------------------------------------------------
    # Provider Failover
    # ---------------------------------------------------------
    failover = client.post(
        "/api/v1/models/failover",
        json={
            "primary": "gpt-5.5",
            "fallback": "claude-sonnet",
        },
        headers=headers,
    )

    assert failover.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Retry Chat
    # ---------------------------------------------------------
    retry_chat = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Explain JWT",
        },
        headers=headers,
    )

    assert retry_chat.status_code == 200

    # ---------------------------------------------------------
    # Simulate Workspace Failure
    # ---------------------------------------------------------
    workspace = client.post(
        "/api/v1/workspaces/recover",
        json={
            "project_id": project_id,
            "simulate_corruption": True,
        },
        headers=headers,
    )

    assert workspace.status_code in (
        500,
        503,
    )

    # ---------------------------------------------------------
    # Recover Workspace
    # ---------------------------------------------------------
    recover = client.post(
        "/api/v1/workspaces/recover",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert recover.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Workflow Health
    # ---------------------------------------------------------
    health = client.get(
        "/api/v1/system/health",
        headers=headers,
    )

    assert health.status_code == 200

    body = health.json()

    assert body["status"] == "healthy"

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