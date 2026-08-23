from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Global application settings.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================
    # Application
    # ==========================================================

    APP_NAME: str = "AI Software Engineer"

    APP_VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"

    DEBUG: bool = True

    SECRET_KEY: str = Field(
        default="change-me",
        repr=False,
    )

    HOST: str = "0.0.0.0"

    PORT: int = 8080

    API_PREFIX: str = "/api/v1"

    # ==========================================================
    # LLM Keys
    # ==========================================================

    OPENAI_API_KEY: str | None = None

    ANTHROPIC_API_KEY: str | None = None

    GEMINI_API_KEY: str | None = None

    MISTRAL_API_KEY: str | None = None

    OPENROUTER_API_KEY: str | None = None

    OLLAMA_HOST: str = "http://localhost:11434"

    # ==========================================================
    # Database
    # ==========================================================

    DATABASE_URL: str | None = None

    REDIS_URL: str | None = None

    VECTOR_DB_URL: str | None = None

    # ==========================================================
    # Workspace
    # ==========================================================

    WORKSPACE_ROOT: Path = BASE_DIR / "workspace"

    SANDBOX_ROOT: Path = BASE_DIR / "sandbox"

    TEMP_DIR: Path = BASE_DIR / "tmp"

    # ==========================================================
    # Logging
    # ==========================================================

    LOG_LEVEL: str = "INFO"

    LOG_FORMAT: str = "console"

    # ==========================================================
    # Cache
    # ==========================================================

    CACHE_ENABLED: bool = True

    CACHE_SIZE: int = 1000

    # ==========================================================
    # Memory
    # ==========================================================

    MEMORY_BACKEND: str = "sqlite"

    MEMORY_PATH: Path = BASE_DIR / "memory"

    # ==========================================================
    # Tool Execution
    # ==========================================================

    TOOL_TIMEOUT: int = 120

    MAX_CONCURRENT_TOOLS: int = 5

    # ==========================================================
    # Agent Settings
    # ==========================================================

    MAX_ITERATIONS: int = 20

    MAX_PLAN_DEPTH: int = 5

    ENABLE_STREAMING: bool = True

    ENABLE_TOOL_CALLS: bool = True

    # ==========================================================
    # Security
    # ==========================================================

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

    CORS_ALLOW_CREDENTIALS: bool = True

    # ==========================================================
    # Computed Fields
    # ==========================================================

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @computed_field
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "testing"

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a singleton Settings instance.
    """
    return Settings()


# Module-level singleton for direct import
settings: Settings = get_settings()
