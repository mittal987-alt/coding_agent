from pathlib import Path


class ArtifactCollector:

    async def collect(

        self,

        workspace,

        execution_id,

    ):

        artifacts = []

        for file in Path(workspace).rglob("*"):

            if file.is_file():

                artifacts.append(file)

        return artifacts