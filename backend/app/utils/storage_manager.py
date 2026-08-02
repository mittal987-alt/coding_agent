from pathlib import Path
import shutil


class StorageManager:
    """
    Handles all project storage operations.
    """

    # Anchor storage to this file's location, not the process's current
    # working directory. A relative Path("storage") would resolve
    # differently depending on where uvicorn was launched from (repo root
    # vs backend/ vs an IDE run config), which could make project storage
    # appear to "move" or point at the wrong folder across restarts.
    BASE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"
    PROJECTS_DIR = BASE_DIR / "projects"

    def __init__(self):
        self.PROJECTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    def project_path(self, project_id: int) -> Path:
        return self.PROJECTS_DIR / str(project_id)

    def repository_path(self, project_id: int) -> Path:
        return self.project_path(project_id) / "repository"

    def upload_path(self, project_id: int) -> Path:
        return self.project_path(project_id) / "uploads"

    def vectorstore_path(self, project_id: int) -> Path:
        return self.project_path(project_id) / "vectorstore"

    def logs_path(self, project_id: int) -> Path:
        return self.project_path(project_id) / "logs"

    def temp_path(self, project_id: int) -> Path:
        return self.project_path(project_id) / "temp"

    def create_workspace(self, project_id: int):
        """
        Create project workspace.
        """

        folders = [
            self.repository_path(project_id),
            self.upload_path(project_id),
            self.vectorstore_path(project_id),
            self.logs_path(project_id),
            self.temp_path(project_id),
        ]

        for folder in folders:
            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

    def delete_workspace(self, project_id: int):
        """
        Delete entire project workspace.
        """

        workspace = self.project_path(project_id)

        if workspace.exists():
            shutil.rmtree(workspace)