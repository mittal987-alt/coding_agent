import pytest

from fastapi.testclient import TestClient


def test_create_chat(
    client: TestClient,
    auth_headers,
    test_project,
):
    response = client.post(
        "/api/v1/chat",
        json={
            "project_id": str(test_project.id),
            "title": "Integration Chat",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "Integration Chat"


def test_send_message(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": "chat-1",
            "message": "Explain authentication architecture.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "response" in body


def test_multi_turn_conversation(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": "chat-1",
            "message": "What is JWT?",
        },
        headers=auth_headers,
    )

    response = client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": "chat-1",
            "message": "How does refresh token work?",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "response" in body


def test_rag_retrieval(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/context",
        json={
            "query": "JWT authentication",
            "chat_id": "chat-1",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body


def test_tool_invocation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/tools",
        json={
            "tool": "search_files",
            "query": "auth.py",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_model_routing(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/model",
        json={
            "task": "code_generation",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "selected_model" in body


def test_streaming_response(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": "chat-1",
            "message": "Generate a FastAPI CRUD application.",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_chat_history(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chat/history/chat-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert isinstance(history, list)


def test_memory_update(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/memory",
        json={
            "chat_id": "chat-1",
            "summary": "Authentication module completed.",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
    )


def test_token_usage(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chat/usage/chat-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "prompt_tokens" in body
    assert "completion_tokens" in body
    assert "total_tokens" in body


def test_delete_chat(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/chat/chat-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_chat_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chat/invalid-chat",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_chat_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/chat"
    )

    assert response.status_code == 401


def test_invalid_chat_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/message",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_chat_context_persistence(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": "chat-1",
            "message": "My project uses PostgreSQL.",
        },
        headers=auth_headers,
    )

    response = client.post(
        "/api/v1/chat/message",
        json={
            "chat_id": "chat-1",
            "message": "Which database am I using?",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "response" in body