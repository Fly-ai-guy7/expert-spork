"""Application configuration for RxEgypt Pilot.

Settings are loaded from environment variables (see .env.example). Defaults are
safe for local development only — production secrets must be injected via the
host (Fly.io secrets, Cloudflare, etc.).
"""
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET = "dev-only-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Core
    app_name: str = "RxEgypt Pilot — Experts Pharmacy Hurghada"
    api_prefix: str = "/api/v1"
    environment: str = "development"

    # Database
    database_url: str = "postgresql+psycopg2://user:pass@localhost/rxegypt"

    # Auth (JWT)
    secret_key: str = _DEV_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    # Paymob (Egypt) — when paymob_api_key is empty, payments run in MOCK mode.
    paymob_api_key: str = ""
    paymob_integration_id: str = ""
    paymob_iframe_id: str = ""
    paymob_hmac_secret: str = ""

    # Rx gating — pharmacist WhatsApp verification line
    pharmacist_whatsapp: str = "+20"

    # CORS
    cors_origins: str = "http://localhost:3000"

    @model_validator(mode="after")
    def _guard_production(self):
        """Fail fast if a production deploy is missing a real secret."""
        if self.environment == "production" and (
            not self.secret_key
            or self.secret_key == _DEV_SECRET
            or len(self.secret_key) < 16
        ):
            raise ValueError(
                "SECRET_KEY must be set to a strong value (>=16 chars) in "
                "production. Set it via host secrets (e.g. `fly secrets set "
                "SECRET_KEY=...`)."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
