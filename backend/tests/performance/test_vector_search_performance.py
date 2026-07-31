import asyncio
import random
import string
import time
import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"

VECTOR_DIM = 1536


def random_text(length=512):
    return "".join(
        random.choice(string.ascii_letters + " ")
        for _ in range(length)
    )


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=120,
    ) as client:
        yield client


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_document_indexing(client):

    payload = {
        "id": str(uuid.uuid4()),
        "text": random_text(),
    }

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/index",
        json=payload,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_indexing(client):

    docs = [
        {
            "id": str(uuid.uuid4()),
            "text": random_text(),
        }
        for _ in range(1000)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/index/bulk",
        json=docs,
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_similarity_search_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/search",
        json={
            "query": random_text(128),
            "top_k": 10,
        },
    )

    latency = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert latency < 150


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_top_k(client):

    response = await client.post(
        "/api/v1/rag/search",
        json={
            "query": random_text(128),
            "top_k": 100,
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_searches(client):

    async def search():
        r = await client.post(
            "/api/v1/rag/search",
            json={
                "query": random_text(64),
                "top_k": 5,
            },
        )
        assert r.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[search() for _ in range(500)]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 15


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_indexing(client):

    async def upload():

        return await client.post(
            "/api/v1/rag/index",
            json={
                "id": str(uuid.uuid4()),
                "text": random_text(),
            },
        )

    responses = await asyncio.gather(
        *[upload() for _ in range(300)]
    )

    assert all(
        r.status_code in (200, 201)
        for r in responses
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_filter_search(client):

    response = await client.post(
        "/api/v1/rag/search",
        json={
            "query": "database",
            "filters": {
                "language": "python",
                "repository": "backend",
            },
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_namespace_search(client):

    response = await client.post(
        "/api/v1/rag/search",
        json={
            "namespace": "workspace-1",
            "query": "authentication",
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_delete_vectors(client):

    response = await client.delete(
        "/api/v1/rag/vector/test-id"
    )

    assert response.status_code in (
        200,
        204,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_reindex_performance(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/rag/reindex"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (
        200,
        202,
    )

    assert elapsed < 120


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_consumption(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["memory_mb"] < 8192


@pytest.mark.performance
@pytest.mark.asyncio
async def test_vector_database_health(client):

    response = await client.get(
        "/api/v1/rag/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"