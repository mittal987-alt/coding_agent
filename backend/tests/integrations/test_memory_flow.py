import pytest

from fastapi.testclient import TestClient


def test_create_memory(
    client: TestClient,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories",
        json={
            "title": "JWT Authentication",
            "content": "JWT uses access tokens and refresh tokens.",
            "project_id": "project-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body


def test_get_memory(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/memories/memory-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "content" in body


def test_generate_embedding(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/memory-1/embed",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_semantic_search(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/search",
        json={
            "query": "JWT Authentication",
            "top_k": 5,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body["results"],
        list,
    )


def test_similarity_search(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/similarity",
        json={
            "memory_id": "memory-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_context_retrieval(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/context",
        json={
            "query": "Explain JWT authentication",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body


def test_update_memory(
    client,
    auth_headers,
):
    response = client.put(
        "/api/v1/memories/memory-1",
        json={
            "content": "Updated JWT authentication documentation.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_pin_memory(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/memory-1/pin",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_add_tags(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/memory-1/tags",
        json={
            "tags": [
                "security",
                "jwt",
                "authentication",
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_archive_memory(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/memory-1/archive",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_restore_memory(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories/memory-1/restore",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_memory_statistics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/memories/stats",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_memories" in body
    assert "embedded_memories" in body


def test_delete_memory(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/memories/memory-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_memory_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/memories/invalid-memory",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/memories",
    )

    assert response.status_code == 401


def test_invalid_memory_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/memories",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422