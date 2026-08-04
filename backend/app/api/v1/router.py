from app.api.v1.chat import storage
from fastapi import HTTPException
from app.api.v1.project import get_project_service
from fastapi import Depends
from app.services.project_service import ProjectService
from app.api.schemas.common import ApiResponse
from fastapi import APIRouter
import re
from .health import router as health_router
from .project import router as project_router
from .chat import router as chat_router
from app.terminal.routes import router as terminal_router

from app.schema.project import ProjectCreate, ProjectResponse, ProjectUpdate


api_router = APIRouter()

api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    project_router,
    prefix="/projects",
    tags=["Projects"],
)

api_router.include_router(
    chat_router,
    prefix="/projects/{project_id}/chat",
    tags=["Chat"],
)

api_router.include_router(
    terminal_router,
    prefix="/terminal",
    tags=["Terminal"],
)

@api_router.patch(
    "/{project_id}",
    response_model=ApiResponse,
)
def update_project(
    project_id: str,
    updates: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    updated = service.update_project(project, updates)

    return ApiResponse(
        success=True,
        message="Project updated successfully.",
        data=ProjectResponse.model_validate(updated),
    )



@api_router.get("/{project_id}/search", response_model=ApiResponse)
def search_project_files(
    project_id: str,
    q: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not q or len(q.strip()) < 2:
        return ApiResponse(success=True, message="Query too short", data=[])

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists():
        return ApiResponse(success=True, message="Success", data=[])

    SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".next"}
    TEXT_EXTS = {
        ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".css", ".html",
        ".yml", ".yaml", ".toml", ".txt", ".sh", ".env", ".gitignore",
    }
    MAX_RESULTS = 200
    MAX_FILE_SIZE = 2_000_000  # skip files > 2MB, likely binary/generated

    pattern = re.compile(re.escape(q), re.IGNORECASE)
    results = []

    for path in repo_path.rglob("*"):
        if len(results) >= MAX_RESULTS:
            break
        if path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line_num, line in enumerate(content.splitlines(), start=1):
            if pattern.search(line):
                results.append({
                    "path": str(path.relative_to(repo_path)).replace("\\", "/"),
                    "line": line_num,
                    "preview": line.strip()[:200],
                })
                if len(results) >= MAX_RESULTS:
                    break

    return ApiResponse(success=True, message="Success", data=results)