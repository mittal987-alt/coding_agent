from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.session import get_db
from app.repositories.project_repository import ProjectRepository
from app.utils.storage_manager import StorageManager
from app.terminal.manager import terminal_manager

router = APIRouter()

storage = StorageManager()

# Project manifest files that indicate a project root directory
_PROJECT_MANIFEST_FILES = [
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "Makefile",
    "setup.py",
]

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".next", "dist", "build", ".venv", "venv"}


def _find_project_root(repo_path: Path) -> Path:
    """
    Return the actual project root directory.

    Checks the repository root first. If no manifest file is found there,
    walks one level of immediate subdirectories to find the real root
    (handles the common case where a local folder was uploaded and the
    files ended up nested one level deep, e.g. repository/my-app/).
    """
    # Check root first
    for manifest in _PROJECT_MANIFEST_FILES:
        if (repo_path / manifest).exists():
            return repo_path

    # Check immediate subdirectories (one level deep)
    try:
        for sub in sorted(repo_path.iterdir()):
            if sub.is_dir() and sub.name not in _SKIP_DIRS:
                for manifest in _PROJECT_MANIFEST_FILES:
                    if (sub / manifest).exists():
                        return sub
    except Exception:
        pass

    return repo_path


@router.post("/projects/{project_id}")
def create_terminal(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = ProjectRepository(db).get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    repo_path = storage.repository_path(project.id)
    project_root = _find_project_root(repo_path)

    session = terminal_manager.create(
        cwd=str(project_root),
        project_name=project.name,
        env_vars=project.env_vars,
    )

    return {
        "session_id": session.id
    }