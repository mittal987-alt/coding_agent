from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_database_url: str | None = settings.DATABASE_URL

if _database_url:
    engine = create_engine(
        _database_url,
        echo=settings.DEBUG,

        # Recycle connections every 5 minutes to handle Neon's idle timeout
        pool_recycle=300,

        pool_size=5,
        max_overflow=10,

        # Fail fast if pool is exhausted (seconds)
        pool_timeout=6,

        # psycopg2 connection settings:
        # - connect_timeout: abort if host is unreachable within 10s
        # - keepalives: detect stale Neon connections quickly
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 10,
            "keepalives_interval": 5,
            "keepalives_count": 3,
        },
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