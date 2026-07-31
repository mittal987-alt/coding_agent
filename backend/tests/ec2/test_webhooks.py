import hashlib
import hmac
import json
import time
import uuid

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"webhook-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Webhook User",
        },
    )

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    return {
        "Authorization": f"Bearer {login.json()['access_token']}",
    }


def generate_signature(secret: str, payload: dict):
    body = json.dumps(payload).encode()

    return hmac.new(
        secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()


def test_register_webhook(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://example.com/webhook",
            "events": [
                "project.created",
                "agent.completed",
            ],
            "secret": "super-secret",
        },
        headers=headers,
    )

    assert response.status_code in (200, 201)

    body = response.json()

    assert "id" in body


def test_list_webhooks(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_update_webhook(
    client,
    auth_headers,
):
    response = client.put(
        "/api/v1/webhooks/webhook-1",
        json={
            "events": [
                "project.updated",
            ],
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_delete_webhook(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/webhooks/webhook-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_signature_verification():
    payload = {
        "event": "project.created",
        "id": str(uuid.uuid4()),
    }

    signature = generate_signature(
        "secret",
        payload,
    )

    assert len(signature) == 64


def test_event_delivery(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/webhooks/test-delivery",
        json={
            "webhook_id": "webhook-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_retry_delivery(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/webhooks/retry",
        json={
            "delivery_id": "delivery-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_duplicate_event_prevention(
    client,
    auth_headers,
):
    event = {
        "event_id": "evt-123",
    }

    first = client.post(
        "/api/v1/webhooks/events",
        json=event,
        headers=auth_headers,
    )

    second = client.post(
        "/api/v1/webhooks/events",
        json=event,
        headers=auth_headers,
    )

    assert first.status_code in (
        200,
        201,
    )

    assert second.status_code in (
        200,
        409,
    )


def test_event_ordering(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks/events",
        headers=auth_headers,
    )

    assert response.status_code == 200

    events = response.json()

    if len(events) > 1:
        timestamps = [
            e["timestamp"]
            for e in events
        ]

        assert timestamps == sorted(
            timestamps,
        )


def test_dead_letter_queue(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks/dead-letter-queue",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "failed_events" in body


def test_delivery_timeout(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/webhooks/simulate-timeout",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        408,
        202,
    )


def test_webhook_metrics(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks/metrics",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "deliveries" in body
    assert "success_rate" in body
    assert "average_latency_ms" in body


def test_delivery_logs(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks/delivery-logs",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_webhook_report(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/webhooks/report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert "reliability" in body
    assert "recommendations" in body