from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_database_url: str | None = settings.DATABASE_URL

if _database_url:
    engine = create_engine(
        _database_url,
        echo=settings.DEBUG,

        # Fixes dropped SSL connections (Neon)
        pool_pre_ping=True,

        # Recycle connections every 5 minutes
        pool_recycle=300,

        # Optional but recommended
        pool_size=5,
        max_overflow=10,
    )

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

else:
    engine = None  # type: ignore
    SessionLocal = None  # type: ignore


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