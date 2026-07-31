from pathlib import Path


class PathValidator:

    def __init__(

        self,

        workspace: Path,

    ):

        self.workspace = workspace.resolve()

    def validate(

        self,

        path: str,

    ) -> Path:

        target = (

            self.workspace / path

        ).resolve()

        if not str(target).startswith(

            str(self.workspace)

        ):

            raise PermissionError(

                "Path escapes workspace."

            )

        return target