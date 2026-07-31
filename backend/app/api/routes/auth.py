#
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_container
from app.api.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter()

@router.post(
    "/login",
    response_model=LoginResponse,
)
async def login(
    request: LoginRequest,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    user = await auth.authenticate(

        email=request.email,

        password=request.password,
    )

    tokens = await auth.create_tokens(user)

    return LoginResponse(

        access_token=tokens.access_token,

        refresh_token=tokens.refresh_token,

        expires_in=tokens.expires_in,

        user=user,
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh(
    request: RefreshRequest,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    token = await auth.refresh(

        request.refresh_token,
    )

    return token
@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    return await auth.current_user()



@router.post("/logout")
async def logout(
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.logout()

    return {
        "success": True,
    }

@router.post("/register")
async def register(
    request,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    user = await auth.register(

        name=request.name,

        email=request.email,

        password=request.password,
    )

    return user

@router.post("/change-password")
async def change_password(
    request,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.change_password(

        current=request.current_password,

        new=request.new_password,
    )

    return {
        "success": True,
    }   

@router.post("/forgot-password")
async def forgot_password(
    email: str,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.send_reset_email(
        email,
    )

    return {
        "message": "Password reset email sent."
    }

@router.post("/reset-password")
async def reset_password(
    token: str,
    password: str,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.reset_password(

        token,

        password,
    )

    return {
        "success": True,
    }

@router.get("/verify-email")
async def verify_email(
    token: str,
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.verify_email(
        token,
    )

    return {
        "verified": True,
    }

@router.post("/revoke")
async def revoke_sessions(
    container=Depends(get_container),
):
    auth = container.resolve("auth_service")

    await auth.revoke_all_sessions()

    return {
        "success": True,
    }   