from .base import SandboxException


class DockerException(SandboxException):

    pass


class ImageNotFound(DockerException):

    pass


class ContainerStartFailed(DockerException):

    pass


class ContainerTimeout(DockerException):

    pass


class ContainerOOM(DockerException):

    pass