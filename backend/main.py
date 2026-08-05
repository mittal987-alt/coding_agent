import app.models  # Register all SQLAlchemy models first

from app.bootstrap.startup import lifespan
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.bootstrap.container import container
from app.api.v1.router import api_router
from app.core.constant import API_PREFIX
from app.terminal.websocket import router as terminal_ws_router

app = FastAPI(
    title=container.settings.APP_NAME,
    version=container.settings.APP_VERSION,
    debug=container.settings.DEBUG,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=container.settings.ALLOWED_ORIGINS,
    allow_credentials=container.settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(terminal_ws_router)
app.include_router(api_router, prefix=API_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "AI Software Engineer API",
        "version": container.settings.APP_VERSION,
    }