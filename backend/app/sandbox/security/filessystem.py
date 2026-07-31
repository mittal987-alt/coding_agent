from pathlib import Path


class FilesystemValidator(

    BaseValidator,

):

    async def validate(

        self,

        request,

    ):

        path = Path(

            request.working_directory

        ).resolve()

        workspace = Path("/workspace").resolve()

        if workspace not in path.parents and path != workspace:

            return SecurityResult(

                decision=SecurityDecision.DENY,

                reason="Working directory outside sandbox",

            )

        return SecurityResult(

            decision=SecurityDecision.ALLOW,

        )