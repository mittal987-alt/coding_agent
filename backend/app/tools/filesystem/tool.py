from pathlib import Path

from app.tools.base import BaseTool
from app.tools.base import ToolResult

from .validator import PathValidator
from .reader import FileReader
from .writer import FileWriter
from .search import FileSearcher
from .metadata import MetadataService


class FilesystemTool(BaseTool):

    name = "filesystem"

    description = "Safe workspace file operations."

    def __init__(

        self,

        workspace: Path,

    ):

        self.validator = PathValidator(

            workspace

        )

        self.reader = FileReader()

        self.writer = FileWriter()

        self.searcher = FileSearcher()

        self.metadata = MetadataService()

    async def execute(

        self,

        action: str,

        **kwargs,

    ) -> ToolResult:

        if action == "read":

            path = self.validator.validate(

                kwargs["path"]

            )

            return ToolResult(

                success=True,

                output=self.reader.read(

                    path

                ),

            )

        raise NotImplementedError(
            f"Unknown action: {action}"
        )