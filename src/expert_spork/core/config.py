"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration — values are read from env vars or .env file."""

    app_name: str = "expert-spork"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Model
    model_name: str = "default"
    model_device: str = "cpu"
    max_batch_size: int = 32

    # Logging
    log_level: str = "INFO"
    log_json: bool = True

    model_config = {"env_prefix": "SPORK_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
