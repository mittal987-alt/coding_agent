from pathlib import Path
import json
import shutil
from datetime import datetime
from typing import Dict, Any


class WorkspaceManager:
    """
    Handles all workspace operations.

    Workspace Structure:

    storage/
        workspaces/
            {project_id}/
                repository/
                uploads/
                vectorstore/
                memory/
                logs/
                cache/
                terminal/
                tasks/
                metadata.json
    """

    BASE_PATH = Path("storage")
    WORKSPACE_PATH = BASE_PATH / "workspaces"

    def __init__(self):
        self.WORKSPACE_PATH.mkdir(
            parents=True,
            exist_ok=True,
        )

    # -----------------------------------
    # Path Helpers
    # -----------------------------------

    def workspace_path(self, project_id: int) -> Path:
        return self.WORKSPACE_PATH / str(project_id)

    def repository_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "repository"

    def uploads_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "uploads"

    def vectorstore_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "vectorstore"

    def memory_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "memory"

    def logs_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "logs"

    def cache_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "cache"

    def terminal_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "terminal"

    def tasks_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "tasks"

    def metadata_path(self, project_id: int) -> Path:
        return self.workspace_path(project_id) / "metadata.json"

    # -----------------------------------
    # Workspace Creation
    # -----------------------------------

    def create_workspace(
        self,
        project_id: int,
        project_name: str,
    ):

        folders = [
            self.repository_path(project_id),
            self.uploads_path(project_id),
            self.vectorstore_path(project_id),
            self.memory_path(project_id),
            self.logs_path(project_id),
            self.cache_path(project_id),
            self.terminal_path(project_id),
            self.tasks_path(project_id),
        ]

        for folder in folders:
            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

        metadata = {
            "project_id": project_id,
            "project_name": project_name,
            "status": "CREATED",
            "language": None,
            "framework": None,
            "indexed": False,
            "embedding_model": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.save_metadata(
            project_id,
            metadata,
        )

    # -----------------------------------
    # Metadata
    # -----------------------------------

    def load_metadata(
        self,
        project_id: int,
    ) -> Dict[str, Any]:

        metadata_file = self.metadata_path(project_id)

        if not metadata_file.exists():
            raise FileNotFoundError(
                "Metadata not found."
            )

        with open(metadata_file, "r") as f:
            return json.load(f)

    def save_metadata(
        self,
        project_id: int,
        metadata: Dict[str, Any],
    ):

        metadata["updated_at"] = datetime.utcnow().isoformat()

        with open(
            self.metadata_path(project_id),
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                metadata,
                f,
                indent=4,
            )

    def update_metadata(
        self,
        project_id: int,
        **kwargs,
    ):

        metadata = self.load_metadata(project_id)

        metadata.update(kwargs)

        self.save_metadata(
            project_id,
            metadata,
        )

    # -----------------------------------
    # Delete Workspace
    # -----------------------------------

    def delete_workspace(
        self,
        project_id: int,
    ):

        workspace = self.workspace_path(project_id)

        if workspace.exists():
            shutil.rmtree(workspace)