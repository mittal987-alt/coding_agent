from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import EmailStr, Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)

class UserResponse(TimestampSchema):
    """
    User information returned by the API.
    """

    id: str

    name: str

    email: EmailStr

    username: str | None = None

    avatar: str | None = None

    verified: bool = False

    role: Literal[
        "admin",
        "developer",
        "viewer",
    ] = "developer"

    active: bool = True


class LoginRequest(BaseSchema):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )
class TokenResponse(BaseSchema):

    access_token: str

    refresh_token: str

    token_type: str = "Bearer"

    expires_in: int
class LoginResponse(TokenResponse):

    user: UserResponse
class RegisterRequest(BaseSchema):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str
class RegisterResponse(BaseSchema):

    user: UserResponse

    verification_required: bool = True
class RefreshRequest(BaseSchema):

    refresh_token: str 
class LogoutResponse(BaseSchema):

    success: bool = True
class ChangePasswordRequest(BaseSchema):

    current_password: str

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str
class ForgotPasswordRequest(BaseSchema):

    email: EmailStr
class ResetPasswordRequest(BaseSchema):

    token: str

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    confirm_password: str
class VerifyEmailRequest(BaseSchema):

    token: str
class UserSession(BaseSchema):

    id: str

    device: str

    ip_address: str

    location: str | None = None

    created_at: datetime

    last_active: datetime
class UserProfile(UserResponse):

    bio: str | None = None

    company: str | None = None

    website: str | None = None

    github: str | None = None

    timezone: str | None = None

    language: str = "en"
class UpdateProfileRequest(BaseSchema):

    name: str | None = None

    avatar: str | None = None

    bio: str | None = None

    company: str | None = None

    website: str | None = None

    github: str | None = None

    timezone: str | None = None

    language: str | None = None
class ApiKeyResponse(BaseSchema):

    id: str

    name: str

    prefix: str

    created_at: datetime

    expires_at: datetime | None = None
class CreateApiKeyRequest(BaseSchema):

    name: str

    expires_in_days: int | None = Field(
        default=None,
        ge=1,
    )
class Permission(BaseSchema):

    name: str

    description: str

class RoleResponse(BaseSchema):

    name: str

    permissions: list[Permission]