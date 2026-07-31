import os
import uuid
import winpty


class TerminalSession:
    def __init__(self, cwd: str, name: str = "project"):
        self.id = str(uuid.uuid4())

        self.pty = winpty.PTY(cols=120, rows=30)

        shell = os.environ.get(
            "COMSPEC",
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        )

        self.pty.spawn(shell, cwd=cwd)

        safe_name = name.replace('"', '')
        self.write(f'function prompt {{ "{safe_name}> " }}\r\n')

    def write(self, data: str):
        self.pty.write(data)

    def read(self) -> str:
        try:
            return self.pty.read()
        except Exception:
            return ""

    def close(self):
        try:
            self.pty.close()
        except Exception:
            pass