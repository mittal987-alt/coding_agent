import pytest

from fastapi.testclient import TestClient


def test_list_tools(
    client: TestClient,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_get_tool(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/search_files",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["name"] == "search_files"


def test_execute_tool(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "search_files",
            "arguments": {
                "query": "main.py",
            },
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    body = response.json()

    assert "execution_id" in body


def test_execution_status(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/executions/execution-1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "status" in body


def test_retry_execution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/executions/execution-1/retry",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_cancel_execution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/executions/execution-1/cancel",
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )


def test_sandbox_execution(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/sandbox",
        json={
            "tool": "python",
            "code": "print('Hello World')",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )

    body = response.json()

    assert "output" in body


def test_mcp_tools(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/mcp",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_tool_permissions(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "delete_file",
            "arguments": {
                "path": "/etc/passwd",
            },
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        401,
        403,
    )


def test_tool_logs(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_audit_records(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/audit",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_tool_timeout(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "long_running_task",
            "arguments": {},
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        408,
        504,
    )


def test_tool_not_found(
    client,
    auth_headers,
):
    response = client.get(
        "/api/v1/tools/invalid-tool",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_requires_authentication(
    client,
):
    response = client.get(
        "/api/v1/tools",
    )

    assert response.status_code == 401


def test_invalid_tool_payload(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/tools/execute",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 422