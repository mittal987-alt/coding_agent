import time
import uuid
import winpty
import asyncio
from collections import deque


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
        self.pty = winpty.PTY(
            cols=220,
            rows=50,
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

        # --- npm / Node tooling fixes ---
        # Disable npm's animated progress bar.  When npm detects a TTY it
        # renders a spinner/progress bar by writing rapid ANSI escape
        # sequences (cursor-up, clear-line, re-draw) hundreds of times per
        # second.  This flood of bytes fills winpty's output pipe faster
        # than the asyncio reader can drain it, causing npm to block on its
        # own write() call — the visible symptom is the terminal freezing
        # for minutes at a time during `npm install`.
        self.write("$env:NPM_CONFIG_PROGRESS='false'\r\n")
        # Disable the npm update notifier and non-essential network calls
        # that can stall the process on slow/offline environments.
        self.write("$env:NO_UPDATE_NOTIFIER='1'\r\n")
        self.write("$env:NPM_CONFIG_FUND='false'\r\n")
        self.write("$env:NPM_CONFIG_AUDIT='false'\r\n")

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
        """Read available output from the PTY.

        Uses non-blocking reads with a short sleep to avoid deadlocking:
        - blocking=True can cause winpty to hold its internal lock while
          waiting for data, which prevents write() from acquiring the same
          lock, creating a deadlock when npm is actively writing output.
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
                # busy-spin and so write() can acquire the winpty lock.
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