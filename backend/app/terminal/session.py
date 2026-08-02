import time
import uuid
import winpty


class TerminalSession:

    def __init__(self, cwd: str, project_name: str):

        self.id = str(uuid.uuid4())

        self.pty = winpty.PTY(
            cols=120,
            rows=30,
        )

        shell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

        # cwd is set here directly at process creation — no race, no
        # separate `cd` command needed.
        self.pty.spawn(shell, cwd=cwd)

        # Give PowerShell a brief moment to finish initializing its input
        # loop before we start writing setup commands. Without this, fast
        # writes immediately after spawn can arrive before the shell is
        # ready to read stdin, causing dropped/scrambled input.
        time.sleep(0.3)

        # Custom prompt, written as a SINGLE line (semicolon-separated)
        # instead of a multi-line block. Multi-line PowerShell function
        # definitions sent over a PTY are fragile — if any line is lost or
        # reordered, PowerShell gets stuck in a ">>" continuation prompt
        # waiting for the closing brace, which is what was happening before.
        prompt_fn = (
            f'function prompt {{ '
            f'Write-Host "PS " -ForegroundColor DarkGray -NoNewline; '
            f'Write-Host "{project_name}" -ForegroundColor Cyan -NoNewline; '
            f'Write-Host "> " -ForegroundColor DarkGray -NoNewline; '
            f'return " " '
            f'}}\r\n'
        )
        self.write(prompt_fn)

        time.sleep(0.1)
        self.write("Clear-Host\r\n")

    def write(self, data: str):
        self.pty.write(data)

    def read(self):
        try:
            return self.pty.read()
        except Exception:
            return ""

    def close(self):
        try:
            self.pty.close()
        except Exception:
            pass