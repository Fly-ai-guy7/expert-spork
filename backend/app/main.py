import logging

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.observability.logging import setup_logging
from app.observability.metrics import render_latest
from app.observability.middleware import ObservabilityMiddleware
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

    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth_router)
    app.include_router(cases.router)
    app.include_router(statutes.router)
    app.include_router(hil.router)
    app.include_router(training.router)
    app.include_router(admin.router)

    if settings.metrics_enabled:

        @app.get("/metrics", include_in_schema=False)
        def metrics() -> Response:
            body, content_type = render_latest()
            return Response(content=body, media_type=content_type)

    return app


app = create_app()
