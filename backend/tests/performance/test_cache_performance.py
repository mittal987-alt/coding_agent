import asyncio
import random
import string
import statistics
import time

import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=120,
    ) as client:
        yield client


def random_key():
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=16,
        )
    )


def random_value():
    return "".join(
        random.choices(
            string.ascii_letters,
            k=4096,
        )
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_cache_write(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/cache/set",
        json={
            "key": random_key(),
            "value": random_value(),
        },
    )

    elapsed = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_cache_read(client):

    key = random_key()

    await client.post(
        "/api/v1/cache/set",
        json={
            "key": key,
            "value": random_value(),
        },
    )

    start = time.perf_counter()

    response = await client.get(
        f"/api/v1/cache/{key}"
    )

    elapsed = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_hit_rate(client):

    key = random_key()

    await client.post(
        "/api/v1/cache/set",
        json={
            "key": key,
            "value": random_value(),
        },
    )

    hits = 0

    for _ in range(100):

        response = await client.get(
            f"/api/v1/cache/{key}"
        )

        if response.status_code == 200:
            hits += 1

    assert hits >= 95


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_cache_write(client):

    payload = [
        {
            "key": random_key(),
            "value": random_value(),
        }
        for _ in range(1000)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/cache/bulk",
        json=payload,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_cache_read(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/cache/bulk/read",
        json={
            "keys": [
                random_key()
                for _ in range(1000)
            ]
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_reads(client):

    async def read():

        await client.get(
            f"/api/v1/cache/{random_key()}"
        )

    start = time.perf_counter()

    await asyncio.gather(
        *[
            read()
            for _ in range(1000)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_writes(client):

    async def write():

        await client.post(
            "/api/v1/cache/set",
            json={
                "key": random_key(),
                "value": random_value(),
            },
        )

    start = time.perf_counter()

    await asyncio.gather(
        *[
            write()
            for _ in range(500)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 15


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_eviction(client):

    response = await client.post(
        "/api/v1/cache/evict",
        json={
            "policy": "lru",
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_expiration(client):

    key = random_key()

    await client.post(
        "/api/v1/cache/set",
        json={
            "key": key,
            "value": random_value(),
            "ttl": 2,
        },
    )

    await asyncio.sleep(3)

    response = await client.get(
        f"/api/v1/cache/{key}"
    )

    assert response.status_code == 404


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_statistics(client):

    response = await client.get(
        "/api/v1/cache/stats"
    )

    assert response.status_code == 200

    body = response.json()

    assert "hits" in body
    assert "misses" in body
    assert "hit_rate" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_latency_distribution(client):

    latencies = []

    for _ in range(100):

        start = time.perf_counter()

        await client.get(
            f"/api/v1/cache/{random_key()}"
        )

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 10
    assert max(latencies) < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_memory_usage(client):

    response = await client.get(
        "/api/v1/cache/metrics"
    )

    body = response.json()

    assert body["memory_mb"] < 4096


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_failover(client):

    response = await client.post(
        "/api/v1/cache/failover"
    )

    assert response.status_code in (
        200,
        202,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cache_cluster_health(client):

    response = await client.get(
        "/api/v1/cache/health"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "healthy"