from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Only create the engine if a DATABASE_URL is configured
_database_url: str | None = settings.DATABASE_URL

if _database_url:
    engine = create_engine(_database_url, echo=settings.DEBUG)
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
else:
    engine = None  # type: ignore[assignment]
    SessionLocal = None  # type: ignore[assignment]


def get_db():
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Please set it in your .env file."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()