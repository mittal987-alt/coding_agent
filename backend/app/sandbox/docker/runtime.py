# Runtime module
import docker

from .containers import ContainerManager
from .images import ImageManager


class DockerRuntime:

    def __init__(self):

        self.client = docker.from_env()

        self.images = ImageManager(self.client)

        self.containers = ContainerManager(
            self.client
        )