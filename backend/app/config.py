from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    deepseek_api_key: str = ""

    database_url: str = "postgresql+psycopg://equalise:equalise@db:5432/equalise"

    claude_opus_model: str = "claude-opus-4-7"
    claude_sonnet_model: str = "claude-sonnet-4-6"
    deepseek_model: str = "deepseek-chat"

    default_max_debate_rounds: int = 3
    hil_gating_enabled: bool = True

    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"

    corpus_dir: str = "/corpus"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
