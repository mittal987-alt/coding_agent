import pytest

from fastapi.testclient import TestClient


def test_complete_rag_pipeline(
    client: TestClient,
):
    # ---------------------------------------------------------
    # Register User
    # ---------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "rag@example.com",
            "password": "Password123!",
            "full_name": "RAG User",
        },
    )

    assert register.status_code == 201

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "rag@example.com",
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
            "name": "RAG Pipeline",
            "repository_url": "https://github.com/example/rag.git",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ---------------------------------------------------------
    # Upload Documents
    # ---------------------------------------------------------
    upload = client.post(
        "/api/v1/rag/documents",
        json={
            "project_id": project_id,
            "documents": [
                {
                    "name": "architecture.md",
                    "content": "# System Architecture",
                },
                {
                    "name": "api.md",
                    "content": "# API Documentation",
                },
            ],
        },
        headers=headers,
    )

    assert upload.status_code == 201

    # ---------------------------------------------------------
    # Chunk Documents
    # ---------------------------------------------------------
    chunk = client.post(
        "/api/v1/rag/chunk",
        json={
            "project_id": project_id,
            "chunk_size": 512,
            "chunk_overlap": 64,
        },
        headers=headers,
    )

    assert chunk.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Generate Embeddings
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Build Vector Index
    # ---------------------------------------------------------
    index = client.post(
        "/api/v1/rag/index",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert index.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Semantic Search
    # ---------------------------------------------------------
    search = client.post(
        "/api/v1/rag/search",
        json={
            "query": "Explain system architecture",
            "top_k": 5,
        },
        headers=headers,
    )

    assert search.status_code == 200

    results = search.json()["results"]

    assert len(results) > 0

    # ---------------------------------------------------------
    # Rerank Results
    # ---------------------------------------------------------
    rerank = client.post(
        "/api/v1/rag/rerank",
        json={
            "query": "Explain system architecture",
            "documents": results,
        },
        headers=headers,
    )

    assert rerank.status_code == 200

    # ---------------------------------------------------------
    # Build Context
    # ---------------------------------------------------------
    context = client.post(
        "/api/v1/rag/context",
        json={
            "query": "Explain system architecture",
        },
        headers=headers,
    )

    assert context.status_code == 200

    body = context.json()

    assert "context" in body

    # ---------------------------------------------------------
    # Generate AI Response
    # ---------------------------------------------------------
    answer = client.post(
        "/api/v1/rag/answer",
        json={
            "query": "Explain system architecture",
        },
        headers=headers,
    )

    assert answer.status_code == 200

    response = answer.json()

    assert "answer" in response

    # ---------------------------------------------------------
    # Verify Citations
    # ---------------------------------------------------------
    citations = client.get(
        "/api/v1/rag/citations",
        headers=headers,
    )

    assert citations.status_code == 200

    # ---------------------------------------------------------
    # Incremental Re-index
    # ---------------------------------------------------------
    incremental = client.post(
        "/api/v1/rag/reindex",
        json={
            "project_id": project_id,
            "incremental": True,
        },
        headers=headers,
    )

    assert incremental.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Save Retrieved Knowledge
    # ---------------------------------------------------------
    memory = client.post(
        "/api/v1/memories",
        json={
            "project_id": project_id,
            "title": "Architecture",
            "content": response["answer"],
        },
        headers=headers,
    )

    assert memory.status_code == 201

    # ---------------------------------------------------------
    # Pipeline Metrics
    # ---------------------------------------------------------
    metrics = client.get(
        "/api/v1/rag/stats",
        headers=headers,
    )

    assert metrics.status_code == 200

    stats = metrics.json()

    assert "documents" in stats
    assert "chunks" in stats
    assert "embeddings" in stats
    assert "index_size" in stats

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