class ResourceValidator(

    BaseValidator,

):

    MAX_TIMEOUT = 600

    async def validate(

        self,

        request,

    ):

        if request.timeout > self.MAX_TIMEOUT:

            return SecurityResult(

                decision=SecurityDecision.DENY,

                reason="Timeout exceeds policy",

            )

        return SecurityResult(

            decision=SecurityDecision.ALLOW,

        )