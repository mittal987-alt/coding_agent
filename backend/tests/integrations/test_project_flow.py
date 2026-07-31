import pytest

from fastapi.testclient import TestClient

def test_create_project(
    client: TestClient,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects",
        json={
            "name": "AI IDE",
            "description": "Integration Test",
            "repository_url": "https://github.com/example/repo.git",
            "language": "Python",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "AI IDE"

    return body["id"]

    def test_get_project(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(response.json(), list)
    def test_import_repository(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/import",
        json={
            "repository_url": "https://github.com/example/repo.git",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )
    def test_workspace_initialization(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/workspace",
        json={
            "project_id": "project-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    def test_repository_indexing(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/index",
        json={
            "project_id": "project-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    def test_rag_indexing(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/rag",
        json={
            "project_id": "project-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    def test_git_sync(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/project-1/sync",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
    def test_update_project(
    client,
    auth_headers,
):

    response = client.put(
        "/api/v1/projects/project-1",
        json={
            "description": "Updated Description",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    def test_archive_project(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/project-1/archive",
        headers=auth_headers,
    )

    assert response.status_code == 200
    def test_restore_project(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/project-1/restore",
        headers=auth_headers,
    )

    assert response.status_code == 200  

    def test_delete_project(
    client,
    auth_headers,
):

    response = client.delete(
        "/api/v1/projects/project-1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        204,
    )

    def test_project_removed(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects/project-1",
        headers=auth_headers,
    )

    assert response.status_code == 404