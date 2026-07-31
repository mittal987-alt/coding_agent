from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Central WebSocket manager.

    Handles:

    - Multiple users
    - Multiple workspaces
    - Execution streams
    - Broadcasts
    """

    def __init__(self):

        self.connections: dict[
            str,
            set[WebSocket],
        ] = defaultdict(set)

        self.lock = asyncio.Lock()

    async def connect(
        self,
        channel: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        async with self.lock:

            self.connections[channel].add(
                websocket
            )

        logger.info(
            "Client connected to %s",
            channel,
        )

    async def disconnect(
        self,
        channel: str,
        websocket: WebSocket,
    ):

        async with self.lock:

            if channel in self.connections:

                self.connections[channel].discard(
                    websocket
                )

                if not self.connections[channel]:

                    del self.connections[channel]

        logger.info(
            "Client disconnected from %s",
            channel,
        )

    async def send(
        self,
        websocket: WebSocket,
        message: dict[str, Any],
    ):

        await websocket.send_text(
            json.dumps(message)
        )

    async def broadcast(
        self,
        channel: str,
        message: dict[str, Any],
    ):

        if channel not in self.connections:

            return

        disconnected = []

        for websocket in self.connections[channel]:

            try:

                await websocket.send_text(
                    json.dumps(message)
                )

            except Exception:

                disconnected.append(websocket)

        for ws in disconnected:

            await self.disconnect(
                channel,
                ws,
            )

    async def publish_event(
        self,
        event,
    ):
        """
        EventBus subscriber.
        """

        channel = (
            event.execution_id
            or event.name
        )

        await self.broadcast(
            channel,
            {
                "event": event.name,
                "timestamp": event.timestamp.isoformat(),
                "payload": event.payload,
            },
        )

    async def terminal_stream(
        self,
        execution_id: str,
        line: str,
    ):

        await self.broadcast(
            execution_id,
            {
                "type": "terminal",

                "line": line,
            },
        )

    async def progress(
        self,
        execution_id: str,
        stage: str,
        percent: int,
    ):

        await self.broadcast(
            execution_id,
            {
                "type": "progress",

                "stage": stage,

                "percent": percent,
            },
        )

    async def metrics(
        self,
        execution_id: str,
        cpu: float,
        memory: float,
    ):

        await self.broadcast(
            execution_id,
            {
                "type": "metrics",

                "cpu": cpu,

                "memory": memory,
            },
        )

    async def logs(
        self,
        execution_id: str,
        stdout: str,
        stderr: str,
    ):

        await self.broadcast(
            execution_id,
            {
                "type": "logs",

                "stdout": stdout,

                "stderr": stderr,
            },
        )

    async def artifact_created(
        self,
        execution_id: str,
        artifact: dict,
    ):

        await self.broadcast(
            execution_id,
            {
                "type": "artifact",

                "artifact": artifact,
            },
        )

    async def handle_client(
        self,
        websocket: WebSocket,
        channel: str,
    ):

        await self.connect(
            channel,
            websocket,
        )

        try:

            while True:

                await websocket.receive_text()

        except WebSocketDisconnect:

            await self.disconnect(
                channel,
                websocket,
            )


websocket_manager = WebSocketManager()