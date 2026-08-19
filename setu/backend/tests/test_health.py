"""Smoke tests: the app boots and both health endpoints answer."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "relief-registry-backend"


def test_health_db():
    resp = client.get("/health/db")
    assert resp.status_code == 200
    body = resp.json()
    assert body["database"] == "reachable"
    assert body["result"] == 1
