class CapabilityRanker:

    def rank(

        self,

        capabilities,

    ):

        return sorted(

            capabilities,

            key=lambda c: (

                c.version,

                c.name,

            ),

            reverse=True,

        )