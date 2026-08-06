import json
import uuid
import subprocess
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel as _PydanticBase

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
    """Replace all env vars for the project. Accepts a plain key->value dict."""
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

    if not str(target_path).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")
        return ApiResponse(success=True, message="File saved.", data={"path": path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")


# ---------------------------------------------------------------------------
# File Operations: Create, Rename, Delete
# ---------------------------------------------------------------------------

class _CreateFileBody(_PydanticBase):
    path: str
    is_directory: bool = False
    content: str = ""


@router.post("/{project_id}/files/create", response_model=ApiResponse)
def create_project_file_or_dir(
    project_id: str,
    body: _CreateFileBody,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    target_path = (repo_path / body.path).resolve()

    if not str(target_path).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        if body.is_directory:
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if not target_path.exists():
                target_path.write_text(body.content, encoding="utf-8")
        return ApiResponse(success=True, message="Created successfully.", data={"path": body.path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not create: {e}")


class _RenameFileBody(_PydanticBase):
    old_path: str
    new_path: str


@router.post("/{project_id}/files/rename", response_model=ApiResponse)
def rename_project_file_or_dir(
    project_id: str,
    body: _RenameFileBody,
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    old_target = (repo_path / body.old_path).resolve()
    new_target = (repo_path / body.new_path).resolve()

    if not str(old_target).startswith(str(repo_path.resolve())) or not str(new_target).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not old_target.exists():
        raise HTTPException(status_code=404, detail="Original item not found.")

    try:
        new_target.parent.mkdir(parents=True, exist_ok=True)
        old_target.rename(new_target)
        return ApiResponse(success=True, message="Renamed successfully.", data={"old_path": body.old_path, "new_path": body.new_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not rename: {e}")


@router.delete("/{project_id}/files/delete", response_model=ApiResponse)
def delete_project_file_or_dir(
    project_id: str,
    path: str,
    service: ProjectService = Depends(get_project_service),
):
    import shutil
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    target_path = (repo_path / path).resolve()

    if not str(target_path).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File or folder not found.")

    try:
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        return ApiResponse(success=True, message="Deleted successfully.", data={"path": path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not delete: {e}")


# ---------------------------------------------------------------------------
# Full-repo text search (Ctrl+Shift+F)
# ---------------------------------------------------------------------------

_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".next", "dist", "build", ".venv", "venv"}
_BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".pdf", ".zip", ".gz", ".tar", ".whl", ".exe", ".dll",
    ".pyc", ".pyo", ".class",
}


@router.get("/{project_id}/search", response_model=ApiResponse)
def search_files(
    project_id: str,
    q: str,
    case_sensitive: bool = False,
    service: ProjectService = Depends(get_project_service),
):
    """
    Grep-style search across all text files in the project repo.
    Returns up to 200 matches with file path, line number, and preview snippet.
    """
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not q or len(q.strip()) < 1:
        return ApiResponse(success=True, message="Empty query", data=[])

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists():
        return ApiResponse(success=True, message="No repository", data=[])

    needle = q if case_sensitive else q.lower()
    results: list[dict] = []
    MAX_RESULTS = 200

    try:
        for file_path in repo_path.rglob("*"):
            if len(results) >= MAX_RESULTS:
                break

            if file_path.is_dir():
                continue
            if any(part in _SKIP_DIRS for part in file_path.parts):
                continue
            if file_path.suffix.lower() in _BINARY_EXTS:
                continue

            try:
                if file_path.stat().st_size > 500_000:
                    continue
            except OSError:
                continue

            try:
                lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue

            relative = str(file_path.relative_to(repo_path)).replace("\\", "/")

            for lineno, line in enumerate(lines, start=1):
                haystack = line if case_sensitive else line.lower()
                if needle in haystack:
                    preview = line.strip()
                    if len(preview) > 160:
                        idx = haystack.find(needle)
                        start = max(0, idx - 40)
                        preview = ("…" if start > 0 else "") + line[start: idx + len(q) + 60].strip() + "…"
                    results.append({
                        "path": relative,
                        "line": lineno,
                        "preview": preview,
                    })
                    if len(results) >= MAX_RESULTS:
                        break
    except Exception as e:
        return ApiResponse(success=False, message=f"Search error: {e}", data=[])

    return ApiResponse(success=True, message=f"{len(results)} result(s)", data=results)


# ---------------------------------------------------------------------------
# Git status (file tree badges & Git panel)
# ---------------------------------------------------------------------------

def _ensure_git_repo(repo_path: Path, default_branch: str = "main") -> bool:
    repo_path.mkdir(parents=True, exist_ok=True)
    git_dir = repo_path / ".git"
    if not git_dir.exists():
        try:
            subprocess.run(["git", "init"], cwd=str(repo_path), capture_output=True, timeout=10)
            subprocess.run(["git", "branch", "-M", default_branch], cwd=str(repo_path), capture_output=True, timeout=10)
        except Exception:
            return False
    return True


@router.get("/{project_id}/git/status", response_model=ApiResponse)
def get_git_status(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    """Return a dict of {relative_path: status} for changed files in the project repo."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not _ensure_git_repo(repo_path, project.default_branch or "main"):
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
# Git commit
# ---------------------------------------------------------------------------

class _GitCommitBody(_PydanticBase):
    message: str


@router.post("/{project_id}/git/commit", response_model=ApiResponse)
def git_commit(
    project_id: str,
    body: _GitCommitBody,
    service: ProjectService = Depends(get_project_service),
):
    """Stage all changes and create a commit."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    _ensure_git_repo(repo_path, project.default_branch or "main")

    try:
        subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent", "add", "-A"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        result = subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent", "commit", "-m", body.message],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            return ApiResponse(
                success=False,
                message=result.stderr.strip() or result.stdout.strip(),
                data={},
            )
        return ApiResponse(success=True, message="Committed successfully.", data={"output": result.stdout.strip()})
    except subprocess.CalledProcessError as e:
        return ApiResponse(success=False, message=e.stderr.strip(), data={})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class _GitPushBody(_PydanticBase):
    remote: str = "origin"
    branch: Optional[str] = None


@router.post("/{project_id}/git/push", response_model=ApiResponse)
def git_push(
    project_id: str,
    body: _GitPushBody = _GitPushBody(),
    service: ProjectService = Depends(get_project_service),
):
    """Push local commits to remote GitHub repository."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    target_branch = body.branch or project.default_branch or "main"
    remote = body.remote or "origin"

    # Build authenticated remote URL using stored GitHub PAT if available
    repo_url = project.repository_url
    if repo_url and hasattr(project, "github_token") and project.github_token:
        # Embed token: https://TOKEN@github.com/owner/repo.git
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(repo_url)
        auth_url = urlunparse(parsed._replace(netloc=f"{project.github_token}@{parsed.netloc}"))
        repo_url = auth_url

    # Set up remote URL
    if repo_url:
        try:
            remote_chk = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=str(repo_path), capture_output=True, text=True, timeout=5
            )
            if remote_chk.returncode != 0:
                subprocess.run(
                    ["git", "remote", "add", remote, repo_url],
                    cwd=str(repo_path), capture_output=True, text=True, timeout=5
                )
            else:
                subprocess.run(
                    ["git", "remote", "set-url", remote, repo_url],
                    cwd=str(repo_path), capture_output=True, text=True, timeout=5
                )
        except Exception:
            pass

    # Ensure local branch is renamed to target_branch (e.g. master -> main)
    try:
        subprocess.run(["git", "branch", "-M", target_branch], cwd=str(repo_path), capture_output=True, timeout=5)
    except Exception:
        pass

    try:
        result = subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent", "push", "-u", remote, f"HEAD:{target_branch}"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or result.stdout.strip()
            if "fetch first" in stderr or "non-fast-forward" in stderr or "rejected" in stderr or "unrelated" in stderr:
                pull_res = subprocess.run(
                    ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent",
                     "pull", remote, target_branch, "--allow-unrelated-histories", "--no-edit"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                retry_push = subprocess.run(
                    ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent", "push", "-u", remote, f"HEAD:{target_branch}"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if retry_push.returncode == 0:
                    return ApiResponse(success=True, message="Pushed to GitHub successfully.", data={"output": retry_push.stdout.strip()})

                # Fallback: force push for initial sync
                force_push = subprocess.run(
                    ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent", "push", "-u", remote, f"HEAD:{target_branch}", "--force"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if force_push.returncode == 0:
                    return ApiResponse(success=True, message="Pushed to GitHub successfully.", data={"output": force_push.stdout.strip()})

            return ApiResponse(
                success=False,
                message=stderr or "Git push failed.",
                data={},
            )
        return ApiResponse(success=True, message="Pushed to GitHub successfully.", data={"output": result.stdout.strip()})
    except Exception as e:
        return ApiResponse(success=False, message=f"Git push errored: {e}", data={})


# ---------------------------------------------------------------------------
# Git log
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/log", response_model=ApiResponse)
def git_log(
    project_id: str,
    n: int = 20,
    service: ProjectService = Depends(get_project_service),
):
    """Return recent commits as a list."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ApiResponse(success=True, message="No git repo", data=[])

    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--pretty=format:%H|%an|%ae|%ar|%s"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        commits = []
        for line in result.stdout.splitlines():
            parts = line.split("|", 4)
            if len(parts) == 5:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                })
        return ApiResponse(success=True, message="Success", data=commits)
    except Exception as e:
        return ApiResponse(success=True, message=f"git log failed: {e}", data=[])


# ---------------------------------------------------------------------------
# Git diff
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/diff", response_model=ApiResponse)
def git_diff(
    project_id: str,
    path: Optional[str] = None,
    service: ProjectService = Depends(get_project_service),
):
    """Return unified diff for unstaged/staged changes."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ApiResponse(success=True, message="No git repo", data="")

    try:
        cmd = ["git", "diff", "HEAD"]
        if path:
            cmd.append(path)
        result = subprocess.run(
            cmd,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return ApiResponse(success=True, message="Success", data=result.stdout)
    except Exception as e:
        return ApiResponse(success=True, message=f"git diff failed: {e}", data="")


# ---------------------------------------------------------------------------
# Git rollback
# ---------------------------------------------------------------------------

class _RollbackBody(_PydanticBase):
    commit_hash: Optional[str] = None


@router.post("/{project_id}/git/rollback", response_model=ApiResponse)
def git_rollback(
    project_id: str,
    body: _RollbackBody = _RollbackBody(),
    service: ProjectService = Depends(get_project_service),
):
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    target = body.commit_hash or "HEAD"

    try:
        result = subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent",
             "revert", "--no-edit", target],
            cwd=str(repo_path),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            fb = subprocess.run(
                ["git", "reset", "--hard", f"{target}~1"],
                cwd=str(repo_path), capture_output=True, text=True, timeout=15,
            )
            if fb.returncode != 0:
                return ApiResponse(success=False, message=result.stderr.strip() or "Rollback failed.", data={})
        return ApiResponse(success=True, message="Rolled back successfully.", data={"output": result.stdout.strip()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Git revert single file (restore to HEAD)
# ---------------------------------------------------------------------------

class _RevertFileBody(_PydanticBase):
    path: str


@router.post("/{project_id}/git/revert-file", response_model=ApiResponse)
def git_revert_file(
    project_id: str,
    body: _RevertFileBody,
    service: ProjectService = Depends(get_project_service),
):
    """Restore a single file to its last committed state (git checkout HEAD -- <path>)."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    target = (repo_path / body.path).resolve()
    if not str(target).startswith(str(repo_path.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    try:
        result = subprocess.run(
            ["git", "checkout", "HEAD", "--", body.path],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            # File may be untracked (no HEAD version) — just report
            return ApiResponse(
                success=False,
                message=result.stderr.strip() or "Could not revert file (no committed version?)",
                data={},
            )
        # Read the restored content to send back to the frontend
        try:
            restored_content = target.read_text(encoding="utf-8")
        except Exception:
            restored_content = ""
        return ApiResponse(
            success=True,
            message="File reverted to HEAD.",
            data={"path": body.path, "content": restored_content},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Git file content at HEAD
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/file", response_model=ApiResponse)
def git_file_at_head(
    project_id: str,
    path: str,
    service: ProjectService = Depends(get_project_service),
):
    """Return the content of a file at git HEAD (for diff viewer original side)."""
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ApiResponse(success=False, message="No git repo", data="")

    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{path}"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return ApiResponse(success=False, message="File not in HEAD", data="")
        return ApiResponse(success=True, message="Success", data=result.stdout)
    except Exception as e:
        return ApiResponse(success=False, message=str(e), data="")