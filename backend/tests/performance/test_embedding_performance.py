import asyncio
import random
import statistics
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
        timeout=300,
    ) as client:
        yield client


def random_text(size=1024):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + " ",
            k=size,
        )
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_embedding_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": random_text(),
        },
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert latency < 1000


@pytest.mark.performance
@pytest.mark.asyncio
async def test_batch_embedding_generation(client):

    payload = {
        "texts": [
            random_text(512)
            for _ in range(500)
        ]
    }

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/embeddings/batch",
        json=payload,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 60


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_embedding_requests(client):

    async def embed():

        response = await client.post(
            "/api/v1/embeddings",
            json={
                "text": random_text(),
            },
        )

        assert response.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            embed()
            for _ in range(200)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 40


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_document_embedding(client):

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": random_text(100000),
        },
    )

    assert response.status_code in (
        200,
        413,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_cache_latency(client):

    text = random_text()

    await client.post(
        "/api/v1/embeddings",
        json={
            "text": text,
        },
    )

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": text,
        },
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert latency < 300


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_dimension(client):

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": "Hello World",
        },
    )

    body = response.json()

    assert len(body["embedding"]) > 0


@pytest.mark.performance
@pytest.mark.asyncio
async def test_similarity_computation(client):

    response = await client.post(
        "/api/v1/embeddings/similarity",
        json={
            "text1": "Python programming",
            "text2": "FastAPI framework",
        },
    )

    assert response.status_code == 200

    score = response.json()["score"]

    assert 0 <= score <= 1


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_storage(client):

    response = await client.post(
        "/api/v1/embeddings/store",
        json={
            "id": str(uuid.uuid4()),
            "text": random_text(),
        },
    )

    assert response.status_code in (
        200,
        201,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_similarity(client):

    response = await client.post(
        "/api/v1/embeddings/search",
        json={
            "query": random_text(),
            "top_k": 100,
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_latency_distribution(client):

    latencies = []

    for _ in range(100):

        start = time.perf_counter()

        response = await client.post(
            "/api/v1/embeddings",
            json={
                "text": random_text(),
            },
        )

        assert response.status_code == 200

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 1000


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_metrics(client):

    response = await client.get(
        "/api/v1/embeddings/metrics"
    )

    assert response.status_code == 200

    body = response.json()

    assert "requests" in body
    assert "cache_hits" in body
    assert "average_latency" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_health(client):

    response = await client.get(
        "/api/v1/embeddings/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_resource_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["cpu_percent"] < 90
    assert body["memory_mb"] < 8192


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_cleanup(client):

    response = await client.delete(
        "/api/v1/embeddings/cache"
    )

    assert response.status_code in (
        200,
        202,
        204,
    )