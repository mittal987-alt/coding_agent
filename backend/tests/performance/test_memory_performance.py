import asyncio
import gc
import random
import statistics
import string
import time
import tracemalloc
import uuid

import httpx
import psutil
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=300,
    ) as client:
        yield client


def random_text(size=4096):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + " ",
            k=size,
        )
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_process_memory_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert response.status_code == 200
    assert body["memory_mb"] < 8192


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_growth_under_load(client):

    tracemalloc.start()

    for _ in range(100):

        await client.post(
            "/api/v1/chat",
            json={
                "message": random_text(2048),
            },
        )

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    assert peak < 1024 * 1024 * 1024


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_requests_memory(client):

    async def request():

        response = await client.post(
            "/api/v1/chat",
            json={
                "message": random_text(),
            },
        )

        assert response.status_code == 200

    await asyncio.gather(
        *[
            request()
            for _ in range(200)
        ]
    )

    process = psutil.Process()

    memory_mb = process.memory_info().rss / 1024 / 1024

    assert memory_mb < 4096


@pytest.mark.performance
@pytest.mark.asyncio
async def test_workspace_memory(client):

    payload = {
        "files": [
            {
                "path": f"src/file_{i}.py",
                "content": random_text(4096),
            }
            for i in range(1000)
        ]
    }

    response = await client.post(
        "/api/v1/workspaces/import",
        json=payload,
    )

    assert response.status_code in (
        200,
        201,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_vector_memory(client):

    docs = {
        "documents": [
            {
                "id": str(uuid.uuid4()),
                "text": random_text(),
            }
            for _ in range(1000)
        ]
    }

    response = await client.post(
        "/api/v1/rag/documents",
        json=docs,
    )

    assert response.status_code in (
        200,
        201,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_memory(client):

    for i in range(5000):

        await client.post(
            "/api/v1/cache/set",
            json={
                "key": f"key-{i}",
                "value": random_text(2048),
            },
        )

    response = await client.get(
        "/api/v1/cache/metrics"
    )

    body = response.json()

    assert body["memory_mb"] < 4096


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_after_cleanup(client):

    await client.delete(
        "/api/v1/cache/all"
    )

    gc.collect()

    process = psutil.Process()

    memory = process.memory_info().rss / 1024 / 1024

    assert memory < 4096


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_fragmentation(client):

    snapshots = []

    for _ in range(50):

        response = await client.get(
            "/api/v1/system/resources"
        )

        body = response.json()

        snapshots.append(
            body["memory_mb"]
        )

    std = statistics.stdev(snapshots)

    assert std < 512


@pytest.mark.performance
@pytest.mark.asyncio
async def test_long_running_memory(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 60:

        await client.post(
            "/api/v1/chat",
            json={
                "message": random_text(1024),
            },
        )

    process = psutil.Process()

    memory = process.memory_info().rss / 1024 / 1024

    assert memory < 6144


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_memory(client):

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": random_text(50000),
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_upload_memory(client):

    payload = {
        "content": random_text(5_000_000)
    }

    response = await client.post(
        "/api/v1/files/upload",
        json=payload,
    )

    assert response.status_code in (
        200,
        201,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_metrics(client):

    response = await client.get(
        "/api/v1/system/memory"
    )

    assert response.status_code == 200

    body = response.json()

    assert "rss_mb" in body
    assert "virtual_mb" in body
    assert "heap_mb" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_health(client):

    response = await client.get(
        "/api/v1/system/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_leak_detection(client):

    before = psutil.Process().memory_info().rss

    for _ in range(100):

        await client.post(
            "/api/v1/chat",
            json={
                "message": random_text(4096),
            },
        )

    gc.collect()

    after = psutil.Process().memory_info().rss

    growth = (after - before) / 1024 / 1024

    assert growth < 512