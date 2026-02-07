"""Application entry point — creates and configures the FastAPI app."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

import uvicorn
from fastapi import FastAPI

from expert_spork.api.routes import router
from expert_spork.core.config import settings
from expert_spork.core.logging import get_logger, setup_logging
from expert_spork.ml.engine import engine

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle hook."""
    setup_logging()
    log.info("starting", app=settings.app_name, version=settings.app_version)
    await engine.load()
    yield
    log.info("shutting_down")


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1")
    return app


app = create_app()


def run() -> None:
    """CLI entry point (``serve`` command)."""
    uvicorn.run(
        "expert_spork.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run()
