from fastapi import APIRouter
from .health import router as health_router
from .project import router as project_router
from .chat import router as chat_router
from .hitl import router as hitl_router
from .stream import router as stream_router
from .patches import router as patches_router
from app.terminal.routes import router as terminal_router

api_router = APIRouter()

api_router.include_router(
    health_router,
    tags=["Health"],
)

api_router.include_router(
    project_router,
    prefix="/projects",
    tags=["Projects"],
)

api_router.include_router(
    chat_router,
    prefix="/projects/{project_id}/chat",
    tags=["Chat"],
)

api_router.include_router(
    terminal_router,
    prefix="/terminal",
    tags=["Terminal"],
)

api_router.include_router(
    hitl_router,
    prefix="/hitl",
    tags=["Human-In-The-Loop"],
)

api_router.include_router(
    stream_router,
    prefix="/stream",
    tags=["Stream"],
)

api_router.include_router(
    patches_router,
    prefix="/patches",
    tags=["Patches"],
)