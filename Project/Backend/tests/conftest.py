
"""
Shared test setup.

Tests create tables directly from SQLModel metadata.
The application itself no longer creates tables at startup.
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test_run.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

import app.models  # noqa: F401
from app.core.database import engine
from app.main import app


@pytest.fixture(scope="module")
def client():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def remove_test_database_file():
    yield

    engine.dispose()

    if os.path.exists("./test_run.db"):
        os.remove("./test_run.db")
