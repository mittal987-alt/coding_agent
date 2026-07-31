import time

import pytest
from fastapi.testclient import TestClient


def authenticate(client: TestClient):
    email = f"backup-{time.time_ns()}@example.com"

    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Backup User",
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


def test_create_full_backup(
    client: TestClient,
):
    headers = authenticate(client)

    response = client.post(
        "/api/v1/backups/full",
        headers=headers,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )

    body = response.json()

    assert "backup_id" in body


def test_create_incremental_backup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/incremental",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_schedule_backup(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/schedule",
        json={
            "frequency": "daily",
            "retention_days": 30,
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
    )


def test_list_backups(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_backup_metadata(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups/backup-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "created_at" in body
    assert "size_bytes" in body
    assert "type" in body


def test_backup_integrity(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/backup-1/verify",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["valid"] is True


def test_backup_encryption(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups/backup-1/encryption",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["encrypted"] is True


def test_restore_entire_system(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/backup-1/restore",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_restore_single_project(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/backup-1/restore/project",
        json={
            "project_id": "project-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_restore_workspace(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/backup-1/restore/workspace",
        json={
            "workspace_id": "workspace-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_retention_policy(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups/retention",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "retention_days" in body


def test_cleanup_expired_backups(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/backups/cleanup",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_backup_catalog(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups/catalog",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_backups" in body
    assert "latest_backup" in body


def test_delete_backup(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/backups/backup-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_backup_report(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/backups/report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "summary" in body
    assert "storage_usage" in body
    assert "recommendations" in body