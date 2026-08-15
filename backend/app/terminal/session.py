import time
import uuid
import winpty


class TerminalSession:

    def __init__(self, cwd: str, project_name: str, env_vars: dict | None = None):

        self.id = str(uuid.uuid4())
        self._closed = False

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
        time.sleep(0.5)

        # Use Set-Item to redefine the prompt function. This is the most
        # reliable way to set a custom prompt over a PTY — it avoids the
        # ">>" continuation-prompt trap that occurs when a multi-line
        # function body is sent over stdin and PowerShell waits for the
        # closing brace on a separate line.
        #
        # The scriptblock is a single line so PowerShell never enters
        # continuation mode. Single-quotes are used inside to avoid any
        # quoting collisions with the Python f-string double-quotes.
        name = project_name.replace("'", "").replace('"', "")
        prompt_cmd = (
            f"Set-Item -Path Function:prompt -Value "
            f"{{ Write-Host 'PS ' -ForegroundColor DarkGray -NoNewline; "
            f"Write-Host '{name}' -ForegroundColor Cyan -NoNewline; "
            f"Write-Host '> ' -ForegroundColor DarkGray -NoNewline; "
            f"return ' ' }}\r\n"
        )
        self.write(prompt_cmd)

        if env_vars:
            for k, v in env_vars.items():
                if v is not None:
                    # Escape single quotes in powershell by doubling them
                    escaped_val = str(v).replace("'", "''")
                    self.write(f"$env:{k}='{escaped_val}'\r\n")

        time.sleep(0.15)
        self.write("Clear-Host\r\n")

    def write(self, data: str) -> None:
        if not self._closed:
            try:
                self.pty.write(data)
            except Exception:
                pass

    def resize(self, cols: int, rows: int) -> None:
        if not self._closed:
            try:
                self.pty.set_size(cols, rows)
            except Exception:
                pass

    def read(self) -> str | None:
        """Blocking read from the PTY.

        Blocks the calling thread until data is available or the child process
        exits. This is intentionally blocking so that `asyncio.run_in_executor`
        can park a thread cheaply without busy-polling.

        Returns:
            str  - output data (always non-empty when process is alive).
            None - the child process has exited; caller should stop reading.
        """
        if self._closed:
            return None
        try:
            # Check for process exit before blocking.
            if self.pty.iseof():
                self._closed = True
                return None
            # blocking=True: thread waits here until winpty has data ready.
            data = self.pty.read(blocking=True)
            # After a blocking read, check again — a zero-length result after
            # blocking usually means the child process just exited.
            if not data and self.pty.iseof():
                self._closed = True
                return None
            return data
        except Exception:
            return None

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.pty.close()
        except Exception:
            pass