import asyncio
import json
import statistics
import time
import uuid

import pytest
import websockets

WS_URL = "ws://localhost:8000/ws"


@pytest.fixture
async def websocket():

    async with websockets.connect(
        WS_URL,
        max_size=10 * 1024 * 1024,
    ) as ws:
        yield ws


@pytest.mark.performance
@pytest.mark.asyncio
async def test_connection_latency():

    start = time.perf_counter()

    async with websockets.connect(WS_URL):
        pass

    latency = (time.perf_counter() - start) * 1000

    assert latency < 100


@pytest.mark.performance
@pytest.mark.asyncio
async def test_send_receive_latency(websocket):

    payload = {
        "id": str(uuid.uuid4()),
        "message": "hello",
    }

    start = time.perf_counter()

    await websocket.send(json.dumps(payload))

    await websocket.recv()

    latency = (time.perf_counter() - start) * 1000

    assert latency < 50


@pytest.mark.performance
@pytest.mark.asyncio
async def test_large_message(websocket):

    payload = {
        "data": "A" * 1024 * 1024,
    }

    start = time.perf_counter()

    await websocket.send(json.dumps(payload))

    await websocket.recv()

    elapsed = time.perf_counter() - start

    assert elapsed < 5


@pytest.mark.performance
@pytest.mark.asyncio
async def test_stream_messages(websocket):

    start = time.perf_counter()

    for i in range(1000):

        await websocket.send(
            json.dumps(
                {
                    "message": f"msg-{i}",
                }
            )
        )

        await websocket.recv()

    elapsed = time.perf_counter() - start

    assert elapsed < 30


@pytest.mark.performance
@pytest.mark.asyncio
async def test_parallel_connections():

    async def client(i):

        async with websockets.connect(WS_URL) as ws:

            await ws.send(
                json.dumps(
                    {
                        "client": i,
                    }
                )
            )

            await ws.recv()

    start = time.perf_counter()

    await asyncio.gather(
        *[
            client(i)
            for i in range(500)
        ]
    )

    elapsed = time.perf_counter() - start

    assert elapsed < 40


@pytest.mark.performance
@pytest.mark.asyncio
async def test_broadcast_performance(websocket):

    start = time.perf_counter()

    await websocket.send(
        json.dumps(
            {
                "type": "broadcast",
                "message": "hello everyone",
            }
        )
    )

    await websocket.recv()

    elapsed = time.perf_counter() - start

    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_ping_pong(websocket):

    latencies = []

    for _ in range(100):

        start = time.perf_counter()

        pong = await websocket.ping()

        await pong

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

    assert statistics.mean(latencies) < 20


@pytest.mark.performance
@pytest.mark.asyncio
async def test_connection_recovery():

    async with websockets.connect(WS_URL) as ws:

        await ws.close()

    start = time.perf_counter()

    async with websockets.connect(WS_URL):
        pass

    elapsed = time.perf_counter() - start

    assert elapsed < 2


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_rooms():

    async def join(room):

        async with websockets.connect(WS_URL) as ws:

            await ws.send(
                json.dumps(
                    {
                        "room": room,
                    }
                )
            )

            await ws.recv()

    await asyncio.gather(
        *[
            join(f"room-{i}")
            for i in range(100)
        ]
    )


@pytest.mark.performance
@pytest.mark.asyncio
async def test_message_ordering(websocket):

    for i in range(100):

        await websocket.send(
            json.dumps(
                {
                    "sequence": i,
                }
            )
        )

        reply = json.loads(
            await websocket.recv()
        )

        assert reply["sequence"] == i


@pytest.mark.performance
@pytest.mark.asyncio
async def test_binary_messages(websocket):

    payload = bytes(1024 * 512)

    await websocket.send(payload)

    reply = await websocket.recv()

    assert reply is not None


@pytest.mark.performance
@pytest.mark.asyncio
async def test_disconnect_handling(websocket):

    await websocket.close()

    assert websocket.closed


@pytest.mark.performance
@pytest.mark.asyncio
async def test_websocket_metrics():

    import httpx

    async with httpx.AsyncClient(
        base_url="http://localhost:8000"
    ) as client:

        response = await client.get(
            "/api/v1/websocket/metrics"
        )

        assert response.status_code == 200

        body = response.json()

        assert "connections" in body
        assert "messages_sent" in body


@pytest.mark.performance
@pytest.mark.asyncio
async def test_websocket_health():

    import httpx

    async with httpx.AsyncClient(
        base_url="http://localhost:8000"
    ) as client:

        response = await client.get(
            "/api/v1/websocket/health"
        )

        assert response.status_code == 200

        assert response.json()["status"] == "healthy"