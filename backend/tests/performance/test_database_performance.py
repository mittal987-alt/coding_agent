import asyncio
import statistics
import time
import uuid

import asyncpg
import pytest

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/ai_engineer"


@pytest.fixture
async def db():
    conn = await asyncpg.connect(DATABASE_URL)
    yield conn
    await conn.close()


@pytest.mark.performance
@pytest.mark.asyncio
async def test_single_insert_latency(db):
    latencies = []

    for _ in range(200):
        project_id = str(uuid.uuid4())

        start = time.perf_counter()

        await db.execute(
            """
            INSERT INTO projects(id,name)
            VALUES($1,$2)
            """,
            project_id,
            "Performance Test",
        )

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    avg = statistics.mean(latencies)
    p95 = sorted(latencies)[190]

    assert avg < 20
    assert p95 < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_bulk_insert(db):
    rows = [
        (
            str(uuid.uuid4()),
            f"Project {i}",
        )
        for i in range(1000)
    ]

    start = time.perf_counter()

    await db.executemany(
        """
        INSERT INTO projects(id,name)
        VALUES($1,$2)
        """,
        rows,
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_primary_key_lookup(db):
    project_id = str(uuid.uuid4())

    await db.execute(
        """
        INSERT INTO projects(id,name)
        VALUES($1,$2)
        """,
        project_id,
        "Lookup",
    )

    latencies = []

    for _ in range(500):
        start = time.perf_counter()

        await db.fetchrow(
            """
            SELECT *
            FROM projects
            WHERE id=$1
            """,
            project_id,
        )

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_index_scan(db):
    start = time.perf_counter()

    await db.fetch(
        """
        SELECT *
        FROM projects
        ORDER BY created_at DESC
        LIMIT 100
        """
    )

    elapsed = (time.perf_counter() - start) * 1000

    assert elapsed < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_reads(db):

    async def read():
        await db.fetch(
            """
            SELECT *
            FROM projects
            LIMIT 100
            """
        )

    start = time.perf_counter()

    await asyncio.gather(
        *[read() for _ in range(500)]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 10


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_writes(db):

    async def write(i):
        await db.execute(
            """
            INSERT INTO projects(id,name)
            VALUES($1,$2)
            """,
            str(uuid.uuid4()),
            f"P{i}",
        )

    start = time.perf_counter()

    await asyncio.gather(
        *[
            write(i)
            for i in range(300)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 15


@pytest.mark.performance
@pytest.mark.asyncio
async def test_transaction_latency(db):

    start = time.perf_counter()

    async with db.transaction():

        await db.execute(
            """
            INSERT INTO projects(id,name)