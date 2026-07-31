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
            "title": "AI Assistant",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == "AI Assistant"
def test_get_chat(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/chat",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
def test_send_message(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "Explain this repository.",
            "chat_id": "test-chat",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_streaming_chat(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Hello",
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
        "/api/v1/chat/history",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
def test_delete_chat(
    client,
    auth_headers,
):

    response = client.delete(
        "/api/v1/chat/test-chat",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )
def test_rag_context(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/context",
        json={
            "query": "authentication flow",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_tool_execution(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/tools",
        json={
            "tool": "search_files",
            "query": "main.py",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_model_selection(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/model",
        json={
            "model": "gpt-5.5",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_token_usage(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/chat/usage",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_tokens" in body
def test_chat_requires_auth(
    client,
):

    response = client.get(
        "/api/v1/chat"
    )

    assert response.status_code == 401
def test_chat_not_found(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/chat/invalid-chat-id",
        headers=auth_headers,
    )

    assert response.status_code == 404
def test_empty_message(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/chat/message",
        json={
            "message": "",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422