from .session import TerminalSession


class TerminalManager:

    def __init__(self):
        self.sessions = {}

    def create(self, cwd: str, project_name: str):

        session = TerminalSession(
            cwd=cwd,
            project_name=project_name,
        )

        self.sessions[session.id] = session

        return session

    def get(self, session_id):
        return self.sessions.get(session_id)

    def remove(self, session_id):
        session = self.sessions.pop(session_id, None)

        if session:
            session.close()


terminal_manager = TerminalManager()