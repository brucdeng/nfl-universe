"""FastAPI gateway entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.deps import create_clients
from app.routers.health import router as health_router
from shared.settings import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an application; configuration and connections load during startup."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        clients = create_clients(settings if settings is not None else get_settings())
        application.state.clients = clients
        try:
            yield
        finally:
            clients.close()

    application = FastAPI(title="nfl-universe", version="0.1.0", lifespan=lifespan)
    application.include_router(health_router)
    return application


app = create_app()
