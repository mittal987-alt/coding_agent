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
# Full-repo text search  (Ctrl+Shift+F)
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

            # Skip dirs and binary-like files
            if file_path.is_dir():
                continue
            if any(part in _SKIP_DIRS for part in file_path.parts):
                continue
            if file_path.suffix.lower() in _BINARY_EXTS:
                continue

            # Skip large files (> 500 KB)
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
                    # Build a short preview with the match highlighted
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
# Search & Replace across files  (Ctrl+H)
# ---------------------------------------------------------------------------

class _ReplaceBody(_PydanticBase):
    search: str
    replace: str
    case_sensitive: bool = False


@router.post("/{project_id}/files/replace", response_model=ApiResponse)
def replace_in_files(
    project_id: str,
    body: _ReplaceBody,
    service: ProjectService = Depends(get_project_service),
):
    """Replace all occurrences of a search term across all text files."""
    import re as _re

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    if not body.search:
        return ApiResponse(success=False, message="Search term is required.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists():
        return ApiResponse(success=True, message="No repository", data={"replaced": 0, "files": []})

    modified_files: list[dict] = []
    total_replaced = 0
    flags = 0 if body.case_sensitive else _re.IGNORECASE
    pattern = _re.compile(_re.escape(body.search), flags)

    for file_path in repo_path.rglob("*"):
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
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            count = len(pattern.findall(content))
            if count > 0:
                new_content = pattern.sub(body.replace, content)
                file_path.write_text(new_content, encoding="utf-8")
                relative = str(file_path.relative_to(repo_path)).replace("\\", "/")
                modified_files.append({"path": relative, "count": count})
                total_replaced += count
        except Exception:
            pass

    return ApiResponse(
        success=True,
        message=f"Replaced {total_replaced} occurrence(s) in {len(modified_files)} file(s).",
        data={"replaced": total_replaced, "files": modified_files},
    )


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
# Git commit  (stage all + commit)
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
    import subprocess

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    try:
        # Stage all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", body.message],
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


# ---------------------------------------------------------------------------
# Git log  (recent commits)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/log", response_model=ApiResponse)
def git_log(
    project_id: str,
    n: int = 20,
    service: ProjectService = Depends(get_project_service),
):
    """Return recent commits as a list."""
    import subprocess

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
# Git diff  (unstaged changes for a file or all)
# ---------------------------------------------------------------------------

@router.get("/{project_id}/git/diff", response_model=ApiResponse)
def git_diff(
    project_id: str,
    path: str | None = None,
    service: ProjectService = Depends(get_project_service),
):
    """Return unified diff for unstaged/staged changes."""
    import subprocess

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
# Git branch management
# ---------------------------------------------------------------------------

class _BranchCreateBody(_PydanticBase):
    name: str


class _CheckoutBranchBody(_PydanticBase):
    branch: str


@router.get("/{project_id}/git/branches", response_model=ApiResponse)
def get_git_branches(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    """Return all local branches and the currently checked-out branch."""
    import subprocess
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        return ApiResponse(success=True, message="No git repo", data={"current": "main", "branches": ["main"]})

    try:
        current_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(repo_path), capture_output=True, text=True, timeout=10,
        )
        current = current_result.stdout.strip() or "HEAD"
        branches_result = subprocess.run(
            ["git", "branch"],
            cwd=str(repo_path), capture_output=True, text=True, timeout=10,
        )
        branches = [
            line.strip().lstrip("* ").strip()
            for line in branches_result.stdout.splitlines()
            if line.strip()
        ]
        return ApiResponse(success=True, message="Success", data={"current": current, "branches": branches})
    except Exception as e:
        return ApiResponse(success=True, message=f"Error: {e}", data={"current": "main", "branches": []})


@router.post("/{project_id}/git/branches", response_model=ApiResponse)
def create_git_branch(
    project_id: str,
    body: _BranchCreateBody,
    service: ProjectService = Depends(get_project_service),
):
    """Create and check out a new local branch."""
    import subprocess
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    result = subprocess.run(
        ["git", "checkout", "-b", body.name],
        cwd=str(repo_path), capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        return ApiResponse(success=False, message=result.stderr.strip() or "Failed to create branch.")
    return ApiResponse(success=True, message=f"Created and switched to branch '{body.name}'.")


@router.post("/{project_id}/git/checkout", response_model=ApiResponse)
def git_checkout_branch(
    project_id: str,
    body: _CheckoutBranchBody,
    service: ProjectService = Depends(get_project_service),
):
    """Switch to an existing local branch."""
    import subprocess
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    result = subprocess.run(
        ["git", "checkout", body.branch],
        cwd=str(repo_path), capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        return ApiResponse(success=False, message=result.stderr.strip() or "Checkout failed.")
    return ApiResponse(success=True, message=f"Switched to '{body.branch}'.")


@router.delete("/{project_id}/git/branches/{branch_name}", response_model=ApiResponse)
def delete_git_branch(
    project_id: str,
    branch_name: str,
    service: ProjectService = Depends(get_project_service),
):
    """Delete a local branch (must not be currently checked out)."""
    import subprocess
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    result = subprocess.run(
        ["git", "branch", "-d", branch_name],
        cwd=str(repo_path), capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        return ApiResponse(success=False, message=result.stderr.strip() or "Delete failed.")
    return ApiResponse(success=True, message=f"Branch '{branch_name}' deleted.")


# ---------------------------------------------------------------------------
# Project-scoped chat  (called directly by the workspace page)
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _PydanticBase
import subprocess as _subprocess


# ── Context helpers ────────────────────────────────────────────────────────

_SKIP_DIRS_CTX = {".git", "node_modules", "__pycache__", ".next", "dist", "build", ".venv", "venv"}
_TEXT_EXTS_CTX = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt",
    ".yaml", ".yml", ".toml", ".env", ".sh", ".html", ".css", ".rs", ".go",
}


def _build_file_tree(root: Path, prefix: str = "", depth: int = 0) -> str:
    """Return a compact ASCII tree of the repo."""
    if depth > 4:
        return ""
    lines: list[str] = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return ""
    for entry in entries:
        if entry.name in _SKIP_DIRS_CTX or entry.name.startswith("."):
            continue
        if entry.is_dir():
            lines.append(f"{prefix}📁 {entry.name}/")
            lines.append(_build_file_tree(entry, prefix + "  ", depth + 1))
        else:
            lines.append(f"{prefix}📄 {entry.name}")
    return "\n".join(l for l in lines if l)


def _recent_diff(repo_path: Path, max_chars: int = 3000) -> str:
    """Return a truncated `git diff HEAD` for recent changes."""
    try:
        result = _subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=str(repo_path), capture_output=True, text=True, timeout=10,
        )
        diff = result.stdout.strip()
        if len(diff) > max_chars:
            diff = diff[:max_chars] + "\n\n... (diff truncated)"
        return diff
    except Exception:
        return ""


def _files_mentioned(user_text: str, repo_path: Path) -> list[tuple[str, str]]:
    """Find files whose name appears in the user message and read them (up to 5)."""
    words = set(user_text.lower().split())
    found: list[tuple[str, str]] = []
    for fp in repo_path.rglob("*"):
        if fp.is_dir():
            continue
        if any(part in _SKIP_DIRS_CTX for part in fp.parts):
            continue
        if fp.suffix.lower() not in _TEXT_EXTS_CTX:
            continue
        if fp.name.lower() in words or fp.stem.lower() in words:
            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")
                if len(content) > 4000:
                    content = content[:4000] + "\n... (truncated)"
                found.append((str(fp.relative_to(repo_path)).replace("\\", "/"), content))
                if len(found) >= 5:
                    break
            except Exception:
                pass
    return found


def _build_context_prompt(repo_path: Path, user_message: str) -> str:
    """Assemble a system-level codebase context block."""
    sections: list[str] = []

    tree = _build_file_tree(repo_path)
    if tree:
        sections.append(f"## Repository structure\n```\n{tree}\n```")

    diff = _recent_diff(repo_path)
    if diff:
        sections.append(f"## Recent uncommitted changes (git diff HEAD)\n```diff\n{diff}\n```")

    mentioned = _files_mentioned(user_message, repo_path)
    for rel, content in mentioned:
        ext = rel.rsplit(".", 1)[-1] if "." in rel else ""
        sections.append(f"## File: {rel}\n```{ext}\n{content}\n```")

    if not sections:
        return ""

    header = (
        "You are an expert coding assistant with full access to the project repository below. "
        "Use this context to give precise, file-aware answers.\n\n"
    )
    return header + "\n\n".join(sections)


# ── Auto-git-commit helper ─────────────────────────────────────────────────

def _auto_commit(repo_path: Path, summary: str) -> None:
    """Stage all changes and commit them as an AI checkpoint."""
    if not (repo_path / ".git").exists():
        return
    try:
        # Configure identity if not already set (non-interactive envs)
        _subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent",
             "add", "-A"],
            cwd=str(repo_path), capture_output=True, timeout=15,
        )
        # Only commit if there are staged changes
        status = _subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(repo_path), capture_output=True, text=True, timeout=10,
        )
        if not status.stdout.strip():
            return  # nothing to commit
        msg = f"AI: {summary[:72]}"
        _subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent",
             "commit", "-m", msg],
            cwd=str(repo_path), capture_output=True, timeout=15,
        )
    except Exception:
        pass  # never block the response


