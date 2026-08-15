from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.project_repository import ProjectRepository
from app.utils.storage_manager import StorageManager
from app.terminal.manager import terminal_manager

router = APIRouter()

storage = StorageManager()

@router.post("/projects/{project_id}")
def create_terminal(
    project_id: str,
    db: Session = Depends(get_db),
):
    project = ProjectRepository(db).get_by_id(project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    repo_path = storage.repository_path(project.id)

    session = terminal_manager.create(
        cwd=str(repo_path),
        project_name=project.name,
        env_vars=project.env_vars,
    )

    return {
        "session_id": session.id
    }