class ApprovalManager:

    async def check(

        self,

        tool,

    ):

        if getattr(

            tool,

            "requires_approval",

            False,

        ):

            raise PermissionError(

                "Approval required."

            )