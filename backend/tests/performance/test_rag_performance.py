import asyncio
import random
import string
import time
import uuid
import statistics

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
async def test_document_ingestion(client):

    payload = {
        "documents": [
            {
                "id": str(uuid.uuid4()),
                "text": random_text(4096),
            }
            for _ in range(500)
        ]
    }

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/documents",
        json=payload,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 60


@pytest.mark.performance
@pytest.mark.asyncio
async def test_query_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/query",
        json={
            "query": "Explain FastAPI authentication",
        },
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert latency < 300


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_queries(client):

    async def query():

        response = await client.post(
            "/api/v1/rag/query",
            json={
                "query": random_text(128),
            },
        )

        assert response.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            query()
            for _ in range(200)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_context_retrieval(client):

    response = await client.post(
        "/api/v1/rag/query",
        json={
            "query": "Python",
            "top_k": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["documents"]) <= 100


@pytest.mark.performance
@pytest.mark.asyncio
async def test_chunking_speed(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/chunk",
        json={
            "text": random_text(50000),
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_reranking_speed(client):

    response = await client.post(
        "/api/v1/rag/rerank",
        json={
            "query": "database indexing",
            "top_k": 50,
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_hybrid_search(client):

    response = await client.post(
        "/api/v1/rag/hybrid-search",
        json={
            "query": "JWT authentication",
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_metadata_filtering(client):

    response = await client.post(
        "/api/v1/rag/query",
        json={
            "query": "Redis",
            "filters": {
                "language": "python",
            },
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embedding_cache(client):

    response = await client.get(
        "/api/v1/rag/cache"
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_vector_lookup_distribution(client):

    latencies = []

    for _ in range(100):

        start = time.perf_counter()

        response = await client.post(
            "/api/v1/rag/query",
            json={
                "query": random_text(32),
            },
        )

        assert response.status_code == 200

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 300


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_delete(client):

    response = await client.delete(
        "/api/v1/rag/documents/all"
    )

    assert response.status_code in (
        200,
        202,
        204,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_rag_metrics(client):

    response = await client.get(
        "/api/v1/rag/metrics"
    )

    assert response.status_code == 200

    body = response.json()

    assert "documents" in body
    assert "queries" in body
    assert "cache_hit_rate" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_rag_health(client):

    response = await client.get(
        "/api/v1/rag/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_resource_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["cpu_percent"] < 90
    assert body["memory_mb"] < 8192