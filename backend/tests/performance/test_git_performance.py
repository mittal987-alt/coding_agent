import asyncio
import random
import string
import time
import uuid
from pathlib import Path

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


def random_content(size=4096):
    return "".join(
        random.choices(
            string.ascii_letters + string.digits + "\n ",
            k=size,
        )
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_repository_initialization(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/init",
        json={
            "repository": f"repo-{uuid.uuid4()}",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 201)
    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_commit(client):

    files = [
        {
            "path": f"src/file_{i}.py",
            "content": random_content(),
        }
        for i in range(1000)
    ]

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/commit",
        json={
            "message": "Large commit",
            "files": files,
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_clone_repository(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/clone",
        json={
            "url": "https://github.com/example/repository.git",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 202)
    assert elapsed < 60


@pytest.mark.performance
@pytest.mark.asyncio
async def test_fetch_performance(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/fetch"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_pull_performance(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/pull"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_push_performance(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/push"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 202)
    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_branch_creation(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/branch",
        json={
            "name": "feature-performance",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 201
    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_commits(client):

    async def commit(i):

        response = await client.post(
            "/api/v1/git/commit",
            json={
                "message": f"Commit {i}",
                "files": [
                    {
                        "path": f"file_{i}.txt",
                        "content": random_content(1024),
                    }
                ],
            },
        )

        assert response.status_code == 200

    start = time.perf_counter()

    await asyncio.gather(
        *[
            commit(i)
            for i in range(100)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 60


@pytest.mark.performance
@pytest.mark.asyncio
async def test_repository_status(client):

    start = time.perf_counter()

    response = await client.get(
        "/api/v1/git/status"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1


@pytest.mark.performance
@pytest.mark.asyncio
async def test_diff_generation(client):

    start = time.perf_counter()

    response = await client.get(
        "/api/v1/git/diff"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_log_history(client):

    start = time.perf_counter()

    response = await client.get(
        "/api/v1/git/log"
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 3


@pytest.mark.performance
@pytest.mark.asyncio
async def test_repository_search(client):

    start = time.perf_counter()

    response = await client.post(
        "/api/v1/git/search",
        json={
            "query": "FastAPI",
        },
    )

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_git_metrics(client):

    response = await client.get(
        "/api/v1/git/metrics"
    )

    assert response.status_code == 200

    body = response.json()

    assert "repositories" in body
    assert "commits" in body
    assert "branches" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_git_health(client):

    response = await client.get(
        "/api/v1/git/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "healthy"