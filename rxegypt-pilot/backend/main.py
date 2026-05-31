"""FastAPI entry point for RxEgypt Pilot — Experts Pharmacy Hurghada.

Astra Intelligence Services (Misr) — AISE
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes import auth, drugs, inventory, orders

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="B2B pharmacy management + patient platform. Pilot: Experts Pharmacy Hurghada.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "service": "rxegypt-pilot", "env": settings.environment}


for module in (auth, drugs, inventory, orders):
    app.include_router(module.router, prefix=settings.api_prefix)
