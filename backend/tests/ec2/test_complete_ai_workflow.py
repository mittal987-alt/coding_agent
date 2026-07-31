import pytest

from fastapi.testclient import TestClient


def test_complete_ai_workflow(
    client: TestClient,
):
    # ------------------------------------------------------------------
    # Register User
    # ------------------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "e2e@example.com",
            "password": "Password123!",
            "full_name": "E2E User",
        },
    )

    assert register.status_code == 201

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "e2e@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    tokens = login.json()

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}"
    }

    # ------------------------------------------------------------------
    # Create Project
    # ------------------------------------------------------------------
    project = client.post(
        "/api/v1/projects",
        json={
            "name": "AI IDE",
            "description": "End-to-End Test",
            "repository_url": "https://github.com/example/repository.git",
            "language": "Python",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ------------------------------------------------------------------
    # Import Repository
    # ------------------------------------------------------------------
    repo = client.post(
        "/api/v1/projects/import",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert repo.status_code in (
        200,
        201,
        202,
    )

    # ------------------------------------------------------------------
    # Create Workspace
    # ------------------------------------------------------------------
    workspace = client.post(
        "/api/v1/workspaces",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert workspace.status_code == 201

    workspace_id = workspace.json()["id"]

    # ------------------------------------------------------------------
    # Repository Indexing
    # ------------------------------------------------------------------
    index = client.post(
        "/api/v1/projects/index",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert index.status_code in (
        200,
        202,
    )

    # ------------------------------------------------------------------
    # Generate Embeddings
    # ------------------------------------------------------------------
    embed = client.post(
        "/api/v1/rag/embed",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert embed.status_code in (
        200,
        202,
    )

    # ------------------------------------------------------------------
    # Create Chat
    # ------------------------------------------------------------------
    chat = client.post(
        "/api/v1/chat",
        json={
            "project_id": project_id,
            "title": "Assistant",
        },
        headers=headers,
    )

    assert chat.status_code == 201

    chat_id = chat.json()["id"]

    # ------------------------------------------------------------------
    # Chat Message
    # ------------------------------------------------------------------
    message = client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": chat_id,
            "message": "Create JWT authentication.",
        },
        headers=headers,
    )

    assert message.status_code == 200

    # ------------------------------------------------------------------
    # Planner
    # ------------------------------------------------------------------
    planner = client.post(
        "/api/v1/agents/plan",
        json={
            "task": "Implement authentication",
        },
        headers=headers,
    )

    assert planner.status_code == 200

    # ------------------------------------------------------------------
    # Execute Agent
    # ------------------------------------------------------------------
    execution = client.post(
        "/api/v1/agents/execute",
        json={
            "goal": "Implement authentication module",
        },
        headers=headers,
    )

    assert execution.status_code in (
        200,
        202,
    )

    # ------------------------------------------------------------------
    # Execute Tool
    # ------------------------------------------------------------------
    tool = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "write_file",
            "arguments": {
                "path": "app/auth.py",
                "content": "# authentication",
            },
        },
        headers=headers,
    )

    assert tool.status_code in (
        200,
        202,
    )

    # ------------------------------------------------------------------
    # Read File
    # ------------------------------------------------------------------
    read = client.get(
        f"/api/v1/workspaces/{workspace_id}/files/app/auth.py",
        headers=headers,
    )

    assert read.status_code == 200

    # ------------------------------------------------------------------
    # Git Commit
    # ------------------------------------------------------------------
    commit = client.post(
        f"/api/v1/workspaces/{workspace_id}/git/commit",
        json={
            "message": "Generated authentication module",
        },
        headers=headers,
    )

    assert commit.status_code in (
        200,
        201,
    )

    # ------------------------------------------------------------------
    # Git Push
    # ------------------------------------------------------------------
    push = client.post(
        f"/api/v1/workspaces/{workspace_id}/git/push",
        headers=headers,
    )

    assert push.status_code in (
        200,
        202,
    )

    # ------------------------------------------------------------------
    # Save Memory
    # ------------------------------------------------------------------
    memory = client.post(
        "/api/v1/memories",
        json={
            "project_id": project_id,
            "title": "Authentication",
            "content": "JWT authentication generated.",
        },
        headers=headers,
    )

    assert memory.status_code == 201

    # ------------------------------------------------------------------
    # Semantic Search
    # ------------------------------------------------------------------
    search = client.post(
        "/api/v1/memories/search",
        json={
            "query": "JWT",
        },
        headers=headers,
    )

    assert search.status_code == 200

    # ------------------------------------------------------------------
    # Token Usage
    # ------------------------------------------------------------------
    usage = client.get(
        "/api/v1/chat/usage",
        headers=headers,
    )

    assert usage.status_code == 200

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------
    delete = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )

    assert delete.status_code in (
        200,
        204,
    )