import app.models  # Register all SQLAlchemy models first
import uvicorn

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
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        *container.settings.ALLOWED_ORIGINS,
    ],
    allow_credentials=True,
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


@app.get("/health")
@app.get("/health/ready")
@app.get("/health/live")
@app.get("/health/startup")
async def health_root():
    return {
        "status": "ok",
        "message": "Backend Running",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=container.settings.HOST,
        port=container.settings.PORT,
        reload=container.settings.is_development,
    )