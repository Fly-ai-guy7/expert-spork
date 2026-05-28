from pydantic_settings import BaseSettings, SettingsConfigDict


class MissingSecretsError(RuntimeError):
    """Raised at boot when EQUALISE_ENV=production but required secrets are unset."""


PRODUCTION_REQUIRED = (
    "anthropic_api_key",
    "deepseek_api_key",
    "database_url",
    "jwt_secret",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    equalise_env: str = "development"

    anthropic_api_key: str = ""
    deepseek_api_key: str = ""

    database_url: str = "postgresql+psycopg://equalise:equalise@db:5432/equalise"

    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_ttl_minutes: int = 60 * 24

    claude_opus_model: str = "claude-opus-4-7"
    claude_sonnet_model: str = "claude-sonnet-4-6"
    deepseek_model: str = "deepseek-chat"

    default_max_debate_rounds: int = 3
    hil_gating_enabled: bool = True

    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    corpus_dir: str = "/corpus"

    sentry_dsn: str = ""
    otel_exporter_otlp_endpoint: str = ""

    # Job queue. When broker is empty, Celery runs in eager (in-process) mode —
    # used by dev and the test suite. Production sets a real Redis URL.
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    # LLM resilience
    llm_max_retries: int = 3
    llm_timeout_seconds: float = 60.0
    llm_circuit_threshold: int = 5
    llm_circuit_cooldown_seconds: float = 60.0

    # Observability
    log_json: bool = True
    metrics_enabled: bool = True

    @property
    def celery_eager(self) -> bool:
        return not self.celery_broker_url

    @property
    def is_production(self) -> bool:
        return self.equalise_env.lower() == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def assert_production_ready(self) -> None:
        """Refuse to start in production with empty required secrets.

        Development boots tolerate empty values so contributors can run tests
        without keys. In production we fail fast rather than silently making
        empty API calls.
        """
        if not self.is_production:
            return
        missing = [name for name in PRODUCTION_REQUIRED if not getattr(self, name)]
        if self.cors_origins.strip() in ("", "*"):
            missing.append("cors_origins (must be a concrete allow-list in production)")
        if missing:
            raise MissingSecretsError(
                "Cannot start in production with missing/empty settings: "
                + ", ".join(missing)
            )


settings = Settings()
