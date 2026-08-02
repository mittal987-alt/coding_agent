import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if os.getenv("RENDER") == "true" and (not DATABASE_URL or "localhost" in DATABASE_URL):
    raise ValueError(
        "CRITICAL ERROR: The DATABASE_URL environment variable is missing or set to localhost on Render! "
        "You MUST go to the Render Dashboard -> your Web Service (finance-coach-backend) -> Environment -> "
        "Add Environment Variable. Set Key to 'DATABASE_URL' and Value to your Render PostgreSQL Internal Database URL."
    )

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:Mittal987368%40@localhost:5432/finance"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()