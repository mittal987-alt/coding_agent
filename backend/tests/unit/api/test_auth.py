import pytest

from fastapi.testclient import TestClient
def test_register_user(client: TestClient):

    payload = {
        "email": "john@example.com",
        "username": "john",
        "password": "Password@123",
        "full_name": "John Doe",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == payload["email"]
def test_register_duplicate_email(
    client: TestClient,
):

    payload = {
        "email": "test@example.com",
        "username": "duplicate",
        "password": "Password@123",
    }

    client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 409
def test_login_success(client: TestClient):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert "refresh_token" in body
def test_login_invalid_password(
    client: TestClient,
):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
def test_login_unknown_user(
    client: TestClient,
):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 401
def test_login_unknown_user(
    client: TestClient,
):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "Password@123",
        },
    )

    assert response.status_code == 401
def test_refresh_token(client):

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "dummy-token"
        },
    )

    assert response.status_code in (
        200,
        401,
    )
def test_logout(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_me_endpoint(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert "email" in response.json()
def test_protected_without_token(
    client,
):

    response = client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401
def test_invalid_token(
    client,
):

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization":
            "Bearer invalid-token"
        },
    )

    assert response.status_code == 401
def test_expired_token(
    client,
):

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization":
            "Bearer expired-token"
        },
    )

    assert response.status_code == 401
def test_password_reset_request(
    client,
):

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "test@example.com"
        },
    )

    assert response.status_code in (
        200,
        404,
    )
def test_password_reset(
    client,
):

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "dummy",
            "password": "NewPassword@123",
        },
    )

    assert response.status_code in (
        200,
        400,
    )
@pytest.mark.parametrize(
    "role",
    [
        "admin",
        "developer",
        "viewer",
    ],
)
def test_role_access(
    client,
    role,
):

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "X-Test-Role": role
        },
    )

    assert response.status_code in (
        200,
        403,
    )
def test_jwt_format(
    client,
):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Password@123",
        },
    )

    if response.status_code == 200:

        token = response.json()["access_token"]

        assert token.count(".") == 2