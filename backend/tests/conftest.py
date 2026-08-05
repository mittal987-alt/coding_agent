import os
from collections.abc import Generator

import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.models.base import Base
from app.database.session import get_db
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///./test.db",
)

engine = create_engine(
    TEST_DATABASE_URL,
    future=True,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
@pytest.fixture(scope="session", autouse=True)
def create_database():

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
@pytest.fixture
def db() -> Generator:

    session = TestingSessionLocal()

    try:
        yield session

    finally:
        session.close()
def override_get_db():

    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()
@pytest.fixture
def client():

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
@pytest.fixture
def test_user(db):

    from app.models.user import User

    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        full_name="Test User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
@pytest.fixture
def test_project(db, test_user):

    from app.models.project import Project

    project = Project(
        name="Demo Project",
        slug="demo-project",
        owner_id=test_user.id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project
@pytest.fixture
def auth_headers():

    token = "test-access-token"

    return {
        "Authorization": f"Bearer {token}"
    }
@pytest.fixture
def mock_current_user(test_user):

    from app.api.dependencies.auth import get_current_user

    app.dependency_overrides[
        get_current_user
    ] = lambda: test_user

    yield test_user

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )
@pytest.fixture
def temp_workspace(tmp_path):

    workspace = tmp_path / "workspace"

    workspace.mkdir()

    return workspace
@pytest.fixture
def git_repo(temp_workspace):

    import subprocess

    subprocess.run(
        ["git", "init"],
        cwd=temp_workspace,
        check=True,
    )

    return temp_workspace
@pytest.fixture
def mock_llm():

    class FakeLLM:

        async def chat(self, *args, **kwargs):
            return "Mock response"

    return FakeLLM()
@pytest.fixture
def mock_embeddings():

    return [0.1] * 1536 