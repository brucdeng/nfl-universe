"""API-owned connections, created and closed by the application lifespan."""

from dataclasses import dataclass

from fastapi import Request
from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, SQLAlchemyError

from shared.settings import Settings


@dataclass
class ServiceClients:
    """Connections used by the gateway, never by the agent SQL tool."""

    database: Engine
    redis: Redis

    def close(self) -> None:
        """Release connections when the application shuts down."""
        try:
            self.redis.close()
        finally:
            self.database.dispose()


def create_clients(settings: Settings) -> ServiceClients:
    """Validate required configuration and create clients with bounded waits."""
    if settings.database_url is None or settings.redis_url is None:
        raise RuntimeError("The API requires DATABASE_URL and REDIS_URL.")

    try:
        database_url = make_url(settings.database_url.get_secret_value())
    except (ArgumentError, ValueError):
        raise RuntimeError("DATABASE_URL must be a valid PostgreSQL connection URL.") from None
    if database_url.drivername != "postgresql+psycopg":
        raise RuntimeError("DATABASE_URL must use the postgresql+psycopg driver.")

    try:
        redis = Redis.from_url(
            settings.redis_url.get_secret_value(),
            socket_connect_timeout=2,
            socket_timeout=2,
            retry=Retry(NoBackoff(), 0),
        )
    except ValueError:
        raise RuntimeError("REDIS_URL must be a valid Redis connection URL.") from None
    try:
        database = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=0,
            pool_timeout=2,
            connect_args={"connect_timeout": 2, "options": "-c statement_timeout=2000"},
        )
    except (ImportError, SQLAlchemyError):
        redis.close()
        raise
    return ServiceClients(database=database, redis=redis)


def get_clients(request: Request) -> ServiceClients:
    """Expose lifespan-owned clients through FastAPI dependency injection."""
    return request.app.state.clients
