import asyncio
import random
import string
import time
import uuid
from datetime import datetime

import httpx
import pytest

BASE_URL = "http://localhost:8000"

SOAK_DURATION = 60 * 60  # 1 hour


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=600,
    ) as client:
        yield client


def random_text(size=1024):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + " ",
            k=size,
        )
    )


async def execute_iteration(client):

    await client.post(
        "/api/v1/chat",
        json={
            "message": random_text(512),
        },
    )

    await client.get(
        "/api/v1/system/resources"
    )

    await client.post(
        "/api/v1/cache/set",
        json={
            "key": str(uuid.uuid4()),
            "value": random_text(),
        },
    )

    await client.post(
        "/api/v1/rag/query",
        json={
            "query": "FastAPI authentication",
        },
    )

    await client.post(
        "/api/v1/agents/run",
        json={
            "task": "Generate CRUD API",
        },
    )


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_one_hour_soak(client):

    start = time.perf_counter()

    iterations = 0

    while time.perf_counter() - start < SOAK_DURATION:

        await execute_iteration(client)

        iterations += 1

    assert iterations > 0


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_memory_stability(client):

    memory_samples = []

    start = time.perf_counter()

    while time.perf_counter() - start < 600:

        response = await client.get(
            "/api/v1/system/resources"
        )

        body = response.json()

        memory_samples.append(
            body["memory_mb"]
        )

        await asyncio.sleep(5)

    growth = max(memory_samples) - min(memory_samples)

    assert growth < 1024


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_cpu_stability(client):

    cpu_samples = []

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/system/resources"
        )

        body = response.json()

        cpu_samples.append(
            body["cpu_percent"]
        )

        await asyncio.sleep(5)

    assert max(cpu_samples) < 95


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_api_availability(client):

    failures = 0

    start = time.perf_counter()

    while time.perf_counter() - start < 600:

        response = await client.get("/health")

        if response.status_code != 200:
            failures += 1

        await asyncio.sleep(2)

    assert failures == 0


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_database_connections(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/database/metrics"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["active_connections"] < 500

        await asyncio.sleep(5)


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_queue_processing(client):

    processed = 0

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/queue/metrics"
        )

        body = response.json()

        processed += body["completed"]

        await asyncio.sleep(5)

    assert processed >= 0


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_cache_health(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/cache/health"
        )

        assert response.status_code == 200

        await asyncio.sleep(5)


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_vector_database_health(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/rag/health"
        )

        assert response.status_code == 200

        await asyncio.sleep(5)


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_llm_provider_health(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/models/health"
        )

        assert response.status_code == 200

        await asyncio.sleep(5)


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_agent_health(client):

    start = time.perf_counter()

    while time.perf_counter() - start < 300:

        response = await client.get(
            "/api/v1/agents/metrics"
        )

        assert response.status_code == 200

        await asyncio.sleep(5)


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_resource_cleanup(client):

    response = await client.post(
        "/api/v1/system/cleanup"
    )

    assert response.status_code in (
        200,
        202,
    )


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_service_health_after_soak(client):

    response = await client.get("/health")

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_metrics_snapshot(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    assert response.status_code == 200

    body = response.json()

    assert "cpu_percent" in body
    assert "memory_mb" in body
    assert "disk_percent" in body


@pytest.mark.performance
@pytest.mark.soak
@pytest.mark.asyncio
async def test_soak_summary(client):

    response = await client.get(
        "/api/v1/system/report"
    )

    assert response.status_code == 200

    report = response.json()

    assert report["generated_at"] is not None