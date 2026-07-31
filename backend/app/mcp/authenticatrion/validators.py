class ScopeValidator:

    def validate(

        self,

        credentials,

        required,

    ):

        missing = [

            scope

            for scope in required

            if scope not in credentials.scopes

        ]

        if missing:

            raise PermissionError(

                f"Missing scopes: {missing}"

            )