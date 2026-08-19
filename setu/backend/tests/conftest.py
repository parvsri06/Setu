"""Pytest config: point the backend at a throwaway SQLite DB before anything imports.

Because ``app.db`` builds its engine from ``DATABASE_URL`` at import time, we must
set the env var here (conftest is imported before test modules). The TestClient
triggers the startup event, which calls ``init_db()`` to create tables.
"""
import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "setu_test.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)

os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"
os.environ["DEV_API_KEY"] = "test-dev-key"
os.environ["JWT_SECRET"] = "test-jwt-secret"


import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
