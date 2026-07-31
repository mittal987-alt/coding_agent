from pathlib import Path

from .models import FileInfo


class MetadataService:

    def info(

        self,

        path: Path,

    ):

        stat = path.stat()

        return FileInfo(

            path=str(path),

            size=stat.st_size,

            is_file=path.is_file(),

            is_directory=path.is_dir(),

            modified_time=stat.st_mtime,

        )