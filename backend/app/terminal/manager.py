from .session import TerminalSession
from .docker_session import DockerTerminalSession


class TerminalManager:

    def __init__(self):
        self.sessions = {}

    def create(self, cwd: str, project_name: str, env_vars: dict | None = None):

        try:
            # Attempt to use Docker for secure sandboxed execution
            session = DockerTerminalSession(
                cwd=cwd,
                project_name=project_name,
                env_vars=env_vars,
            )
        except Exception as e:
            print(f"Failed to start Docker session: {e}. Falling back to host terminal.")
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