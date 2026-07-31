import logging
import re
import unicodedata
import uuid

from app.models.project import Project
from app.models.workspace import Workspace
from app.repositories.project_repository import ProjectRepository
from app.utils.storage_manager import StorageManager

logger = logging.getLogger(__name__)
storage = StorageManager()


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text)


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

                # Create the remaining fold ers after clone
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