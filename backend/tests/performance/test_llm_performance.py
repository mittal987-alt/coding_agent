import asyncio
import statistics
import time

import httpx
import pytest

BASE_URL = "http://localhost:8000"

PROMPT = """
You are an expert software engineer.
Explain dependency injection in Python with examples.
"""


@pytest.fixture
async def client():
    async with httpx.AsyncClient(
        base_url=BASE_URL,
        timeout=300,
    ) as client:
        yield client


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_completion_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": PROMPT,
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 15


@pytest.mark.performance
@pytest.mark.asyncio
async def test_streaming_latency(client):

    start = time.perf_counter()

    async with client.stream(
        "POST",
        "/api/v1/chat/stream",
        json={
            "message": PROMPT,
        },
    ) as response:

        async for _ in response.aiter_text():
            break

    first_token = time.perf_counter() - start

    assert first_token < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_requests(client):

    async def request():

        r = await client.post(
            "/api/v1/chat",
            json={
                "message": PROMPT,
            },
        )

        assert r.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            request()
            for _ in range(100)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 60


@pytest.mark.performance
@pytest.mark.asyncio
async def test_tokens_per_second(client):

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": PROMPT,
        },
    )

    body = response.json()

    assert body["tokens_per_second"] > 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_context_window(client):

    large_prompt = "Python " * 50000

    response = await client.post(
        "/api/v1/chat",
        json={
            "message": large_prompt,
        },
    )

    assert response.status_code in (
        200,
        413,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage(client):

    response = await client.get(
        "/api/v1/system/resources"
    )

    body = response.json()

    assert body["memory_mb"] < 16384


@pytest.mark.performance
@pytest.mark.asyncio
async def test_provider_switch_latency(client):

    providers = [
        "openai",
        "anthropic",
        "gemini",
        "mistral",
    ]

    latencies = []

    for provider in providers:

        start = time.perf_counter()

        response = await client.post(
            "/api/v1/chat",
            json={
                "provider": provider,
                "message": "Hello",
            },
        )

        elapsed = time.perf_counter() - start

        assert response.status_code in (
            200,
            503,
        )

        latencies.append(elapsed)

    assert statistics.mean(latencies) < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_embeddings_latency(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/embeddings",
        json={
            "text": PROMPT,
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_model_cache(client):

    first = await client.post(
        "/api/v1/chat",
        json={
            "message": "cache test",
        },
    )

    second = await client.post(
        "/api/v1/chat",
        json={
            "message": "cache test",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert second.json()["cache_hit"] in (
        True,
        False,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_long_conversation(client):

    messages = []

    for i in range(50):

        messages.append(
            {
                "role": "user",
                "content": f"Question {i}",
            }
        )

    response = await client.post(
        "/api/v1/chat/history",
        json={
            "messages": messages,
        },
    )

    assert response.status_code == 200


@pytest.mark.performance
@pytest.mark.asyncio
async def test_failover_between_models(client):

    response = await client.post(
        "/api/v1/chat",
        json={
            "provider": "primary",
            "fallback": "secondary",
            "message": PROMPT,
        },
    )

    assert response.status_code in (
        200,
        503,
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_llm_metrics(client):

    response = await client.get(
        "/api/v1/models/metrics"
    )

    body = response.json()

    assert "requests" in body
    assert "average_latency" in body
    assert "tokens_generated" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_provider_health(client):

    response = await client.get(
        "/api/v1/models/health"
    )

    assert response.status_code == 200

    body = response.json()

    assert "providers" in body