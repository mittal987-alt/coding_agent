import json
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.session import get_db
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schema.project import ProjectCreate, ProjectResponse
from app.schema.response import ApiResponse
from app.services.project_service import ProjectService
from app.utils.storage_manager import StorageManager

storage = StorageManager()

router = APIRouter()


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    repository = ProjectRepository(db)
    return ProjectService(repository)


@router.post(
    "/",
    response_model=ApiResponse,
    status_code=201
)
def create_project(
    project: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
):
    new_project = service.create_project(project)

    return ApiResponse(
        success=True,
        message="Project created successfully.",
        data=ProjectResponse.model_validate(new_project),
    )


@router.get(
    "/",
)
def get_projects(
    service: ProjectService = Depends(get_project_service),
):
    try:
        projects = service.get_projects()
        return ApiResponse(
            success=True,
            message="Projects fetched successfully.",
            data=[
                ProjectResponse.model_validate(project)
                for project in projects
            ],
        )
    except Exception as e:
        import traceback
        return {
            "success": False,
            "message": str(e),
            "traceback": traceback.format_exc(),
        }


@router.get(
    "/{project_id}",
    response_model=ApiResponse,
)
def get_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return ApiResponse(
        success=True,
        message="Project fetched successfully.",
        data=ProjectResponse.model_validate(project),
    )


@router.delete(
    "/{project_id}",
    response_model=ApiResponse,
)
def delete_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    service.delete_project(project)

    return ApiResponse(
        success=True,
        message="Project deleted successfully.",
    )


@router.post(
    "/{project_id}/upload-folder",
    response_model=ApiResponse,
)
async def upload_folder(
    project_id: str,
    files: List[UploadFile] = File(...),
    paths: str = Form(...),
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    try:
        relative_paths = json.loads(paths)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid 'paths' payload.")

    if len(relative_paths) != len(files):
        raise HTTPException(
            status_code=400,
            detail="Mismatch between number of files and paths.",
        )

    entries = []
    for rel_path, upload in zip(relative_paths, files):
        content = await upload.read()
        entries.append((rel_path, content))

    service.save_uploaded_folder(project, entries)

    return ApiResponse(
        success=True,
        message=f"Uploaded {len(entries)} files successfully.",
    )


def build_file_tree_relative(current_path: Path, repo_root: Path):
    tree = []
    if not current_path.exists():
        return tree

    for item in sorted(current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
        if item.name in [".git", "node_modules", "__pycache__", ".venv", "venv", ".next"]:
            continue

        node = {
            "name": item.name,
            "path": str(item.relative_to(repo_root)).replace("\\", "/"),
            "type": "directory" if item.is_dir() else "file"
        }
        if item.is_dir():
            node["children"] = build_file_tree_relative(item, repo_root)
        tree.append(node)
    return tree


@router.get("/{project_id}/files", response_model=ApiResponse)
def get_project_files(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists():
        return ApiResponse(success=True, message="Success", data=[])

    tree = build_file_tree_relative(repo_path, repo_path)
    return ApiResponse(success=True, message="Success", data=tree)


@router.get("/{project_id}/files/content", response_model=ApiResponse)
def get_project_file_content(
    project_id: str,
    path: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    target_path = (repo_path / path).resolve()

    if not str(target_path).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        content = target_path.read_text(encoding="utf-8")
        return ApiResponse(success=True, message="Success", data={"content": content})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read file: {e}")