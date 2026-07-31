# Lifecycle module
class LifecycleManager:

    def __init__(

        self,

        container,

    ):

        self.container = container

    def stop(self):

        self.container.stop()

    def remove(self):

        self.container.remove(force=True)