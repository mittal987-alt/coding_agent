import time
import uuid
import winpty
import os
import tempfile

class DockerTerminalSession:
    def __init__(self, cwd: str, project_name: str, env_vars: dict | None = None):
        self.id = str(uuid.uuid4())
        self._closed = False

        self.pty = winpty.PTY(
            cols=120,
            rows=30,
        )

        # Create a temporary batch file to launch docker with arguments.
        # This avoids any issues with winpty's argument parsing.
        self.bat_path = os.path.join(tempfile.gettempdir(), f"docker_run_{self.id}.bat")
        
        # Mount the project directory into the container
        # Using python:3.11-slim as a lightweight, capable base image
        docker_cmd = (
            f'docker run -it --rm '
            f'--memory="512m" --cpus="1.0" '
            f'--security-opt="no-new-privileges:true" --cap-drop=ALL '
            f'-v "{cwd}:/workspace" -w /workspace '
        )
        
        if env_vars:
            for k, v in env_vars.items():
                if v is not None:
                    # Escape quotes for batch file
                    escaped_val = str(v).replace('"', '\\"')
                    docker_cmd += f'-e {k}="{escaped_val}" '
                    
        docker_cmd += 'python:3.11-slim bash'
        
        with open(self.bat_path, "w") as f:
            f.write("@echo off\r\n")
            f.write(f"{docker_cmd}\r\n")

        # Spawn cmd.exe to run the batch file
        self.pty.spawn(r"C:\Windows\System32\cmd.exe", cwd=cwd)
        
        # Execute the batch file to start docker
        time.sleep(0.5)
        self.write(f"{self.bat_path}\r\n")
        
        # Clean up the console
        time.sleep(1)
        self.write("clear\r\n")
        
        # Setup a nice prompt in bash
        name = project_name.replace("'", "").replace('"', "")
        prompt_cmd = f"export PS1='\\[\\e[38;5;240m\\][Docker]\\[\\e[0m\\] \\[\\e[36m\\]{name}\\[\\e[0m\\] \\[\\e[38;5;240m\\]> \\[\\e[0m\\]'\r\n"
        self.write(prompt_cmd)
        time.sleep(0.1)
        self.write("clear\r\n")

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
        if self._closed:
            return None
        try:
            if self.pty.iseof():
                self._closed = True
                return None
            data = self.pty.read(blocking=True)
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
        
        # Clean up the temporary batch file
        try:
            if os.path.exists(self.bat_path):
                os.remove(self.bat_path)
        except Exception:
            pass
