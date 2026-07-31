class CapabilityRegistry:

    def __init__(self):

        self.capabilities = {}

    def register(

        self,

        capability,

    ):

        self.capabilities[

            capability.name

        ] = capability

    def get(

        self,

        name,

    ):

        return self.capabilities.get(name)

    def list(self):

        return list(

            self.capabilities.values()

        )