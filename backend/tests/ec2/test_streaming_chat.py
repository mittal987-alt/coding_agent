import threading
import time

import pytest
from fastapi.testclient import TestClient


def test_streaming_chat_response(
    client: TestClient,
):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "stream@example.com",
            "password": "Password123!",
            "full_name": "Streaming User",
        },
    )

    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "stream@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    project = client.post(
        "/api/v1/projects",
        json={
            "name": "Streaming Project",
            "repository_url": "https://github.com/example/project.git",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    chat = client.post(
        "/api/v1/chat",
        json={
            "project_id": project_id,
            "title": "Streaming Chat",
        },
        headers=headers,
    )

    assert chat.status_code == 201

    chat_id = chat.json()["id"]

    response = client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": chat_id,
            "message": "Generate a FastAPI CRUD API.",
        },
        headers=headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_streaming_chunks(
    client: TestClient,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": "chat-1",
            "message": "Explain JWT authentication.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.text

    assert len(body) > 0


def test_stream_cancellation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/cancel",
        json={
            "chat_id": "chat-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_stream_reconnect(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/reconnect",
        json={
            "chat_id": "chat-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_multi_turn_streaming(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": "chat-1",
            "message": "What is FastAPI?",
        },
        headers=auth_headers,
    )

    response = client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": "chat-1",
            "message": "Create authentication using JWT.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_parallel_streaming_clients(
    client,
    auth_headers,
):
    responses = []

    def worker():
        r = client.post(
            "/api/v1/chat/stream",
            json={
                "chat_id": "chat-1",
                "message": "Hello AI",
            },
            headers=auth_headers,
        )
        responses.append(r.status_code)

    threads = [
        threading.Thread(target=worker)
        for _ in range(5)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    assert all(
        status in (200, 202)
        for status in responses
    )


def test_streaming_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chat/stream/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "active_streams" in body
    assert "completed_streams" in body


def test_stream_timeout(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "chat_id": "chat-1",
            "message": "Generate an entire operating system.",
            "timeout": 1,
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        408,
        504,
    )


def test_stream_history(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/chat/history/chat-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    history = response.json()

    assert isinstance(
        history,
        list,
    )


def test_stream_requires_authentication(
    client,
):
    response = client.post(
        "/api/v1/chat/stream",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code == 401


def test_invalid_stream_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/stream",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_stream_cleanup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/chat/stream/cleanup",
        json={
            "chat_id": "chat-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )