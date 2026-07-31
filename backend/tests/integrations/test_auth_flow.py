import pytest

from fastapi.testclient import TestClient
def test_register_login_flow(
    client: TestClient,
):

    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
            "full_name": "Integration User",
        },
    )

    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
def test_refresh_token(
    client,
):

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
        },
    )

    refresh = login.json()["refresh_token"]

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
def test_logout(
    client,
):

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
        },
    )

    token = login.json()["access_token"]

    response = client.post(
        "/api/v1/auth/logout",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
def test_access_after_logout(
    client,
):

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401
def test_duplicate_registration(
    client,
):

    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "Duplicate User",
    }

    first = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    second = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first.status_code == 201
    assert second.status_code == 409
def test_invalid_password(
    client,
):

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
def test_invalid_refresh_token(
    client,
):

    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid-token",
        },
    )

    assert response.status_code == 401
def test_expired_token(
    client,
):

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer expired-token",
        },
    )

    assert response.status_code == 401
def test_profile_endpoint(
    client,
):

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
        },
    )

    token = login.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["email"] == "integration@example.com"
def test_refresh_token_rotation(
    client,
):

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "Password123!",
        },
    )

    refresh = login.json()["refresh_token"]

    rotated = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh,
        },
    )

    assert rotated.status_code == 200

    new_refresh = rotated.json()["refresh_token"]

    assert new_refresh != refresh