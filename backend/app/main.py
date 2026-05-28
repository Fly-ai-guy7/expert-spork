import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.auth.router import router as auth_router
from app.config import settings
from app.observability.logging import setup_logging
from app.observability.metrics import render_latest
from app.observability.middleware import (
    ApiVersionMiddleware,
    ObservabilityMiddleware,
    SecurityHeadersMiddleware,
)
from app.routers import admin, cases, health, hil, statutes, training

logging.basicConfig(level=settings.log_level)
setup_logging(level=settings.log_level, json_logs=settings.log_json)


def _init_sentry() -> None:
    if not settings.sentry_dsn:
        return
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.equalise_env,
            traces_sample_rate=0.1,
        )
    except Exception:  # noqa: BLE001 — observability must not block startup
        logging.getLogger(__name__).warning("Sentry init failed", exc_info=True)


def create_app() -> FastAPI:
    settings.assert_production_ready()
    _init_sentry()
    app = FastAPI(
        title="EQUALISE Egypt API",
        version="0.1.0",
        description=(
            "AI-Powered Legal Simulation & Case Intelligence System for Egyptian law. "
            "AI Simulation Only — Not Legal Advice. All outputs require review by a "
            "qualified Egyptian lawyer."
        ),
    )

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit_default],
        enabled=settings.rate_limit_enabled,
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Middleware order (outermost first): security headers -> rate limit ->
    # observability -> CORS.
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ApiVersionMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health/metrics live at the root, unversioned.
    app.include_router(health.router)

    # API routers are mounted under the current version (/api/v1) and the
    # legacy /api prefix (v0). v0 responses carry a Deprecation header set by
    # ApiVersionMiddleware so clients get nudged to migrate.
    api_routers = [auth_router, cases.router, statutes.router, hil.router, training.router, admin.router]
    for r in api_routers:
        app.include_router(r, prefix="/api/v1")
        app.include_router(r, prefix="/api")

    if settings.metrics_enabled:

        @app.get("/metrics", include_in_schema=False)
        def metrics() -> Response:
            body, content_type = render_latest()
            return Response(content=body, media_type=content_type)

    return app


app = create_app()
