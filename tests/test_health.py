import os

import pytest
from fastapi.testclient import TestClient

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture(scope="module")
def client():
    os.environ["REDIS_URL"] = REDIS_URL
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.skipif(
    os.environ.get("TEST_REDIS", "1") != "1",
    reason="requires a running Redis (see infrastructure/redis)",
)
def test_health_reports_redis_healthy(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert "redis" in body["checks"]
    assert body["checks"]["redis"]["status"] == "healthy"


def test_health_returns_checks_payload(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"status", "checks"}
    assert body["status"] in {"healthy", "unhealthy"}
