import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"dr-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Disaster Recovery User",
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

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


def test_full_system_backup(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.post(
        "/api/v1/system/backup",
        headers=headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    body = response.json()

    assert "backup_id" in body


def test_database_backup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/database/backup",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_object_storage_backup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/storage/backup",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_vector_database_backup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/vector/backup",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_workspace_snapshot_restore(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/restore",
        json={
            "snapshot": "snapshot-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_database_point_in_time_restore(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/database/restore",
        json={
            "timestamp": "2026-01-01T00:00:00Z",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_vector_restore(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/vector/restore",
        json={
            "backup_id": "vector-backup-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_object_storage_restore(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/storage/restore",
        json={
            "backup_id": "storage-backup-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_cross_region_failover(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/regions/failover",
        json={
            "target_region": "secondary",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_service_recovery(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/system/recovery/start",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_rto_validation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/recovery/rto",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "actual_rto_seconds" in body
    assert "target_rto_seconds" in body


def test_rpo_validation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/recovery/rpo",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "actual_rpo_seconds" in body
    assert "target_rpo_seconds" in body


def test_system_health_after_recovery(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/health",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


def test_disaster_recovery_report(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/system/disaster-recovery-report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "backup_status" in body
    assert "recovery_status" in body
    assert "recommendations" in body