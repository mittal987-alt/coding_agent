from .session import TerminalSession


class TerminalManager:

    def __init__(self):
        self.sessions = {}

    def create(self, cwd: str, project_name: str, env_vars: dict | None = None):
        # Always use the host PowerShell terminal session.
        #
        # The DockerTerminalSession was previously attempted first, but it
        # caused two severe problems:
        #   1. It spawns cmd.exe (not PowerShell), so standard commands like
        #      `ls` and `clear` fail with "not recognised".
        #   2. Even when Docker is available, the python:3.11-slim image has
        #      no Node.js, so `npm install` / `npm run dev` break silently.
        #   3. Its blocking=True PTY read held the winpty lock indefinitely,
        #      preventing npm from writing output and causing 30-minute hangs.
        #   4. On shutdown the blocked executor thread caused the
        #      "executor did not finish joining within 300 seconds" error.
        session = TerminalSession(
            cwd=cwd,
            project_name=project_name,
            env_vars=env_vars,
        )

        self.sessions[session.id] = session
        return session

    def get(self, session_id):
        return self.sessions.get(session_id)

    def remove(self, session_id):
        session = self.sessions.pop(session_id, None)

        if session:
            session.close()

    def shutdown_all(self) -> None:
        """Close every active PTY session.

        Called during application shutdown so that any threads blocked in
        `session.read()` (via `run_in_executor`) are unblocked before
        asyncio tears down the executor — preventing the 300-second hang.
        """
        for session in list(self.sessions.values()):
            session.close()
        self.sessions.clear()


terminal_manager = TerminalManager()