import asyncio
import statistics
import time
import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=300,
    ) as client:
        yield client


def task_payload(i: int):
    return {
        "id": str(uuid.uuid4()),
        "type": "agent_task",
        "name": f"Task-{i}",
        "payload": {
            "prompt": f"Generate API endpoint {i}"
        },
    }


@pytest.mark.performance
@pytest.mark.asyncio
async def test_enqueue_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/queue/enqueue",
        json=task_payload(1),
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code in (200, 201)
    assert latency < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_dequeue_latency(client):

    await client.post(
        "/api/v1/queue/enqueue",
        json=task_payload(2),
    )

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/queue/dequeue"
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert latency < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_enqueue(client):

    tasks = [
        task_payload(i)
        for i in range(1000)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/queue/bulk",
        json=tasks,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_enqueue(client):

    async def enqueue(i):

        response = await client.post(
            "/api/v1/queue/enqueue",
            json=task_payload(i),
        )

        assert response.status_code in (200, 201)

    start = time.perf_counter()

    await asyncio.gather(
        *[
            enqueue(i)
            for i in range(500)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_workers(client):

    async def worker():

        response = await client.post(
            "/api/v1/queue/dequeue"
        )

        assert response.status_code in (
            200,
            204,
        )

    start = time.perf_counter()

    await asyncio.gather(
        *[
            worker()
            for _ in range(200)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_queue_throughput(client):

    completed = 0

    start = time.perf_counter()

    for i in range(500):

        response = await client.post(
            "/api/v1/queue/enqueue",
            json=task_payload(i),
        )

        if response.status_code in (200, 201):
            completed += 1

    duration = time.perf_counter() - start

    throughput = completed / duration

    assert throughput > 100


@pytest.mark.performance
@pytest.mark.asyncio
async def test_priority_queue(client):

    response = await client.post(
        "/api/v1/queue/enqueue",
        json={
            **task_payload(999),
            "priority": "high",
        },
    )

    assert response.status_code in (200, 201)


@pytest.mark.performance
@pytest.mark.asyncio
async def test_delayed_jobs(client):

    response = await client.post(
        "/api/v1/queue/schedule",
        json={
            **task_payload(1000),
            "delay": 30,
        },
    )

    assert response.status_code in (200, 201)


@pytest.mark.performance
@pytest.mark.asyncio
async def test_retry_queue(client):

    response = await client.post(
        "/api/v1/queue/retry",
        json={
            "job_id": "failed-job",
        },
    )

    assert response.status_code in (
        200,
        202,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_dead_letter_queue(client):

    response = await client.get(
        "/api/v1/queue/dead-letter"
    )

    assert response.status_code == 200

    body = response.json()

    assert "failed_jobs" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_queue_metrics(client):

    response = await client.get(
        "/api/v1/queue/metrics"
    )

    assert response.status_code == 200

    body = response.json()

    assert "queued" in body
    assert "processing" in body
    assert "completed" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_queue_latency_distribution(client):

    latencies = []

    for i in range(100):

        start = time.perf_counter()

        response = await client.post(
            "/api/v1/queue/enqueue",
            json=task_payload(i),
        )

        assert response.status_code in (200, 201)

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 30
    assert max(latencies) < 100


@pytest.mark.performance
@pytest.mark.asyncio
async def test_queue_health(client):

    response = await client.get(
        "/api/v1/queue/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_queue_resource_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["cpu_percent"] < 90
    assert body["memory_mb"] < 8192