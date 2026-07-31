import asyncio
import statistics
import string
import random
import time
import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"


def random_text(size=2048):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + " ",
            k=size,
        )
    )


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=300,
    ) as client:
        yield client


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_creation_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces",
        json={
            "name": f"workspace-{uuid.uuid4()}",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_workspace_creation(client):

    files = [
        {
            "path": f"src/file_{i}.py",
            "content": random_text(4096),
        }
        for i in range(1000)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/import",
        json={
            "name": "large-workspace",
            "files": files,
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 120


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_loading(client):

    start = time.perf_counter()

    response = await client.get(
        "/api/v1/workspaces/default"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_file_listing(client):

    start = time.perf_counter()

    response = await client.get(
        "/api/v1/workspaces/default/files"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 3


@pytest.mark.performance
@pytest.mark.asyncio
async def test_search_large_workspace(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/search",
        json={
            "workspace": "default",
            "query": "FastAPI",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_file_upload(client):

    files = [
        {
            "path": f"docs/{i}.md",
            "content": random_text(1024),
        }
        for i in range(500)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/files/bulk",
        json={
            "files": files,
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_workspace_access(client):

    async def load():
        response = await client.get(
            "/api/v1/workspaces/default"
        )
        assert response.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            load()
            for _ in range(200)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 15


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_snapshot(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/default/snapshot"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 202)
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_restore(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/default/restore",
        json={
            "snapshot": "latest",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 202)
    assert elapsed < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_sync(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/workspaces/default/sync"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 202)
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_statistics(client):

    response = await client.get(
        "/api/v1/workspaces/default/stats"
    )

    assert response.status_code == 200

    body = response.json()

    assert "files" in body
    assert "size_bytes" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["memory_mb"] < 8192


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_cache(client):

    latencies = []

    for _ in range(20):

        start = time.perf_counter()

        response = await client.get(
            "/api/v1/workspaces/default"
        )

        assert response.status_code == 200

        latencies.append(
            time.perf_counter() - start
        )

    average = statistics.mean(latencies)

    assert average < 1


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_cleanup(client):

    response = await client.delete(
        "/api/v1/workspaces/default"
    )

    assert response.status_code in (
        200,
        202,
        204,
    )