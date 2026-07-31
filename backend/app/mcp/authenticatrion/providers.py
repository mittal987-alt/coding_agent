from enum import Enum

from pydantic import BaseModel


class AuthenticationType(str, Enum):

    API_KEY = "api_key"

    BEARER = "bearer"

    BASIC = "basic"

    OAUTH2 = "oauth2"

    MTLS = "mtls"


class Credentials(BaseModel):

    authentication_type: AuthenticationType

    value: str

    expires_at: float | None = None

    scopes: list[str] = []


class AuthenticationResult(BaseModel):

    headers: dict[str, str] = {}

    authenticated: bool