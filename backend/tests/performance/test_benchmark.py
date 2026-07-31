import asyncio
import csv
import statistics
import time
from datetime import datetime
from pathlib import Path
import uuid

import httpx
import pytest

BASE_URL = "http://localhost:8000"

OUTPUT_DIR = Path("benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=600,
    ) as client:
        yield client


class Benchmark:

    def __init__(self):
        self.results = []

    def add(
        self,
        name,
        latency,
        success=True,
    ):
        self.results.append(
            {
                "test": name,
                "latency_ms": latency,
                "success": success,
            }
        )

    def export(self):

        filename = (
            OUTPUT_DIR /
            f"benchmark_{datetime.utcnow():%Y%m%d_%H%M%S}.csv"
        )

        with open(
            filename,
            "w",
            newline="",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "test",
                    "latency_ms",
                    "success",
                ],
            )

            writer.writeheader()

            for row in self.results:
                writer.writerow(row)

        return filename


benchmark = Benchmark()


async def benchmark_endpoint(
    client,
    name,
    method,
    url,
    **kwargs,
):

    start = time.perf_counter()

    response = await client.request(
        method,
        url,
        **kwargs,
    )

    latency = (
        time.perf_counter() - start
    ) * 1000

    benchmark.add(
        name,
        latency,
        response.status_code < 400,
    )

    return response, latency


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_health_endpoint(client):

    response, latency = await benchmark_endpoint(
        client,
        "health",
        "GET",
        "/health",
    )

    assert response.status_code == 200
    assert latency < 100


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_chat_endpoint(client):

    response, latency = await benchmark_endpoint(
        client,
        "chat",
        "POST",
        "/api/v1/chat",
        json={
            "message": "Explain FastAPI",
        },
    )

    assert response.status_code == 200
    assert latency < 15000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_embedding_endpoint(client):

    response, latency = await benchmark_endpoint(
        client,
        "embedding",
        "POST",
        "/api/v1/embeddings",
        json={
            "text": "Benchmark",
        },
    )

    assert response.status_code == 200
    assert latency < 5000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_vector_search(client):

    response, latency = await benchmark_endpoint(
        client,
        "rag_search",
        "POST",
        "/api/v1/rag/query",
        json={
            "query": "authentication",
        },
    )

    assert response.status_code == 200
    assert latency < 500


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_cache_lookup(client):

    key = str(uuid.uuid4())

    await client.post(
        "/api/v1/cache/set",
        json={
            "key": key,
            "value": "benchmark",
        },
    )

    response, latency = await benchmark_endpoint(
        client,
        "cache_lookup",
        "GET",
        f"/api/v1/cache/{key}",
    )

    assert response.status_code == 200
    assert latency < 50


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_database_query(client):

    response, latency = await benchmark_endpoint(
        client,
        "database_query",
        "GET",
        "/api/v1/database/metrics",
    )

    assert response.status_code == 200
    assert latency < 200


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_agent_execution(client):

    response, latency = await benchmark_endpoint(
        client,
        "agent_execution",
        "POST",
        "/api/v1/agents/run",
        json={
            "task": "Generate REST API",
        },
    )

    assert response.status_code == 200
    assert latency < 20000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_parallel_chat_requests(client):

    async def run():

        _, latency = await benchmark_endpoint(
            client,
            "parallel_chat",
            "POST",
            "/api/v1/chat",
            json={
                "message": "Hello",
            },
        )

        return latency

    latencies = await asyncio.gather(
        *[
            run()
            for _ in range(50)
        ]
    )

    assert statistics.mean(latencies) < 10000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_parallel_embeddings(client):

    async def embed():

        _, latency = await benchmark_endpoint(
            client,
            "parallel_embedding",
            "POST",
            "/api/v1/embeddings",
            json={
                "text": "benchmark",
            },
        )

        return latency

    latencies = await asyncio.gather(
        *[
            embed()
            for _ in range(100)
        ]
    )

    assert statistics.mean(latencies) < 5000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_parallel_rag_queries(client):

    async def query():

        _, latency = await benchmark_endpoint(
            client,
            "parallel_rag",
            "POST",
            "/api/v1/rag/query",
            json={
                "query": "Redis",
            },
        )

        return latency

    latencies = await asyncio.gather(
        *[
            query()
            for _ in range(100)
        ]
    )

    assert statistics.mean(latencies) < 1000


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_system_resources(client):

    response, latency = await benchmark_endpoint(
        client,
        "resources",
        "GET",
        "/api/v1/system/resources",
    )

    assert response.status_code == 200
    assert latency < 100


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_metrics_endpoint(client):

    response, latency = await benchmark_endpoint(
        client,
        "metrics",
        "GET",
        "/metrics",
    )

    assert response.status_code == 200
    assert latency < 100


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_export_results():

    filename = benchmark.export()

    assert filename.exists()


@pytest.mark.performance
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_benchmark_summary():

    latencies = [
        row["latency_ms"]
        for row in benchmark.results
    ]

    if latencies:

        assert statistics.mean(latencies) >= 0
        assert max(latencies) >= min(latencies)

    successes = sum(
        row["success"]
        for row in benchmark.results
    )

    assert successes >= 0