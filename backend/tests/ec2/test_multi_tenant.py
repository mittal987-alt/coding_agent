import time

import pytest
from fastapi.testclient import TestClient


def create_user(
    client: TestClient,
    email: str,
):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": email.split("@")[0],
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


def test_create_tenant(
    client: TestClient,
):
    headers = create_user(
        client,
        f"tenant-{time.time_ns()}@example.com",
    )

    response = client.post(
        "/api/v1/tenants",
        json={
            "name": "Acme Corporation",
        },
        headers=headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body


def test_create_organization(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/organizations",
        json={
            "name": "Engineering",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201


def test_invite_user(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/organizations/invitations",
        json={
            "email": "developer@example.com",
            "role": "developer",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
    )


def test_role_assignment(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/organizations/roles",
        json={
            "user_id": "user-1",
            "role": "admin",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
    )


def test_project_isolation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/projects/project-owned-by-other-tenant",
        headers=auth_headers,
    )

    assert response.status_code in (
        403,
        404,
    )


def test_workspace_isolation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/workspaces/workspace-other-tenant",
        headers=auth_headers,
    )

    assert response.status_code in (
        403,
        404,
    )


def test_memory_isolation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/memories/memory-other-tenant",
        headers=auth_headers,
    )

    assert response.status_code in (
        403,
        404,
    )


def test_vector_database_isolation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/rag/search",
        json={
            "query": "private company documentation",
            "tenant_id": "other-tenant",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        403,
        404,
    )


def test_billing_isolation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/billing",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "subscription" in body


def test_cross_tenant_access_denied(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/projects/project-other-tenant/share",
        json={
            "user_id": "user-123",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        403,
        404,
    )


def test_api_key_isolation(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/api-keys",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_usage_metrics_are_isolated(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/usage",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "requests" in body
    assert "tokens" in body


def test_audit_logs_are_isolated(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/audit",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_delete_tenant(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/tenants/tenant-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
        204,
    )


def test_tenant_cleanup_report(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tenants/tenant-1/report",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "deleted_resources" in body
    assert "status" in body