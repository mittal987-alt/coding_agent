
import pytest
from fastapi.testclient import TestClient

def test_list_projects(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)

    assert "projects" in data

    assert isinstance(data["projects"], list)

def test_create_project(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json={
            "name": "Test Project",
            "slug": "test-project",
            "description": "Test Description",
        },
    )

    assert response.status_code in (
        200,
        201,
    )

    assert "id" in response.json()
@pytest.mark.parametrize(
    "invalid_payload",
    [
        {
            "name": "",
        },
        {
            "name": "Test",
            "slug": "",
        },
    ],
)
def test_create_project_validation(
    client,
    auth_headers,
    invalid_payload,
):

    response = client.post(
        "/api/v1/projects",
        headers=auth_headers,
        json=invalid_payload,
    )

    assert response.status_code == 422

def test_get_project(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects/1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        404,
    )

def test_update_project(
    client,
    auth_headers,
):

    response = client.put(
        "/api/v1/projects/1",
        headers=auth_headers,
        json={
            "name": "Updated Test Project",
        },
    )

    assert response.status_code in (
        200,
        404,
    )

def test_delete_project(
    client,
    auth_headers,
):

    response = client.delete(
        "/api/v1/projects/1",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        404,
    )

def test_project_without_token(
    client,
):

    response = client.get(
        "/api/v1/projects",
    )

    assert response.status_code == 401

def test_project_with_invalid_token(
    client,
):

    response = client.get(
        "/api/v1/projects",
        headers={
            "Authorization":
            "Bearer invalid-token"
        },
    )

    assert response.status_code == 401

def test_project_with_expired_token(
    client,
):

    response = client.get(
        "/api/v1/projects",
        headers={
            "Authorization":
            "Bearer expired-token"
        },
    )

    assert response.status_code == 401

def test_project_owner_relationship(
    session,
):

    from app.models import User, Project

    user = User(
        email="owner@example.com",
        username="owner",
        password_hash="hash",
        full_name="Owner User",
    )

    session.add(user)

    project = Project(
        name="Test Project",
        slug="test-project",
        owner=user,
    )

    session.add(project)

    session.commit()

    queried = session.get(
        Project,
        project.id,
    )

    assert queried.owner.username == "owner"

def test_project_cascade_delete(
    session,
):

    from app.models import User, Project, Workspace

    user = User(
        email="user@example.com",
        username="user",
        password_hash="hash",
        full_name="User",
    )

    session.add(user)

    project = Project(
        name="Test Project",
        slug="test-project",
        owner=user,
    )

    session.add(project)

    workspace = Workspace(
        name="Test Workspace",
        slug="test-workspace",
        project=project,
    )

    session.add(workspace)

    session.commit()

    project_id = project.id

    session.delete(project)

    session.commit()

    assert session.get(
        Project,
        project_id,
    ) is None

    assert session.get(
        Workspace,
        workspace.id,
    ) is None

def test_list_projects_no_auth(
    client,
):
    """
    Ensure listing projects fails without authentication.
    """

    response = client.get(
        "/api/v1/projects",
    )

    assert response.status_code == 401
def test_create_project(
    client: TestClient,
    auth_headers,
):

    payload = {
        "name": "AI Assistant",
        "description": "Autonomous AI Engineer",
        "repository_url": "https://github.com/example/project",
        "language": "Python",
        "framework": "FastAPI",
    }

    response = client.post(
        "/api/v1/projects",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == payload["name"]
def test_get_project(
    client,
    test_project,
    auth_headers,
):

    response = client.get(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert response.json()["id"] == str(test_project.id)
def test_update_project(
    client,
    test_project,
    auth_headers,
):

    response = client.put(
        f"/api/v1/projects/{test_project.id}",
        json={
            "name": "Updated Project"
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert (
        response.json()["name"]
        == "Updated Project"
    )
def test_delete_project(
    client,
    test_project,
    auth_headers,
):

    response = client.delete(
        f"/api/v1/projects/{test_project.id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
def test_list_projects(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
def test_project_pagination(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects?page=1&page_size=10",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_search_projects(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects?search=AI",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_filter_language(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects?language=Python",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_import_repository(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects/import",
        json={
            "repository_url":
            "https://github.com/example/repo"
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )
def test_git_sync(
    client,
    test_project,
    auth_headers,
):

    response = client.post(
        f"/api/v1/projects/{test_project.id}/sync",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_archive_project(
    client,
    test_project,
    auth_headers,
):

    response = client.post(
        f"/api/v1/projects/{test_project.id}/archive",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_restore_project(
    client,
    test_project,
    auth_headers,
):

    response = client.post(
        f"/api/v1/projects/{test_project.id}/restore",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_project_without_auth(
    client,
):

    response = client.get(
        "/api/v1/projects"
    )

    assert response.status_code == 401
def test_project_not_found(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
def test_invalid_project(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/projects",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422