from pydantic import functional_serializers
from pathlib import Path
import hashlib
from datetime import datetime

from app.schemas.repository import RepositoryFile


class ScannerManager:

    IGNORE_DIRECTORIES = {
        ".git",
        ".github",
        ".idea",
        ".vscode",
        "__pycache__",
        ".venv",
        "venv",
        "node_modules",
        "dist",
        "build",
        ".next",
        "coverage",
        ".cache",
    }

    SUPPORTED_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".go": "go",
        ".rs": "rust",
        ".dart": "dart",
        ".php": "php",
        ".cs": "csharp",
        ".kt": "kotlin",
        ".swift": "swift",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".md": "markdown",
        ".html": "html",
        ".css": "css",
    }

    def scan(self, repository_path: Path):

        files = []

        for file in repository_path.rglob("*"):

            if not file.is_file():
                continue

            if any(
                ignored in file.parts
                for ignored in self.IGNORE_DIRECTORIES
            ):
                continue

            extension = file.suffix.lower()

            if extension not in self.SUPPORTED_EXTENSIONS:
                continue

            files.append(
                self._metadata(
                    repository_path,
                    file,
                )
            )

        return files

    def _metadata(
        self,
        repository_root: Path,
        file: Path,
    ) -> RepositoryFile:

        relative_path = file.relative_to(repository_root)

        with open(
            file,
            "rb",
        ) as f:

        data = f.read()

    sha = hashlib.sha256(data).hexdigest()

    try:

        text = data.decode(
            "utf-8",
            errors="ignore",
        )

        lines = len(text.splitlines())

    except Exception:

        lines = 0

        stat = file.stat()

            return RepositoryFile(

            path=str(relative_path),

            extension=file.suffix.lower(),

                language=self.SUPPORTED_EXTENSIONS[
                file.suffix.lower()
            ],

            size=stat.st_size,

            lines=lines,

            sha256=sha,

            modified=datetime.fromtimestamp(
                stat.st_mtime
            ),
        )

        def statistics(
    self,
    files: list[RepositoryFile],
):

    total_lines = sum(
        file.lines
        for file in files
    )

    total_size = sum(
        file.size
        for file in files
    )

    languages = {}

    for file in files:

        languages[file.language] = (
            languages.get(
                file.language,
                0,
            )
            + 1
        )

    return {

        "files": len(files),

        "lines": total_lines,

        "size": total_size,

        "languages": languages,
    }
        