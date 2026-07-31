import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.terminal.manager import terminal_manager

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def terminal_socket(
    websocket: WebSocket,
    session_id: str,
):

    await websocket.accept()

    session = terminal_manager.get(session_id)

    if session is None:
        await websocket.close()
        return

    async def read_terminal():

        while True:

            output = session.read()

            if output:
                await websocket.send_text(output)

            await asyncio.sleep(0.02)

    task = asyncio.create_task(read_terminal())

    try:

        while True:

            data = await websocket.receive_text()

            session.write(data)

    except WebSocketDisconnect:

        task.cancel()

        terminal_manager.remove(session_id)