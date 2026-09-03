from __future__ import annotations

from app.bootstrap import application
from fastapi import APIRouter
from app.terminal.routes import router as terminal_router
from app.api.routes.agent import router as agent_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.memory import router as memory_router
from app.api.routes.models import router as models_router
from app.api.routes.projects import router as projects_router
from app.api.routes.tools import router as tools_router
from app.api.routes.workspace import router as workspace_router
from app.api.v1.hitl import router as hitl_router
from app.api.v1.patches import router as patches_router
from app.api.v1.stream import router as stream_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"],
)
api_router.include_router(
    terminal_router,
    prefix="/terminal",
    tags=["Terminal"],
)

api_router.include_router(
    agent_router,
    prefix="/agents",
    tags=["Agents"],
)
api_router.include_router(
    workspace_router,
    prefix="/workspace",
    tags=["Workspace"],
)

api_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["Projects"],
)
api_router.include_router(
    tools_router,
    prefix="/tools",
    tags=["Tools"],
)

api_router.include_router(
    memory_router,
    prefix="/memory",
    tags=["Memory"],
)

api_router.include_router(
    models_router,
    prefix="/models",
    tags=["Models"],
)

api_router.include_router(
    hitl_router,
    prefix="/hitl",
    tags=["HITL"],
)

api_router.include_router(
    patches_router,
    prefix="/patches",
    tags=["Patches"],
)

api_router.include_router(
    stream_router,
    prefix="/stream",
    tags=["Stream"],
)