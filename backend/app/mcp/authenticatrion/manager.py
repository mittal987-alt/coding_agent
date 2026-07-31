from .models import AuthenticationType

from .providers import (

    APIKeyProvider,

    BearerProvider,

    OAuthProvider,

    BasicProvider,

)


class AuthenticationManager:

    def __init__(self):

        self.providers = {

            AuthenticationType.API_KEY:

                APIKeyProvider(),

            AuthenticationType.BEARER:

                BearerProvider(),

            AuthenticationType.OAUTH2:

                OAuthProvider(),

            AuthenticationType.BASIC:

                BasicProvider(),

        }

    async def authenticate(

        self,

        credentials,

    ):

        provider = self.providers[

            credentials.authentication_type

        ]

        return await provider.authenticate(

            credentials

        )