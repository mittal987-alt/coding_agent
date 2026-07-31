class ArtifactRegistry:

    def __init__(self):

        self.artifacts = {}

    def register(

        self,

        artifact,

    ):

        self.artifacts[

            artifact.id

        ] = artifact

    def get(

        self,

        artifact_id,

    ):

        return self.artifacts.get(

            artifact_id

        )

    def list(

        self,

        execution_id,

    ):

        return [

            a

            for a in self.artifacts.values()

            if a.execution_id

            == execution_id

        ]