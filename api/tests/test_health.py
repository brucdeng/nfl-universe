"""Exercise health responses, dependency failures, and lifespan cleanup."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import Engine
from sqlalchemy.exc import OperationalError

from app.deps import ServiceClients, create_clients
from app.main import create_app
from shared.settings import Settings


@pytest.fixture
def clients() -> ServiceClients:
    database = MagicMock(spec=Engine)
    connection = database.connect.return_value.__enter__.return_value
    connection.execute.return_value.scalar_one.return_value = True
    redis = MagicMock(spec=Redis)
    redis.ping.return_value = True
    return ServiceClients(database=database, redis=redis)


def test_healthy_response_and_cleanup(
    monkeypatch: pytest.MonkeyPatch, clients: ServiceClients
) -> None:
    monkeypatch.setattr("app.main.create_clients", lambda settings: clients)
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "checks": {"postgres": "ok", "pgvector": "ok", "redis": "ok"},
        }
    clients.database.dispose.assert_called_once()
    clients.redis.close.assert_called_once()


@pytest.mark.parametrize("failure", ["postgres", "redis", "pgvector", "both"])
def test_unhealthy_dependencies_return_503_without_leaking_errors(
    monkeypatch: pytest.MonkeyPatch,
    clients: ServiceClients,
    caplog: pytest.LogCaptureFixture,
    failure: str,
) -> None:
    secret = "private-connection-details"
    if failure in {"postgres", "both"}:
        clients.database.connect.side_effect = OperationalError("SELECT", {}, Exception(secret))
    if failure in {"redis", "both"}:
        clients.redis.ping.side_effect = RedisConnectionError(secret)
    if failure == "pgvector":
        connection = clients.database.connect.return_value.__enter__.return_value
        connection.execute.return_value.scalar_one.return_value = False

    monkeypatch.setattr("app.main.create_clients", lambda settings: clients)
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.get("/healthz")
        assert response.status_code == 503
        assert response.json()["status"] == "error"
        checks = response.json()["checks"]
        assert checks["postgres"] == ("error" if failure in {"postgres", "both"} else "ok")
        assert checks["redis"] == ("error" if failure in {"redis", "both"} else "ok")
        assert checks["pgvector"] == (
            "error" if failure in {"postgres", "pgvector", "both"} else "ok"
        )
        assert secret not in response.text
        assert secret not in caplog.text


def test_liveness_does_not_call_dependencies(
    monkeypatch: pytest.MonkeyPatch, clients: ServiceClients
) -> None:
    monkeypatch.setattr("app.main.create_clients", lambda settings: clients)
    with TestClient(create_app(Settings(_env_file=None))) as client:
        response = client.get("/livez")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    clients.database.connect.assert_not_called()
    clients.redis.ping.assert_not_called()


@pytest.mark.parametrize("missing", ["database_url", "redis_url"])
def test_api_startup_rejects_missing_required_setting(missing: str) -> None:
    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://app_rw:fake@localhost/test",
        redis_url="redis://localhost:6379/0",
    ).model_copy(update={missing: None})
    with pytest.raises(RuntimeError, match="requires DATABASE_URL and REDIS_URL"):
        with TestClient(create_app(settings)):
            pass


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("database_url", "private-connection-details", "valid PostgreSQL"),
        ("database_url", "postgresql+psycopg://user:fake@localhost:bad/test", "valid PostgreSQL"),
        ("database_url", "sqlite:///test.db", "postgresql\\+psycopg"),
        ("redis_url", "private-connection-details", "valid Redis"),
    ],
)
def test_invalid_connection_configuration_has_a_safe_error(
    field: str, value: str, message: str
) -> None:
    values = {
        "database_url": "postgresql+psycopg://app_rw:fake@localhost/test",
        "redis_url": "redis://localhost:6379/0",
        field: value,
    }
    with pytest.raises(RuntimeError, match=message) as error:
        create_clients(Settings(_env_file=None, **values))
    assert "private-connection-details" not in str(error.value)
