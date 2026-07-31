import pytest

from fastapi.testclient import TestClient
def test_create_memory(
    client: TestClient,
    auth_headers,
    test_project,
):

    response = client.post(
        "/api/v1/memories",
        json={
            "project_id": str(test_project.id),
            "title": "Authentication Design",
            "content": "JWT authentication uses access and refresh tokens.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "Authentication Design"
def test_get_memory(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/memories/memory-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "content" in response.json()
def test_list_memories(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/memories",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
def test_update_memory(
    client,
    auth_headers,
):

    response = client.put(
        "/api/v1/memories/memory-1",
        json={
            "title": "Updated Memory",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
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
def test_semantic_search(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/memories/search",
        json={
            "query": "JWT authentication",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
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
def test_generate_embedding(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/memories/embed",
        json={
            "memory_id": "memory-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_pin_memory(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/memories/memory-1/pin",
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
def test_tag_memory(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/memories/memory-1/tags",
        json={
            "tags": [
                "authentication",
                "security",
            ],
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
            "query": "Explain JWT",
            "limit": 5,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body
def test_memory_requires_auth(
    client,
):

    response = client.get(
        "/api/v1/memories"
    )

    assert response.status_code == 401
def test_memory_not_found(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/memories/invalid-id",
        headers=auth_headers,
    )

    assert response.status_code == 404  
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