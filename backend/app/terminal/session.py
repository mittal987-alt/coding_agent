import os
import sys
import time
import uuid
import asyncio
import select
from collections import deque

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import winpty
else:
    import ptyprocess


class _WindowsPtyBackend:
    """Wraps winpty.PTY with a uniform interface (Windows only)."""

    def __init__(self, cols: int, rows: int):
        self._pty = winpty.PTY(cols=cols, rows=rows)

    def spawn(self, shell: str, cwd: str) -> None:
        self._pty.spawn(shell, cwd=cwd)

    def write(self, data: str) -> None:
        self._pty.write(data)

    def set_size(self, cols: int, rows: int) -> None:
        self._pty.set_size(cols, rows)

    def iseof(self) -> bool:
        return self._pty.iseof()

    def read(self, blocking: bool = False) -> str:
        return self._pty.read(blocking=blocking)

    def close(self) -> None:
        self._pty.close()


class _UnixPtyBackend:
    """Wraps ptyprocess.PtyProcess with the same interface (Linux/macOS)."""

    def __init__(self, cols: int, rows: int):
        self._cols = cols
        self._rows = rows
        self._proc = None

    def spawn(self, shell: str, cwd: str) -> None:
        self._proc = ptyprocess.PtyProcess.spawn(
            [shell],
            cwd=cwd,
            dimensions=(self._rows, self._cols),
        )

    def write(self, data: str) -> None:
        self._proc.write(data.encode("utf-8", errors="ignore"))

    def set_size(self, cols: int, rows: int) -> None:
        self._proc.setwinsize(rows, cols)

    def iseof(self) -> bool:
        return not self._proc.isalive()

    def read(self, blocking: bool = False) -> str:
        try:
            timeout = 0.05 if blocking else 0
            ready, _, _ = select.select([self._proc.fd], [], [], timeout)
            if not ready:
                return ""
            data = self._proc.read(65536)
            return data.decode("utf-8", errors="ignore")
        except EOFError:
            raise
        except Exception:
            return ""

    def close(self) -> None:
        try:
            self._proc.terminate(force=True)
        except Exception:
            pass


