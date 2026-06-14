"""Production safety guard on Settings."""
import pytest

from config import Settings


def test_production_rejects_dev_secret():
    with pytest.raises(ValueError):
        Settings(environment="production", secret_key="dev-only-secret-change-me")


def test_production_rejects_short_secret():
    with pytest.raises(ValueError):
        Settings(environment="production", secret_key="short")


def test_production_accepts_strong_secret():
    s = Settings(environment="production", secret_key="x" * 32)
    assert s.environment == "production"


def test_development_allows_default_secret():
    s = Settings(environment="development", secret_key="dev-only-secret-change-me")
    assert s.secret_key
