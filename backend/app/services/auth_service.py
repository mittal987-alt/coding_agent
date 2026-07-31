from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import Settings
from app.services.base import BaseService
from app.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    ValidationError,
)
class AuthService(BaseService):
    """
    Handles user authentication, authorization,
    JWT management and account lifecycle.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ) -> None:

        super().__init__(
            settings=settings,
            container=container,
        )

        self.password_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            deprecated="auto",
        )
    def hash_password(
        self,
        password: str,
    ) -> str:

        return self.password_context.hash(password)
    def verify_password(
        self,
        plain: str,
        hashed: str,
    ) -> bool:

        return self.password_context.verify(
            plain,
            hashed,
        )
    def create_access_token(
        self,
        user_id: str,
        role: str,
    ) -> str:

        expire = datetime.now(UTC) + timedelta(
            minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        payload = {
            "sub": user_id,
            "role": role,
            "exp": expire,
            "type": "access",
        }

        return jwt.encode(
            payload,
            self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
        )
    def create_refresh_token(
        self,
        user_id: str,
    ) -> str:

        expire = datetime.now(UTC) + timedelta(
            days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS,
        )

        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "refresh",
        }

        return jwt.encode(
            payload,
            self.settings.JWT_SECRET,
            algorithm=self.settings.JWT_ALGORITHM,
        )
    def decode_token(
        self,
        token: str,
    ) -> dict:

        try:

            return jwt.decode(
                token,
                self.settings.JWT_SECRET,
                algorithms=[
                    self.settings.JWT_ALGORITHM,
                ],
            )

        except JWTError as exc:
            raise AuthenticationError(
                "Invalid authentication token."
            ) from exc
    async def register(
        self,
        *,
        name: str,
        email: str,
        password: str,
    ):

        users = self.resolve("user_repository")

        existing = await users.get_by_email(email)

        if existing:
            raise ConflictError(
                "Email already registered."
            )

        hashed = self.hash_password(password)

        user = await users.create(
            name=name,
            email=email,
            password_hash=hashed,
        )

        await self.publish(
            "user.registered",
            {
                "user_id": user.id,
            },
        )

        return user
    async def login(
        self,
        *,
        email: str,
        password: str,
    ):

        users = self.resolve("user_repository")

        user = await users.get_by_email(email)

        if user is None:
            raise AuthenticationError(
                "Invalid credentials."
            )

        if not self.verify_password(
            password,
            user.password_hash,
        ):
            raise AuthenticationError(
                "Invalid credentials."
            )

        access = self.create_access_token(
            user.id,
            user.role,
        )

        refresh = self.create_refresh_token(
            user.id,
        )

        await self.log_action(
            action="login",
            user=user.id,
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
            "user": user,
        }
    async def refresh(
        self,
        refresh_token: str,
    ):

        payload = self.decode_token(
            refresh_token,
        )

        if payload["type"] != "refresh":
            raise AuthenticationError(
                "Invalid refresh token."
            )

        users = self.resolve("user_repository")

        user = await users.get(
            payload["sub"],
        )

        return {
            "access_token": self.create_access_token(
                user.id,
                user.role,
            )
        }
    async def change_password(
        self,
        *,
        user_id: str,
        current_password: str,
        new_password: str,
    ):

        users = self.resolve("user_repository")

        user = await users.get(user_id)

        if not self.verify_password(
            current_password,
            user.password_hash,
        ):
            raise ValidationError(
                "Current password is incorrect."
            )

        await users.update_password(
            user.id,
            self.hash_password(
                new_password,
            ),
        )

        await self.log_action(
            action="password_changed",
            user=user.id,
        )

        return True
    async def require_role(
        self,
        role: str,
        current_role: str,
    ):

        if role != current_role:
            raise AuthorizationError(
                "Permission denied."
            )
    async def logout(
        self,
        user_id: str,
    ):

        await self.log_action(
            action="logout",
            user=user_id,
        )

        return True
    async def forgot_password(
        self,
        email: str,
    ):

        await self.publish(
            "password.reset.requested",
            {
                "email": email,
            },
        )

        return True
    async def verify_email(
        self,
        token: str,
    ):

        payload = self.decode_token(token)

        users = self.resolve("user_repository")

        await users.verify_email(
            payload["sub"],
        )

        return True
    async def health_check(self):

        return {
            "service": "AuthService",
            "healthy": True,
            "jwt": True,
            "password_hashing": True,
        }