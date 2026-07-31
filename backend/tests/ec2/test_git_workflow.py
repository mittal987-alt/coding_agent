import pytest

from fastapi.testclient import TestClient


def test_complete_git_workflow(
    client: TestClient,
):
    # ---------------------------------------------------------
    # Register User
    # ---------------------------------------------------------
    register = client.post(
        "/api/v1/auth/register",
        json={
            "email": "git@example.com",
            "password": "Password123!",
            "full_name": "Git User",
        },
    )

    assert register.status_code == 201

    # ---------------------------------------------------------
    # Login
    # ---------------------------------------------------------
    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "git@example.com",
            "password": "Password123!",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

    # ---------------------------------------------------------
    # Create Project
    # ---------------------------------------------------------
    project = client.post(
        "/api/v1/projects",
        json={
            "name": "Git Workflow",
            "repository_url": "https://github.com/example/project.git",
        },
        headers=headers,
    )

    assert project.status_code == 201

    project_id = project.json()["id"]

    # ---------------------------------------------------------
    # Clone Repository
    # ---------------------------------------------------------
    clone = client.post(
        "/api/v1/projects/import",
        json={
            "project_id": project_id,
        },
        headers=headers,
    )

    assert clone.status_code in (
        200,
        201,
        202,
    )

    # ---------------------------------------------------------
    # Create Branch
    # ---------------------------------------------------------
    branch = client.post(
        f"/api/v1/projects/{project_id}/git/branches",
        json={
            "name": "feature/authentication",
        },
        headers=headers,
    )

    assert branch.status_code == 201

    # ---------------------------------------------------------
    # Checkout Branch
    # ---------------------------------------------------------
    checkout = client.post(
        f"/api/v1/projects/{project_id}/git/checkout",
        json={
            "branch": "feature/authentication",
        },
        headers=headers,
    )

    assert checkout.status_code == 200

    # ---------------------------------------------------------
    # Git Status
    # ---------------------------------------------------------
    status = client.get(
        f"/api/v1/projects/{project_id}/git/status",
        headers=headers,
    )

    assert status.status_code == 200

    assert "branch" in status.json()

    # ---------------------------------------------------------
    # Commit Changes
    # ---------------------------------------------------------
    commit = client.post(
        f"/api/v1/projects/{project_id}/git/commit",
        json={
            "message": "Implement JWT authentication",
        },
        headers=headers,
    )

    assert commit.status_code in (
        200,
        201,
    )

    # ---------------------------------------------------------
    # Push Branch
    # ---------------------------------------------------------
    push = client.post(
        f"/api/v1/projects/{project_id}/git/push",
        json={
            "branch": "feature/authentication",
        },
        headers=headers,
    )

    assert push.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Pull Latest Changes
    # ---------------------------------------------------------
    pull = client.post(
        f"/api/v1/projects/{project_id}/git/pull",
        headers=headers,
    )

    assert pull.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Detect Merge Conflicts
    # ---------------------------------------------------------
    conflicts = client.get(
        f"/api/v1/projects/{project_id}/git/conflicts",
        headers=headers,
    )

    assert conflicts.status_code == 200

    # ---------------------------------------------------------
    # Resolve Merge Conflicts
    # ---------------------------------------------------------
    resolve = client.post(
        f"/api/v1/projects/{project_id}/git/conflicts/resolve",
        json={
            "strategy": "ours",
        },
        headers=headers,
    )

    assert resolve.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Create Tag
    # ---------------------------------------------------------
    tag = client.post(
        f"/api/v1/projects/{project_id}/git/tags",
        json={
            "name": "v1.0.0",
        },
        headers=headers,
    )

    assert tag.status_code == 201

    # ---------------------------------------------------------
    # Rollback Commit
    # ---------------------------------------------------------
    rollback = client.post(
        f"/api/v1/projects/{project_id}/git/rollback",
        json={
            "commit": "HEAD~1",
        },
        headers=headers,
    )

    assert rollback.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Repository Sync
    # ---------------------------------------------------------
    sync = client.post(
        f"/api/v1/projects/{project_id}/git/sync",
        headers=headers,
    )

    assert sync.status_code in (
        200,
        202,
    )

    # ---------------------------------------------------------
    # Git History
    # ---------------------------------------------------------
    history = client.get(
        f"/api/v1/projects/{project_id}/git/history",
        headers=headers,
    )

    assert history.status_code == 200

    assert isinstance(
        history.json(),
        list,
    )

    # ---------------------------------------------------------
    # Delete Project
    # ---------------------------------------------------------
    delete = client.delete(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )

    assert delete.status_code in (
        200,
        204,
    )