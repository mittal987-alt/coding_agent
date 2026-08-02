import logging
import re
import subprocess
import unicodedata
import uuid
from pathlib import Path

from app.models.project import Project
from app.models.workspace import Workspace
from app.repositories.project_repository import ProjectRepository
from app.utils.storage_manager import StorageManager

logger = logging.getLogger(__name__)
storage = StorageManager()

SKIP_DIR_NAMES = {".git", "node_modules", "__pycache__", ".venv", "venv", ".next"}


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)


def _run_git(args: list[str], cwd: Path) -> None:
    """Run a git command in `cwd`, logging (not raising) on failure so a git
    hiccup never blocks the actual folder upload from succeeding."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.warning(
                "git %s failed in %s: %s", " ".join(args), cwd, result.stderr.strip()
            )
    except Exception as e:
        logger.warning("git %s errored in %s: %s", " ".join(args), cwd, e)


class ProjectService:

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(self, project_in):
        base_slug = _slugify(project_in.name)
        slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"

        project = Project(
            name=project_in.name,
            slug=slug,
            repository_url=project_in.repository_url,
            language=project_in.language,
            framework=project_in.framework,
        )
        project = self.repository.create(project)

        # Set up local workspace storage + clone repo (best-effort)
        try:
            from git import Repo

            repo_path = storage.repository_path(str(project.id))

            repo_path.parent.mkdir(parents=True, exist_ok=True)

            if project.repository_url:
                Repo.clone_from(project.repository_url, str(repo_path))

                # Create the remaining folders after clone
                storage.upload_path(str(project.id)).mkdir(parents=True, exist_ok=True)
                storage.vectorstore_path(str(project.id)).mkdir(parents=True, exist_ok=True)
                storage.logs_path(str(project.id)).mkdir(parents=True, exist_ok=True)
                storage.temp_path(str(project.id)).mkdir(parents=True, exist_ok=True)

            workspace = Workspace(
                project_id=project.id,
                name=f"{project.name} Workspace",
                path=str(repo_path),
                current_branch=project.default_branch or "main",
            )
            project.workspaces.append(workspace)
            self.repository.commit()
        except Exception as e:
            logger.warning("Workspace setup failed for project %s: %s", project.id, e)
            # Clean up any partially-created workspace dir so retries don't collide
            try:
                storage.delete_workspace(str(project.id))
            except Exception:
                pass

        return project

    def save_uploaded_folder(self, project, entries):
        """
        Write an uploaded local folder into the project's repository path.

        entries: list of (relative_path: str, content: bytes) tuples,
        one per uploaded file, as sent by the "Add Folder" flow.
        """
        repo_path = storage.repository_path(str(project.id))
        repo_path.mkdir(parents=True, exist_ok=True)
        repo_root_resolved = repo_path.resolve()

        written = 0
        for rel_path, content in entries:
            parts = Path(rel_path).parts

            # Skip junk directories (node_modules, .git, venvs, build caches, etc.)
            if any(part in SKIP_DIR_NAMES for part in parts):
                continue

            target = (repo_path / rel_path).resolve()

            # Guard against path traversal from a malicious/odd relative path
            if not str(target).startswith(str(repo_root_resolved)):
                logger.warning("Skipped unsafe upload path: %s", rel_path)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            written += 1

        storage.upload_path(str(project.id)).mkdir(parents=True, exist_ok=True)
        storage.vectorstore_path(str(project.id)).mkdir(parents=True, exist_ok=True)
        storage.logs_path(str(project.id)).mkdir(parents=True, exist_ok=True)
        storage.temp_path(str(project.id)).mkdir(parents=True, exist_ok=True)

        # Initialize git for uploaded folders, since the frontend deliberately
        # strips any pre-existing .git directory before upload (to avoid
        # sending huge/broken git internals over multipart). Without this,
        # `git status`, `git remote -v`, etc. all fail with "not a git repository".
        # Safe to call repeatedly — `git init` is a no-op if .git already exists.
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            _run_git(["init"], cwd=repo_path)
            _run_git(["checkout", "-b", project.default_branch or "main"], cwd=repo_path)
            _run_git(["add", "-A"], cwd=repo_path)
            _run_git(
                ["-c", "user.email=agent@local", "-c", "user.name=AI Agent",
                 "commit", "-m", "Initial upload"],
                cwd=repo_path,
            )

        # Only attach a workspace if one doesn't already exist for this project
        if not project.workspaces:
            workspace = Workspace(
                project_id=project.id,
                name=f"{project.name} Workspace",
                path=str(repo_path),
                current_branch=project.default_branch or "main",
            )
            project.workspaces.append(workspace)

        self.repository.commit()

        logger.info("Uploaded %d files into project %s", written, project.id)
        return project

    def get_projects(self):
        return self.repository.get_all()

    def get_project(self, project_id):
        return self.repository.get_by_id(project_id)

    def delete_project(self, project):
        try:
            self.repository.delete(project)
            storage.delete_workspace(project.id)
        except Exception as e:
            logger.error("Failed to delete project %s: %s", project.id, e)
            raise