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
        # The backend process restarted (e.g. --reload picked up a code
        # change) since this session_id was created. terminal_manager is an
        # in-memory dict, so it's wiped on every restart — the frontend may
        # still be holding a stale session_id from sessionStorage. Tell it
        # clearly instead of silently closing, so the terminal UI can show
        # "expired" instead of just looking frozen.
        try:
            await websocket.send_text(
                "\r\n\x1b[31m[Session expired — backend restarted. Click 'Start a new terminal'.]\x1b[0m\r\n"
            )
        except Exception:
            pass
        await websocket.close(code=4001, reason="session_expired")
        return

    queue = asyncio.Queue()
    session.subscribe(queue)

    async def send_to_client():
        try:
            while True:
                data = await queue.get()
                await websocket.send_text(data)
        except Exception:
            pass

    sender_task = asyncio.create_task(send_to_client())

    try:
        while True:
            data = await websocket.receive_text()
            
            # Handle JSON control messages (resize, custom IDE actions)
            try:
                msg = json.loads(data)
                if isinstance(msg, dict):
                    msg_type = msg.get("type")
                    if msg_type == "resize":
                        cols = int(msg.get("cols", 120))
                        rows = int(msg.get("rows", 30))
                        session.resize(cols, rows)
                        continue
                    elif msg_type == "open_file":
                        # Example IDE Action intercept: broadcast back to the frontend
                        # or dispatch to some backend file opener logic.
                        path = msg.get("path")
                        await websocket.send_text(json.dumps({
                            "type": "ide_action",
                            "action": "open_file",
                            "path": path
                        }))
                        continue
            except (json.JSONDecodeError, ValueError):
                pass
                
            # If it's not a handled JSON message, send it to the PTY
            session.write(data)
    except Exception:
        pass
    finally:
        sender_task.cancel()
        session.unsubscribe(queue)
        # Note: We do NOT call `terminal_manager.remove(session_id)` here anymore.
        # This allows the terminal to survive refreshes and supports multiplayer mode.