class TerminalSession:

    def __init__(self, cwd: str, project_name: str, env_vars: dict | None = None):

        self.id = str(uuid.uuid4())
        self._closed = False

        self.subscribers = []
        # Store up to ~50k characters for scrollback
        self.scrollback = ""
        self._read_task = None

        # Larger PTY size reduces line-wrap frequency which decreases the
        # volume of ANSI cursor-movement bytes npm/other CLIs generate.
        # A wide PTY significantly reduces the chance of the PTY output
        # buffer filling up faster than we can drain it.
        if IS_WINDOWS:
            self.pty = _WindowsPtyBackend(cols=220, rows=50)
            shell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        else:
            self.pty = _UnixPtyBackend(cols=220, rows=50)
            shell = os.environ.get("SHELL", "/bin/bash")

        # cwd is set here directly at process creation — no race, no
        # separate `cd` command needed.
        self.pty.spawn(shell, cwd=cwd)

        # Give the shell a brief moment to finish initializing its input
        # loop before we start writing setup commands. Without this, fast
        # writes immediately after spawn can arrive before the shell is
        # ready to read stdin, causing dropped/scrambled input.
        time.sleep(0.5)

        name = project_name.replace("'", "").replace('"', "")

        if IS_WINDOWS:
            # Use Set-Item to redefine the prompt function. This is the most
            # reliable way to set a custom prompt over a PTY — it avoids the
            # ">>" continuation-prompt trap that occurs when a multi-line
            # function body is sent over stdin and PowerShell waits for the
            # closing brace on a separate line.
            prompt_cmd = (
                f"Set-Item -Path Function:prompt -Value "
                f"{{ Write-Host 'PS ' -ForegroundColor DarkGray -NoNewline; "
                f"Write-Host '{name}' -ForegroundColor Cyan -NoNewline; "
                f"Write-Host '> ' -ForegroundColor DarkGray -NoNewline; "
                f"return ' ' }}\r\n"
            )
            self.write(prompt_cmd)

            # --- npm / Node tooling fixes ---
            # Disable npm's animated progress bar. When npm detects a TTY it
            # renders a spinner/progress bar by writing rapid ANSI escape
            # sequences, which can flood the PTY output pipe faster than the
            # asyncio reader can drain it, causing npm to appear to freeze.
            self.write("$env:NPM_CONFIG_PROGRESS='false'\r\n")
            self.write("$env:NO_UPDATE_NOTIFIER='1'\r\n")
            self.write("$env:NPM_CONFIG_FUND='false'\r\n")
            self.write("$env:NPM_CONFIG_AUDIT='false'\r\n")

            if env_vars:
                for k, v in env_vars.items():
                    if v is not None:
                        escaped_val = str(v).replace("'", "''")
                        self.write(f"$env:{k}='{escaped_val}'\r\n")

            time.sleep(0.15)
            self.write("Clear-Host\r\n")
        else:
            # Bash equivalent of the custom colored prompt above.
            # \[ \] marks non-printing sequences so bash's line-wrap math
            # stays correct with the ANSI color codes.
            prompt_cmd = (
                f"PS1='\\[\\e[90m\\]PS \\[\\e[36m\\]{name}\\[\\e[90m\\]> \\[\\e[0m\\]'\n"
            )
            self.write(prompt_cmd)

            # Same npm-flooding mitigation as the Windows branch above.
            self.write("export NPM_CONFIG_PROGRESS=false\n")
            self.write("export NO_UPDATE_NOTIFIER=1\n")
            self.write("export NPM_CONFIG_FUND=false\n")
            self.write("export NPM_CONFIG_AUDIT=false\n")

            if env_vars:
                for k, v in env_vars.items():
                    if v is not None:
                        # Escape single quotes for bash by closing/reopening
                        # the quoted string around an escaped literal quote.
                        escaped_val = str(v).replace("'", "'\\''")
                        self.write(f"export {k}='{escaped_val}'\n")

            time.sleep(0.15)
            self.write("clear\n")

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
        """Read available output from the PTY.

        Uses non-blocking reads with a short sleep to avoid deadlocking:
        - blocking=True can cause the PTY backend to hold its internal lock
          while waiting for data, which prevents write() from acquiring the
          same lock, creating a deadlock when npm is actively writing output.
        - Non-blocking polling with a tiny sleep keeps CPU usage low while
          ensuring reads and writes can interleave freely.

        Returns:
            str  - output data (may be empty string — caller should handle).
            None - the child process has exited; caller should stop reading.
        """
        if self._closed:
            return None
        try:
            if self.pty.iseof():
                self._closed = True
                return None
            # Non-blocking read — returns immediately with whatever is in
            # the buffer (may be empty string if nothing ready yet).
            data = self.pty.read(blocking=False)
            if not data:
                # Nothing available right now; yield briefly so we don't
                # busy-spin and so write() can acquire the PTY lock.
                if self.pty.iseof():
                    self._closed = True
                    return None
                time.sleep(0.01)
            return data
        except Exception:
            return None

    def subscribe(self, queue: asyncio.Queue) -> None:
        if queue not in self.subscribers:
            self.subscribers.append(queue)
            # Instantly send scrollback history to the new subscriber
            if self.scrollback:
                queue.put_nowait(self.scrollback)

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        if queue in self.subscribers:
            self.subscribers.remove(queue)

    def start_reading(self) -> None:
        """Launch background task to constantly drain PTY and push to subscribers."""
        if self._read_task is not None:
            return

        async def _read_loop():
            loop = asyncio.get_running_loop()
            try:
                while not self._closed:
                    data = await loop.run_in_executor(None, self.read)
                    if data is None:
                        break
                    if data:
                        # Append to scrollback
                        self.scrollback += data
                        if len(self.scrollback) > 50000:
                            self.scrollback = self.scrollback[-50000:]
                        # Broadcast to all connected clients
                        for q in list(self.subscribers):
                            try:
                                q.put_nowait(data)
                            except Exception:
                                pass
            except Exception:
                pass
            finally:
                self.close()

        self._read_task = asyncio.create_task(_read_loop())

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._read_task:
            self._read_task.cancel()
        try:
            self.pty.close()
        except Exception:
            pass