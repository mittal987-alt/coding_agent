import time


class OAuthManager:

    async def refresh_if_needed(

        self,

        credentials,

    ):

        if (

            credentials.expires_at

            and credentials.expires_at

            < time.time()

        ):

            raise NotImplementedError(

                "Refresh flow."

            )

        return credentials