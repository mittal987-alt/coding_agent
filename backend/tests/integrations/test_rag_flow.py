import pytest

from fastapi.testclient import TestClient


def test_upload_document(
    client: TestClient,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/documents",
        json={
            "title": "FastAPI Guide",
            "content": "FastAPI is a modern Python web framework.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body


def test_chunk_document(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/chunk",
        json={
            "document_id": "doc-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_generate_embeddings(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/embed",
        json={
            "document_id": "doc-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_vector_store(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/index",
        json={
            "document_id": "doc-1",
        },
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
        "/api/v1/rag/search",
        json={
            "query": "What is FastAPI?",
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
        "/api/v1/rag/similarity",
        json={
            "document_id": "doc-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_reranking(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/rerank",
        json={
            "query": "Explain FastAPI",
            "top_k": 5,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "results" in response.json()


def test_context_generation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/context",
        json={
            "query": "Explain dependency injection",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "context" in body


def test_generate_answer(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/answer",
        json={
            "query": "What is FastAPI?",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body


def test_delete_document(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/rag/documents/doc-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_document_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/rag/documents/invalid-id",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/rag/documents",
    )

    assert response.status_code == 401


def test_invalid_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/search",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_embedding_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/rag/embeddings/doc-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "embedding_status" in body


def test_index_statistics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/rag/stats",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body
    assert "embeddings" in body