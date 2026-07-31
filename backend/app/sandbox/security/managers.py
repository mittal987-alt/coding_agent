class SecurityManager:

    def __init__(

        self,

        validators,

    ):

        self.validators = validators

    async def validate(

        self,

        request,

    ):

        for validator in self.validators:

            result = await validator.validate(

                request

            )

            if result.decision != "allow":

                return result

        return SecurityResult(

            decision="allow"

        )