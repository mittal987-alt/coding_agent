import pytest

from fastapi.testclient import TestClient


def test_large_repository_workflow(
    client: TestClient,
):
    # ---------------------------------------------------------
    # Register
    # ---------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "large@example.com",
            "password": "Password123!",
            "full_name": "Large Repository User",
        },
    )

    assert register.status_code == 201

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "large@example.com",
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
            "name": "Linux Kernel",
            "description": "Large repository benchmark",
            "repository_url": "https://github.com/torvalds/linux.git",
            "language": "C",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ---------------------------------------------------------
    # Clone Repository
    # ---------------------------------------------------------
    clone = client.post(
        "/api/v1/projects/import",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert clone.status_code in (
        200,
        201,
        202,
    )

    # ---------------------------------------------------------
    # Repository Statistics
    # ---------------------------------------------------------
    stats = client.get(
        f"/api/v1/projects/{project_id}/stats",
        headers=headers,
    )

    assert stats.status_code == 200

    body = stats.json()

    assert "total_files" in body

    # ---------------------------------------------------------
    # Parallel Indexing
    # ---------------------------------------------------------
    indexing = client.post(
        "/api/v1/projects/index",
        json={
            "project_id": project_id,
            "parallel": True,
        },
        headers=headers,
    )

    assert indexing.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Generate Embeddings
    # ---------------------------------------------------------
    embeddings = client.post(
        "/api/v1/rag/embed",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert embeddings.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Vector Database Statistics
    # ---------------------------------------------------------
    vectors = client.get(
        "/api/v1/rag/stats",
        headers=headers,
    )

    assert vectors.status_code == 200

    assert "embeddings" in vectors.json()

    # ---------------------------------------------------------
    # Semantic Search
    # ---------------------------------------------------------
    search = client.post(
        "/api/v1/rag/search",
        json={
            "query": "How is process scheduling implemented?",
            "top_k": 10,
        },
        headers=headers,
    )

    assert search.status_code == 200

    results = search.json()["results"]

    assert len(results) > 0

    # ---------------------------------------------------------
    # AI Chat
    # ---------------------------------------------------------
    chat = client.post(
        "/api/v1/chat",
        json={
            "project_id": project_id,
            "title": "Kernel Assistant",
        },
        headers=headers,
    )

    assert chat.status_code == 201

    chat_id = chat.json()["id"]

    # ---------------------------------------------------------
    # Code Explanation
    # ---------------------------------------------------------
    answer = client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": chat_id,
            "message": "Explain the Linux scheduler.",
        },
        headers=headers,
    )

    assert answer.status_code == 200

    assert "response" in answer.json()

    # ---------------------------------------------------------
    # Memory Creation
    # ---------------------------------------------------------
    memory = client.post(
        "/api/v1/memories",
        json={
            "project_id": project_id,
            "title": "Scheduler",
            "content": "Scheduler explanation stored.",
        },
        headers=headers,
    )

    assert memory.status_code == 201

    # ---------------------------------------------------------
    # Synchronize Repository
    # ---------------------------------------------------------
    sync = client.post(
        f"/api/v1/projects/{project_id}/sync",
        headers=headers,
    )

    assert sync.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Performance Metrics
    # ---------------------------------------------------------
    metrics = client.get(
        f"/api/v1/projects/{project_id}/metrics",
        headers=headers,
    )

    assert metrics.status_code == 200

    body = metrics.json()

    assert "indexing_time" in body
    assert "embedding_time" in body
    assert "search_latency" in body

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