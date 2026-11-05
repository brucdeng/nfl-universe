"""Unauthenticated process and dependency health checks."""

import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.deps import ServiceClients, get_clients

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Public health information, without connection details or exception text."""

    status: Literal["ok", "error"]
    checks: dict[str, Literal["ok", "error"]]


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"


@router.get("/livez")
def livez() -> LivenessResponse:
    """Report that the API is responding, independently of external services."""
    return LivenessResponse()


@router.get("/healthz", responses={503: {"model": HealthResponse}})
def healthz(
    response: Response,
    clients: Annotated[ServiceClients, Depends(get_clients)],
) -> HealthResponse:
    """Check a real PostgreSQL query, pgvector availability, and Redis PING."""
    checks: dict[str, Literal["ok", "error"]] = {
        "postgres": "error",
        "pgvector": "error",
        "redis": "error",
    }
    try:
        with clients.database.connect() as connection:
            available = connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'vector')")
            ).scalar_one()
            checks["postgres"] = "ok"
            checks["pgvector"] = "ok" if available else "error"
    except SQLAlchemyError:
        # Driver errors can include credentials or hostnames. Log no exception text.
        logger.warning("PostgreSQL health check failed")

    try:
        checks["redis"] = "ok" if clients.redis.ping() else "error"
    except RedisError:
        logger.warning("Redis health check failed")

    healthy = all(value == "ok" for value in checks.values())
    response.status_code = 200 if healthy else 503
    return HealthResponse(status="ok" if healthy else "error", checks=checks)
