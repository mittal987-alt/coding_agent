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

    async def read_terminal():
        loop = asyncio.get_running_loop()
        try:
            while True:
                # session.read() blocks the executor thread until data
                # is available, so this loop idles efficiently.
                output = await loop.run_in_executor(None, session.read)
                if output is None:
                    # Process exited — close the socket and stop reading.
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