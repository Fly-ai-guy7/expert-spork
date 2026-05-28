import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cases, health, hil, statutes, training

logging.basicConfig(level=settings.log_level)


def create_app() -> FastAPI:
    settings.assert_production_ready()
    app = FastAPI(
        title="EQUALISE Egypt API",
        version="0.1.0",
        description=(
            "AI-Powered Legal Simulation & Case Intelligence System for Egyptian law. "
            "AI Simulation Only — Not Legal Advice. All outputs require review by a "
            "qualified Egyptian lawyer."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(cases.router)
    app.include_router(statutes.router)
    app.include_router(hil.router)
    app.include_router(training.router)
    return app


app = create_app()
