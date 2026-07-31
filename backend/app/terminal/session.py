import os
import uuid
import winpty


class TerminalSession:
    def __init__(self, cwd: str):
        self.id = str(uuid.uuid4())

        # Create a terminal with an initial size
        self.pty = winpty.PTY(cols=120, rows=30)

        shell = os.environ.get(
            "COMSPEC",
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        )

        # Start PowerShell
        self.pty.spawn(shell)

        # Change directory after the shell starts
        self.write(f'cd "{cwd}"\r\n')

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