#
from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    """
    Manages active WebSocket connections.
    """

    def __init__(self) -> None:

        self.connections: set[WebSocket] = set()

    async def connect(
        self,
        websocket: WebSocket,
    ) -> None:

        await websocket.accept()

        self.connections.add(websocket)

        logger.info(
            "WebSocket connected (%d clients)",
            len(self.connections),
        )

    def disconnect(
        self,
        websocket: WebSocket,
    ) -> None:

        self.connections.discard(websocket)

        logger.info(
            "WebSocket disconnected (%d clients)",
            len(self.connections),
        )
    async def send(
        self,
        websocket: WebSocket,
        event: str,
        data,
    ) -> None:

        await websocket.send_json(
            {
                "event": event,
                "data": data,
            }
        )
    async def broadcast(
        self,
        event: str,
        data,
    ) -> None:

        disconnected = []

        for ws in self.connections:

            try:

                await self.send(
                    ws,
                    event,
                    data,
                )

            except Exception:

                disconnected.append(ws)

        for ws in disconnected:

            self.disconnect(ws)
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):

    await manager.connect(
        websocket,
    )

    try:

        while True:

            message = await websocket.receive_text()

            payload = json.loads(message)

            logger.info(
                "Received websocket event %s",
                payload.get("event"),
            )

            await manager.send(

                websocket,

                "ack",

                {
                    "received": True,
                },
            )

    except WebSocketDisconnect:

        manager.disconnect(
            websocket,
        )

async def publish_chat_token(
    token: str,
):

    await manager.broadcast(

        "chat.token",

        {
            "token": token,
        },
    )
async def publish_agent_update(
    task_id: str,
    status: str,
):

    await manager.broadcast(

        "agent.update",

        {
            "task_id": task_id,

            "status": status,
        },
    )
async def publish_tool_update(
    tool: str,
    state: str,
):

    await manager.broadcast(

        "tool.update",

        {
            "tool": tool,

            "state": state,
        },
    )
async def publish_workspace_event(
    workspace_id: str,
    event: str,
):

    await manager.broadcast(

        "workspace.event",

        {
            "workspace": workspace_id,

            "event": event,
        },
    )