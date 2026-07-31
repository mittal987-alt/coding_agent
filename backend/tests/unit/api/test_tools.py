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
def test_invalid_tool(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "does_not_exist",
            "arguments": {},
        },
        headers=auth_headers,
    )

    assert response.status_code == 404
def test_invalid_parameters(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "search_files",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
def test_permission_denied(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "delete_file",
            "arguments": {
                "path": "/tmp/demo.txt",
            },
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        401,
        403,
    )
def test_sandbox_execution(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/sandbox",
        json={
            "tool": "python",
            "code": "print('hello')",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_tool_timeout(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/execute",
        json={
            "tool": "long_running",
            "arguments": {},
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        408,
        504,
    )
def test_tool_retry(
    client,
    auth_headers,
):

    response = client.post(
        "/api/v1/tools/retry",
        json={
            "execution_id": "tool-run-1",
        },
        headers=auth_headers,
    )

    assert response.status_code in (
        200,
        202,
    )
def test_mcp_discovery(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/tools/mcp",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_execution_history(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/tools/history",
        headers=auth_headers,
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )
def test_execution_logs(
    client,
    auth_headers,
):

    response = client.get(
        "/api/v1/tools/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200
def test_requires_authentication(
    client,
):

    response = client.get(
        "/api/v1/tools",
    )

    assert response.status_code == 401