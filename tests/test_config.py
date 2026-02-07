"""Tests for application configuration."""

from __future__ import annotations

from expert_spork.core.config import Settings


def test_default_settings() -> None:
    s = Settings()
    assert s.app_name == "expert-spork"
    assert s.port == 8000
    assert s.debug is False
    assert s.model_device == "cpu"
