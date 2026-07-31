class ArtifactException(SandboxException):

    pass


class ArtifactStorageFailed(ArtifactException):

    pass


class ArtifactTooLarge(ArtifactException):

    pass