import json
import uuid
from typing import Dict, List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.session import get_db
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schema.project import ProjectCreate, ProjectUpdate, ProjectResponse
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


@router.patch(
    "/{project_id}",
    response_model=ApiResponse,
)
def update_project(
    project_id: str,
    update: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    updated = service.update_project(project, update)

    return ApiResponse(
        success=True,
        message="Project updated successfully.",
        data=ProjectResponse.model_validate(updated),
    )


# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------

@router.get("/{project_id}/env-vars", response_model=ApiResponse)
def get_env_vars(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    env_list = []
    if project.env_vars:
        env_list = [
            {"id": k, "key": k, "value": v}
            for k, v in project.env_vars.items()
        ]

    return ApiResponse(success=True, message="Success", data=env_list)


@router.put("/{project_id}/env-vars", response_model=ApiResponse)
def save_env_vars(
    project_id: str,
    body: Dict[str, str],
    service: ProjectService = Depends(get_project_service),
):
    """Replace all env vars for the project. Accepts a plain key→value dict."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    project.env_vars = body
    service.update_project(project, {})  # commit & refresh

    return ApiResponse(success=True, message="Environment variables saved.")


# ---------------------------------------------------------------------------
# API Keys  (stored as JSON files in project storage, full key never returned)
# ---------------------------------------------------------------------------

def _api_keys_path(project_id: str) -> Path:
    keys_dir = storage.logs_path(project_id).parent / "config"
    keys_dir.mkdir(parents=True, exist_ok=True)
    return keys_dir / "api_keys.json"


def _load_api_keys(project_id: str) -> list:
    path = _api_keys_path(project_id)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except Exception:
        return []


def _save_api_keys(project_id: str, keys: list) -> None:
    path = _api_keys_path(project_id)
    path.write_text(json.dumps(keys, indent=2))


@router.get("/{project_id}/api-keys", response_model=ApiResponse)
def get_api_keys(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    keys = _load_api_keys(project_id)
    # Never expose the full key value — return only the preview
    safe_keys = [
        {"id": k["id"], "label": k["label"], "provider": k["provider"], "preview": k["preview"]}
        for k in keys
    ]
    return ApiResponse(success=True, message="Success", data=safe_keys)


@router.post("/{project_id}/api-keys", response_model=ApiResponse)
def add_api_key(
    project_id: str,
    body: dict,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    label = body.get("label", "").strip()
    provider = body.get("provider", "").strip()
    key_value = body.get("key_value", "").strip()

    if not label or not key_value:
        raise HTTPException(status_code=422, detail="label and key_value are required.")

    keys = _load_api_keys(project_id)
    new_key = {
        "id": str(uuid.uuid4()),
        "label": label,
        "provider": provider or "Custom",
        "preview": f"••••{key_value[-4:]}",
        # Store the real key — never returned by GET, only used internally by agent
        "key_value": key_value,
    }
    keys.append(new_key)
    _save_api_keys(project_id, keys)

    safe = {k: v for k, v in new_key.items() if k != "key_value"}
    return ApiResponse(success=True, message="API key added.", data=safe)


@router.delete("/{project_id}/api-keys/{key_id}", response_model=ApiResponse)
def delete_api_key(
    project_id: str,
    key_id: str,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    keys = _load_api_keys(project_id)
    original_len = len(keys)
    keys = [k for k in keys if k["id"] != key_id]

    if len(keys) == original_len:
        raise HTTPException(status_code=404, detail="API key not found.")

    _save_api_keys(project_id, keys)
    return ApiResponse(success=True, message="API key deleted.")


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


# ---------------------------------------------------------------------------
# Save file content (editor edits)
# ---------------------------------------------------------------------------

@router.put("/{project_id}/files/content", response_model=ApiResponse)
def save_project_file_content(
    project_id: str,
    path: str,
    body: dict,
    service: ProjectService = Depends(get_project_service),
):
    """Save/overwrite a file inside the project's repository directory."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    content = body.get("content", "")

    repo_path = storage.repository_path(project.id)
    target_path = (repo_path / path).resolve()

    # Guard against path traversal
    if not str(target_path).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return ApiResponse(success=True, message="File saved.", data={"path": path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")


# ---------------------------------------------------------------------------
# Git status  (file tree badges)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/status", response_model=ApiResponse)
def get_git_status(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    """Return a dict of {relative_path: status} for changed files in the project repo."""
    import subprocess

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ApiResponse(success=True, message="No git repo", data={})

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        statuses: dict[str, str] = {}
        for line in result.stdout.splitlines():
            if len(line) < 4:
                continue
            xy = line[:2]
            file_path = line[3:].strip()
            # Map porcelain codes to frontend status names
            if "?" in xy:
                statuses[file_path] = "untracked"
            elif xy[1] == "M" or xy[0] == "M":
                statuses[file_path] = "modified"
            elif xy[0] in ("A",):
                statuses[file_path] = "staged"
            elif xy[0] in ("D", "d") or xy[1] in ("D",):
                statuses[file_path] = "deleted"
        return ApiResponse(success=True, message="Success", data=statuses)
    except Exception as e:
        return ApiResponse(success=True, message=f"git status failed: {e}", data={})


# ---------------------------------------------------------------------------
# Project-scoped chat  (called directly by the workspace page)
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _PydanticBase


class _ChatBody(_PydanticBase):
    messages: list[dict]
    model: str = "gpt-4o"
    temperature: float = 0.2


@router.post("/{project_id}/chat", response_model=ApiResponse)
def project_chat(
    project_id: str,
    body: _ChatBody,
    service: ProjectService = Depends(get_project_service),
):
    """
    Simple LLM chat endpoint scoped to a project.

    Uses the project's configured llm_model if no model is given in the request.
    Falls back to a plain HTTP call to supported providers so the workspace page
    works even when the heavier agent pipeline is not available.
    """
    import os
    import httpx

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    # Prefer the project's saved model, fall back to what the client sent
    model = project.llm_model or body.model or "gpt-4o"
    messages = body.messages

    # ── Mistral ────────────────────────────────────────────────────────────
    if "mistral" in model.lower():
        api_key = os.getenv("MISTRAL_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="MISTRAL_API_KEY is not set. Add it in .env or project API keys.",
            )
        try:
            resp = httpx.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "temperature": body.temperature},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return ApiResponse(
                success=True,
                message="OK",
                data={"message": reply, "model": model, "modified_files": []},
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Mistral API error: {e.response.text}")

    # ── OpenAI / GPT ───────────────────────────────────────────────────────
    if "gpt" in model.lower() or "openai" in model.lower():
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="OPENAI_API_KEY is not set. Add it in .env or project API keys.",
            )
        try:
            resp = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "temperature": body.temperature},
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            return ApiResponse(
                success=True,
                message="OK",
                data={"message": reply, "model": model, "modified_files": []},
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"OpenAI API error: {e.response.text}")

    # ── Anthropic / Claude ─────────────────────────────────────────────────
    if "claude" in model.lower() or "anthropic" in model.lower():
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="ANTHROPIC_API_KEY is not set. Add it in .env or project API keys.",
            )
        # Anthropic uses a different messages format: system must be separate
        system_msgs = [m["content"] for m in messages if m.get("role") == "system"]
        chat_msgs = [m for m in messages if m.get("role") != "system"]
        try:
            payload: dict = {
                "model": model,
                "max_tokens": 4096,
                "messages": chat_msgs,
            }
            if system_msgs:
                payload["system"] = "\n".join(system_msgs)
            resp = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            reply = data["content"][0]["text"]
            return ApiResponse(
                success=True,
                message="OK",
                data={"message": reply, "model": model, "modified_files": []},
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Anthropic API error: {e.response.text}")

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported model '{model}'. Use a mistral-*, gpt-*, or claude-* model.",
    )