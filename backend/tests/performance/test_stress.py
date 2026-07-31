import asyncio
import random
import string
import time
import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=900,
    ) as client:
        yield client


def random_text(size=2048):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + " ",
            k=size,
        )
    )


async def submit_job(client, i):

    return await client.post(
        "/api/v1/agents/run",
        json={
            "workspace_id": str(uuid.uuid4()),
            "task": f"Stress Job {i}",
            "prompt": random_text(),
        },
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_extreme_concurrent_requests(client):

    start = time.perf_counter()

    responses = await asyncio.gather(
        *[
            submit_job(client, i)
            for i in range(2000)
        ]
    )

    elapsed = time.perf_counter() - start

    success = sum(
        r.status_code == 200
        for r in responses
    )

    assert success >= 1900
    assert elapsed < 600


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_api_request_flood(client):

    async def request():

        response = await client.get(
            "/health"
        )

        assert response.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            request()
            for _ in range(5000)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 120


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_database_stress(client):

    payload = [
        {
            "title": f"Record {i}",
            "content": random_text(1024),
        }
        for i in range(10000)
    ]

    response = await client.post(
        "/api/v1/database/bulk",
        json=payload,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_cache_stress(client):

    async def cache_write(i):

        await client.post(
            "/api/v1/cache/set",
            json={
                "key": f"stress-{i}",
                "value": random_text(1024),
            },
        )

    await asyncio.gather(
        *[
            cache_write(i)
            for i in range(10000)
        ]
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_vector_database_stress(client):

    docs = {
        "documents": [
            {
                "id": str(uuid.uuid4()),
                "text": random_text(),
            }
            for _ in range(10000)
        ]
    }

    response = await client.post(
        "/api/v1/rag/documents",
        json=docs,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_llm_request_storm(client):

    async def generate():

        response = await client.post(
            "/api/v1/chat",
            json={
                "message": random_text(512),
            },
        )

        assert response.status_code in (
            200,
            429,
            503,
        )

    await asyncio.gather(
        *[
            generate()
            for _ in range(500)
        ]
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_workspace_stress(client):

    payload = {
        "files": [
            {
                "path": f"src/file_{i}.py",
                "content": random_text(4096),
            }
            for i in range(5000)
        ]
    }

    response = await client.post(
        "/api/v1/workspaces/import",
        json=payload,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_websocket_stress(client):

    response = await client.get(
        "/api/v1/websocket/metrics"
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_queue_stress(client):

    jobs = [
        {
            "id": str(uuid.uuid4()),
            "task": f"Job {i}",
        }
        for i in range(10000)
    ]

    response = await client.post(
        "/api/v1/queue/bulk",
        json=jobs,
    )

    assert response.status_code in (
        200,
        201,
        202,
    )


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_memory_pressure(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["memory_mb"] < 16384


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_cpu_pressure(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["cpu_percent"] < 100


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_disk_pressure(client):

    response = await client.get(
        "/api/v1/system/storage"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["usage_percent"] < 95


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_service_survival(client):

    response = await client.get(
        "/health"
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.stress
@pytest.mark.asyncio
async def test_recovery_after_stress(client):

    start = time.perf_counter()

    response = await client.get(
        "/health"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2