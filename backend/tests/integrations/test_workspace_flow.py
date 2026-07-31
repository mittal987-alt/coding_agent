import pytest

from fastapi.testclient import TestClient


def test_create_workspace(
    client: TestClient,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces",
        json={
            "project_id": "project-1",
            "name": "Development Workspace",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert "id" in body


def test_clone_repository(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/clone",
        json={
            "repository_url": "https://github.com/example/repository.git",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_list_files(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/workspaces/workspace-1/files",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_read_file(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/workspaces/workspace-1/files/main.py",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "content" in body


def test_write_file(
    client,
    auth_headers,
):
    response = client.put(
        "/api/v1/workspaces/workspace-1/files/main.py",
        json={
            "content": "print('Hello World')",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_create_file(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/files",
        json={
            "path": "app/example.py",
            "content": "# Example",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201


def test_delete_file(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/workspaces/workspace-1/files/app/example.py",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_execute_terminal_command(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/terminal",
        json={
            "command": "python --version",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    body = response.json()

    assert "output" in body


def test_git_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/workspaces/workspace-1/git/status",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_git_commit(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/git/commit",
        json={
            "message": "Initial commit",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
    )


def test_git_push(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/git/push",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_create_snapshot(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/snapshots",
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert "snapshot_id" in body


def test_restore_snapshot(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/snapshots/snapshot-1/restore",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_cleanup_workspace(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces/workspace-1/cleanup",
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_delete_workspace(
    client,
    auth_headers,
):
    response = client.delete(
        "/api/v1/workspaces/workspace-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )


def test_workspace_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/workspaces/invalid-workspace",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/workspaces",
    )

    assert response.status_code == 401


def test_invalid_workspace_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/workspaces",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422