"""Real connections and the containerized API; enabled by explicit test URLs."""

import os
from collections.abc import Iterator

import httpx2 as httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.deps import ServiceClients, create_clients
from app.main import create_app
from shared.settings import Settings

pytestmark = pytest.mark.integration


@pytest.fixture
def integration_settings() -> Settings:
    database_url = os.environ.get("TEST_DATABASE_URL")
    redis_url = os.environ.get("TEST_REDIS_URL")
    if not database_url and not redis_url:
        pytest.skip("Set TEST_DATABASE_URL and TEST_REDIS_URL to run integration tests.")
    if not database_url or not redis_url:
        pytest.fail("Both TEST_DATABASE_URL and TEST_REDIS_URL must be configured.")
    return Settings(_env_file=None, app_env="test", database_url=database_url, redis_url=redis_url)


@pytest.fixture
def real_clients(integration_settings: Settings) -> Iterator[ServiceClients]:
    clients = create_clients(integration_settings)
    try:
        yield clients
    finally:
        clients.close()


def test_postgres_pgvector_and_separate_roles(real_clients: ServiceClients) -> None:
    with real_clients.database.connect() as connection:
        assert connection.execute(text("SELECT current_user")).scalar_one() == "app_rw"
        assert connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector')")
        ).scalar_one()
        roles = connection.execute(
            text(
                "SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles "
                "WHERE rolname IN ('app_rw', 'agent_ro') ORDER BY rolname"
            )
        ).all()
        assert roles == [("agent_ro", False, False, False), ("app_rw", False, False, False)]
        readonly_settings = connection.execute(
            text("SELECT rolconfig FROM pg_roles WHERE rolname = 'agent_ro'")
        ).scalar_one()
        assert "default_transaction_read_only=on" in readonly_settings
    assert real_clients.redis.ping() is True


def test_health_with_real_dependencies(integration_settings: Settings) -> None:
    with TestClient(create_app(integration_settings)) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["checks"] == {"postgres": "ok", "pgvector": "ok", "redis": "ok"}


def test_container_api(integration_settings: Settings) -> None:
    base_url = os.environ.get("TEST_API_URL")
    if not base_url:
        pytest.skip("Set TEST_API_URL to verify the containerized API.")
    with httpx.Client(base_url=base_url, timeout=10) as client:
        health = client.get("/healthz")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"
        assert client.get("/livez").json() == {"status": "ok"}
