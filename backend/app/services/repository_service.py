from pathlib import Path
import shutil

from fastapi import UploadFile

from app.utils.storage_manager import StorageManager
from app.utils.zip_manager import ZipManager


class RepositoryService:

    def __init__(self):

        self.storage = StorageManager()

    async def upload_zip(
        self,
        project,
        file: UploadFile,
    ):

        uploads = self.storage.upload_path(project.id)

        uploads.mkdir(
            parents=True,
            exist_ok=True,
        )

        zip_path = uploads / file.filename

        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        ZipManager.validate_zip(zip_path)

        repository = self.storage.repository_path(
            project.id
        )

        repository.mkdir(
            parents=True,
            exist_ok=True,
        )

        ZipManager.extract(
            zip_path,
            repository,
        )

        ZipManager.delete(zip_path)

        return repository