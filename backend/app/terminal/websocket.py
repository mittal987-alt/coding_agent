import asyncio
import json

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
        loop = asyncio.get_running_loop()
        try:
            while True:
                output = await loop.run_in_executor(None, session.read)
                if output is None:
                    break
                if output:
                    await websocket.send_text(output)
        except Exception:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    task = asyncio.create_task(read_terminal())

    try:
        while True:
            data = await websocket.receive_text()
            # Resize control message: {"type":"resize","cols":N,"rows":N}
            try:
                msg = json.loads(data)
                if isinstance(msg, dict) and msg.get("type") == "resize":
                    cols = int(msg.get("cols", 120))
                    rows = int(msg.get("rows", 30))
                    session.resize(cols, rows)
                    continue
            except (json.JSONDecodeError, ValueError):
                pass
            session.write(data)
    except Exception:
        pass
    finally:
        task.cancel()
        terminal_manager.remove(session_id)