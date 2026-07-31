from pathlib import Path
import shutil


class WorkspaceCleanup:

    async def cleanup(

        self,

        workspace,

    ):

        shutil.rmtree(

            Path(workspace),

            ignore_errors=True,

        )