# ── Plan-mode system prompt ────────────────────────────────────────────────

_PLAN_SYSTEM = """
You are an expert coding assistant in PLANNING MODE.
The user will ask you to perform a task. Instead of doing it, produce a PLAN ONLY.

Your response MUST follow this exact format — no prose before/after:

<!--PLAN-->
SUMMARY: One-sentence description of what you'll do.
STEPS:
- ACTION: <Create|Modify|Delete|Run|Other>  FILE: <path or N/A>  DETAIL: <brief description>
- ACTION: ...
<!--/PLAN-->

Do NOT write any code. Do NOT explain. Only output the plan block above.
"""

_EXECUTE_SYSTEM = """
You are an expert coding assistant in EXECUTION MODE.
The user approved the following plan. Now implement it exactly:

{plan}

Write clean, production-ready code. When you create or modify files, clearly state which file
you are writing to using a header like: `### File: path/to/file.ext`.
"""


class _ChatBody(_PydanticBase):
    messages: list[dict]
    model: str = "gpt-4o"
    temperature: float = 0.2
    require_plan: bool = False    # Feature 5: two-phase plan/execute
    approved_plan: str | None = None   # Feature 5: pass back approved plan


def _call_llm(model: str, messages: list[dict], temperature: float, api_key_override: str = "") -> str:
    """Call the appropriate LLM provider and return the reply string."""
    import os, httpx

    if "mistral" in model.lower():
        api_key = api_key_override or os.getenv("MISTRAL_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=503, detail="MISTRAL_API_KEY is not set.")
        resp = httpx.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": temperature},
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    if "gpt" in model.lower() or "openai" in model.lower():
        api_key = api_key_override or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not set.")
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": messages, "temperature": temperature},
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    if "claude" in model.lower() or "anthropic" in model.lower():
        import os, httpx
        api_key = api_key_override or os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY is not set.")
        system_msgs = [m["content"] for m in messages if m.get("role") == "system"]
        chat_msgs = [m for m in messages if m.get("role") != "system"]
        payload: dict = {"model": model, "max_tokens": 4096, "messages": chat_msgs}
        if system_msgs:
            payload["system"] = "\n".join(system_msgs)
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01",
                     "Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    raise HTTPException(status_code=400, detail=f"Unsupported model '{model}'.")


@router.post("/{project_id}/chat", response_model=ApiResponse)
def project_chat(
    project_id: str,
    body: _ChatBody,
    service: ProjectService = Depends(get_project_service),
):
    """
    LLM chat endpoint with:
    - Feature 5: Two-phase plan/execute (require_plan / approved_plan)
    - Feature 6: Auto-commit after each AI turn
    - Feature 8: Codebase context injection
    """
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    model = project.llm_model or body.model or "gpt-4o"
    repo_path = storage.repository_path(project.id)
    messages = [m for m in body.messages]   # shallow copy

    # ── Feature 8: inject codebase context ──────────────────────────────────
    user_text = next(
        (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
    )
    if repo_path.exists():
        ctx = _build_context_prompt(repo_path, user_text)
        if ctx:
            messages = [{"role": "system", "content": ctx}] + messages

    # ── Feature 5: Plan mode ─────────────────────────────────────────────────
    if body.require_plan:
        plan_messages = [{"role": "system", "content": _PLAN_SYSTEM}] + [
            m for m in messages if m.get("role") != "system"
        ]
        try:
            plan_reply = _call_llm(model, plan_messages, body.temperature)
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
        return ApiResponse(
            success=True,
            message="plan",
            data={"message": plan_reply, "model": model, "modified_files": [], "phase": "plan"},
        )

    # ── Feature 5: Execution with approved plan ──────────────────────────────
    if body.approved_plan:
        exec_system = _EXECUTE_SYSTEM.format(plan=body.approved_plan)
        messages = [{"role": "system", "content": exec_system}] + [
            m for m in messages if m.get("role") != "system"
        ]

    # ── Normal / execution call ───────────────────────────────────────────────
    try:
        reply = _call_llm(model, messages, body.temperature)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    # ── Feature 6: Auto-commit after AI turn ─────────────────────────────────
    if repo_path.exists():
        first_line = reply.split("\n")[0].strip()
        _auto_commit(repo_path, first_line or "agent turn")

    return ApiResponse(
        success=True,
        message="OK",
        data={"message": reply, "model": model, "modified_files": [], "phase": "execute"},
    )


# ---------------------------------------------------------------------------
# SSE streaming chat endpoint  (streams token-by-token to the frontend)
# ---------------------------------------------------------------------------

@router.post("/{project_id}/chat/stream")
async def project_chat_stream(
    project_id: str,
    body: _ChatBody,
    service: ProjectService = Depends(get_project_service),
):
    """
    Streaming SSE version of project_chat.
    Emits: {"type": "token"|"activity"|"done"|"error", ...}
    Also parses '### File:' headers in the LLM response and writes those files to disk.
    """
    import os as _os
    import json as _json
    import re as _re
    import httpx as _httpx
    from fastapi.responses import StreamingResponse

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    model = project.llm_model or body.model or "gpt-4o"
    repo_path = storage.repository_path(project.id)
    messages = list(body.messages)

    user_text = next(
        (m["content"] for m in reversed(messages)
         if m.get("role") == "user" and isinstance(m.get("content"), str)),
        "",
    )
    if repo_path.exists():
        ctx = _build_context_prompt(repo_path, user_text)
        if ctx:
            messages = [{"role": "system", "content": ctx}] + messages

    # Plan mode — return plan in one shot, then done
    if body.require_plan:
        plan_messages = [{"role": "system", "content": _PLAN_SYSTEM}] + [
            m for m in messages if m.get("role") != "system"
        ]
        try:
            plan_reply = _call_llm(model, plan_messages, body.temperature)
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))

        async def _plan_gen():
            yield f"data: {_json.dumps({'type': 'token', 'content': plan_reply})}\n\n"
            yield f"data: {_json.dumps({'type': 'done', 'modified_files': [], 'phase': 'plan'})}\n\n"

        return StreamingResponse(
            _plan_gen(), media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    if body.approved_plan:
        exec_system = _EXECUTE_SYSTEM.format(plan=body.approved_plan)
        messages = [{"role": "system", "content": exec_system}] + [
            m for m in messages if m.get("role") != "system"
        ]

    def _parse_and_write_files(text: str, rpath: Path) -> list[str]:
        """Parse ### File: headers from LLM response and write files to disk."""
        written: list[str] = []
        parts = _re.split(r'^### File:\s*(.+)$', text, flags=_re.MULTILINE)
        i = 1
        while i < len(parts) - 1:
            fname = parts[i].strip()
            block = parts[i + 1]
            code_match = _re.search(r'```(?:\w+)?\n(.*?)```', block, _re.DOTALL)
            content = code_match.group(1) if code_match else block.strip()
            if fname and content:
                target = (rpath / fname).resolve()
                if str(target).startswith(str(rpath.resolve())):
                    try:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text(content, encoding="utf-8")
                        written.append(fname)
                    except Exception:
                        pass
            i += 2
        return written

    async def generate():
        full_response = ""
        seen_files: set[str] = set()

        yield f"data: {_json.dumps({'type': 'activity', 'step': 'Thinking…'})}\n\n"

        try:
            if "mistral" in model.lower():
                api_key = _os.getenv("MISTRAL_API_KEY", "")
                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.mistral.ai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": messages, "temperature": body.temperature, "stream": True},
                    ) as resp:
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            raw = line[6:]
                            if raw.strip() == "[DONE]":
                                break
                            try:
                                chunk = _json.loads(raw)
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    full_response += token
                                    yield f"data: {_json.dumps({'type': 'token', 'content': token})}\n\n"
                                    for ln in full_response.split("\n"):
                                        if ln.startswith("### File:"):
                                            fn = ln.replace("### File:", "").strip()
                                            if fn and fn not in seen_files:
                                                seen_files.add(fn)
                                                yield f"data: {_json.dumps({'type': 'activity', 'step': f'Writing {fn}'})}\n\n"
                            except Exception:
                                pass

            elif "gpt" in model.lower() or "openai" in model.lower():
                api_key = _os.getenv("OPENAI_API_KEY", "")
                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.openai.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"model": model, "messages": messages, "temperature": body.temperature, "stream": True},
                    ) as resp:
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            raw = line[6:]
                            if raw.strip() == "[DONE]":
                                break
                            try:
                                chunk = _json.loads(raw)
                                token = chunk["choices"][0]["delta"].get("content", "")
                                if token:
                                    full_response += token
                                    yield f"data: {_json.dumps({'type': 'token', 'content': token})}\n\n"
                                    for ln in full_response.split("\n"):
                                        if ln.startswith("### File:"):
                                            fn = ln.replace("### File:", "").strip()
                                            if fn and fn not in seen_files:
                                                seen_files.add(fn)
                                                yield f"data: {_json.dumps({'type': 'activity', 'step': f'Writing {fn}'})}\n\n"
                            except Exception:
                                pass

            elif "claude" in model.lower() or "anthropic" in model.lower():
                api_key = _os.getenv("ANTHROPIC_API_KEY", "")
                sys_msgs = [m["content"] for m in messages if m.get("role") == "system"]
                chat_msgs = [m for m in messages if m.get("role") != "system"]
                payload: dict = {"model": model, "max_tokens": 4096, "messages": chat_msgs, "stream": True}
                if sys_msgs:
                    payload["system"] = "\n".join(sys_msgs)
                async with _httpx.AsyncClient(timeout=90) as client:
                    async with client.stream(
                        "POST",
                        "https://api.anthropic.com/v1/messages",
                        headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
                        json=payload,
                    ) as resp:
                        async for line in resp.aiter_lines():
                            if not line.startswith("data: "):
                                continue
                            try:
                                data = _json.loads(line[6:])
                                if data.get("type") == "content_block_delta":
                                    token = data.get("delta", {}).get("text", "")
                                    if token:
                                        full_response += token
                                        yield f"data: {_json.dumps({'type': 'token', 'content': token})}\n\n"
                                        for ln in full_response.split("\n"):
                                            if ln.startswith("### File:"):
                                                fn = ln.replace("### File:", "").strip()
                                                if fn and fn not in seen_files:
                                                    seen_files.add(fn)
                                                    yield f"data: {_json.dumps({'type': 'activity', 'step': f'Writing {fn}'})}\n\n"
                            except Exception:
                                pass

            else:
                # Fallback: non-streaming call
                reply = _call_llm(model, messages, body.temperature)
                full_response = reply
                yield f"data: {_json.dumps({'type': 'token', 'content': reply})}\n\n"

        except Exception as exc:
            yield f"data: {_json.dumps({'type': 'error', 'message': str(exc)})}\n\n"
            return

        # Parse ### File: headers and write files to disk
        written = _parse_and_write_files(full_response, repo_path)
        if not written:
            written = list(seen_files)

        # Auto-commit
        if repo_path.exists():
            first_line = full_response.split("\n")[0].strip()
            _auto_commit(repo_path, first_line or "agent turn")

        yield f"data: {_json.dumps({'type': 'done', 'modified_files': written, 'phase': 'execute'})}\n\n"

    return StreamingResponse(
        generate(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# Feature 6 — Git rollback  (revert last AI commit)
# ---------------------------------------------------------------------------

class _RollbackBody(_PydanticBase):
    commit_hash: str | None = None   # if None, reverts HEAD


@router.post("/{project_id}/git/rollback", response_model=ApiResponse)
def git_rollback(
    project_id: str,
    body: _RollbackBody = _RollbackBody(),
    service: ProjectService = Depends(get_project_service),
):
    """
    Revert the last AI commit (or a specific commit by hash).
    Uses `git revert --no-edit` so it creates a new revert commit safely.
    Falls back to `git reset --hard` for the initial commit edge case.
    """
    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists() or not (repo_path / ".git").exists():
        raise HTTPException(status_code=400, detail="No git repository found.")

    target = body.commit_hash or "HEAD"

    try:
        result = _subprocess.run(
            ["git", "-c", "user.email=agent@local", "-c", "user.name=AI Agent",
             "revert", "--no-edit", target],
            cwd=str(repo_path),
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            # Some commits can't be reverted (e.g. initial commit). Try hard reset as fallback.
            fb = _subprocess.run(
                ["git", "reset", "--hard", f"{target}~1"],
                cwd=str(repo_path), capture_output=True, text=True, timeout=15,
            )
            if fb.returncode != 0:
                return ApiResponse(success=False, message=result.stderr.strip() or "Rollback failed.", data={})
        return ApiResponse(success=True, message="Rolled back successfully.", data={"output": result.stdout.strip()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Feature 7 — Run / Build / Test
# ---------------------------------------------------------------------------

def _detect_run_command(repo_path: Path) -> tuple[list[str], str]:
    """Auto-detect how to run/build/test the project."""
    pkg = repo_path / "package.json"
    if pkg.exists():
        try:
            import json as _json
            data = _json.loads(pkg.read_text())
            scripts = data.get("scripts", {})
            if "dev" in scripts:
                return ["npm", "run", "dev"], "Node.js (npm run dev)"
            if "start" in scripts:
                return ["npm", "run", "start"], "Node.js (npm run start)"
            if "build" in scripts:
                return ["npm", "run", "build"], "Node.js (npm run build)"
        except Exception:
            pass
        return ["npm", "install"], "Node.js (npm install)"

    if (repo_path / "pyproject.toml").exists() or (repo_path / "setup.py").exists():
        if (repo_path / "pytest.ini").exists() or (repo_path / "tests").exists() or (repo_path / "test").exists():
            return ["python", "-m", "pytest", "--tb=short", "-v"], "Python (pytest)"
        return ["python", "-m", "pip", "install", "-e", "."], "Python (pip install -e .)"

    if (repo_path / "requirements.txt").exists():
        return ["python", "-m", "pytest", "--tb=short"], "Python (pytest)"

    if (repo_path / "Makefile").exists():
        return ["make"], "Make"

    if (repo_path / "go.mod").exists():
        return ["go", "build", "./..."], "Go (go build)"

    if (repo_path / "Cargo.toml").exists():
        return ["cargo", "build"], "Rust (cargo build)"

    return ["echo", "No run script detected. Please configure one in project settings."], "Unknown"


@router.post("/{project_id}/run", response_model=ApiResponse)
def run_project(
    project_id: str,
    service: ProjectService = Depends(get_project_service),
):
    """
    Detect the project type, run its dev/build/test command, and return a
    run_session_id that the frontend connects to via /ws/run/{run_session_id}.
    """
    import uuid as _uuid

    project = service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")

    repo_path = storage.repository_path(project.id)
    if not repo_path.exists():
        raise HTTPException(status_code=400, detail="Project has no repository files yet.")

    cmd, label = _detect_run_command(repo_path)
    run_id = str(_uuid.uuid4())

    # Store the pending run so the WebSocket handler can pick it up
    _pending_runs[run_id] = {"cmd": cmd, "cwd": str(repo_path), "label": label}

    return ApiResponse(
        success=True,
        message=f"Run session created: {label}",
        data={"run_id": run_id, "command": " ".join(cmd), "label": label},
    )


# In-memory store for pending run sessions (lightweight, process-local)
_pending_runs: dict[str, dict] = {}


def get_pending_run(run_id: str) -> dict | None:
    return _pending_runs.pop(run_id, None)