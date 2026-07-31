class ArtifactDetector:

    TYPES = {

        ".xml": "report",

        ".html": "documentation",

        ".apk": "binary",

        ".jar": "binary",

        ".log": "log",

        ".png": "screenshot",

        ".patch": "patch",

    }

    def detect(

        self,

        filename,

    ):

        suffix = filename.suffix.lower()

        return self.TYPES.get(

            suffix,

            "other",

        )