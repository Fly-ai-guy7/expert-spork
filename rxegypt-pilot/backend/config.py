"""Application configuration for RxEgypt Pilot.

Settings are loaded from environment variables (see .env.example). Defaults are
safe for local development only — production secrets must be injected via the
host (Fly.io secrets, Cloudflare, etc.).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    app_name: str = "RxEgypt Pilot — Experts Pharmacy Hurghada"
    api_prefix: str = "/api/v1"
    environment: str = "development"

    # Database
    database_url: str = "postgresql+psycopg2://user:pass@localhost/rxegypt"

    # Auth (JWT)
    secret_key: str = "dev-only-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    # Paymob (Egypt) — hooks only until live credentials are provided
    paymob_api_key: str = ""
    paymob_integration_id: str = ""

    # Rx gating — pharmacist WhatsApp verification line
    pharmacist_whatsapp: str = "+20"

    # CORS
    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
