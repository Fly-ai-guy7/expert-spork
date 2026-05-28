"""Boot-time secret validation.

`assert_production_ready` is a no-op in dev (the default) so contributors
and CI can run without API keys. In production it refuses to start with
missing required secrets — fail loud, never silently call empty APIs.
"""
import pytest

from app.config import MissingSecretsError, Settings


def _prod_settings(**overrides) -> Settings:
    base = dict(
        equalise_env="production",
        anthropic_api_key="k1",
        deepseek_api_key="k2",
        database_url="postgresql://user:pw@host/db",
        jwt_secret="super-secret",
        cors_origins="https://app.example.com",
    )
    base.update(overrides)
    return Settings(**base)


def test_dev_environment_tolerates_empty_secrets():
    s = Settings(equalise_env="development")
    # Should not raise
    s.assert_production_ready()


def test_production_passes_when_all_secrets_present():
    _prod_settings().assert_production_ready()


def test_production_rejects_missing_anthropic_key():
    s = _prod_settings(anthropic_api_key="")
    with pytest.raises(MissingSecretsError, match="anthropic_api_key"):
        s.assert_production_ready()


def test_production_rejects_missing_jwt_secret():
    s = _prod_settings(jwt_secret="")
    with pytest.raises(MissingSecretsError, match="jwt_secret"):
        s.assert_production_ready()


def test_production_rejects_wildcard_cors():
    s = _prod_settings(cors_origins="*")
    with pytest.raises(MissingSecretsError, match="cors_origins"):
        s.assert_production_ready()


def test_production_rejects_empty_cors():
    s = _prod_settings(cors_origins="")
    with pytest.raises(MissingSecretsError, match="cors_origins"):
        s.assert_production_ready()


def test_error_lists_every_missing_field():
    s = Settings(equalise_env="production", cors_origins="https://x")
    with pytest.raises(MissingSecretsError) as exc:
        s.assert_production_ready()
    msg = str(exc.value)
    for field in ("anthropic_api_key", "deepseek_api_key", "jwt_secret"):
        assert field in msg


def test_is_production_flag():
    assert Settings(equalise_env="production").is_production is True
    assert Settings(equalise_env="development").is_production is False
    assert Settings(equalise_env="PRODUCTION").is_production is True
