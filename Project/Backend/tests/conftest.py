"""
Shared test setup. pytest loads this file BEFORE any test module, so the
environment variables are set before the app (and its cached settings) are imported.
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_run.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

import app.models  # noqa: F401  (makes sure every table is registered)
from app.core.database import engine
from app.main import app


@pytest.fixture(scope="module")
def client():
    # Every test file starts from empty tables, so files can't affect each other.
    SQLModel.metadata.drop_all(engine)
    with TestClient(app) as c:  # app startup re-creates the tables
        yield c


@pytest.fixture(scope="session", autouse=True)
def _remove_test_database_file():
    yield
    engine.dispose()
    if os.path.exists("./test_run.db"):
        os.remove("./test_run.db")