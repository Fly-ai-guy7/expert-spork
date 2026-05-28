"""Security hardening + health probes.

Covers security headers, global rate limiting, LLM input sanitisation, and
the liveness/readiness endpoints.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db import Base, get_db
from app.main import create_app
from app.security.sanitize import sanitize_citations, sanitize_text


def _build_client(**setting_overrides):
    for k, v in setting_overrides.items():
        setattr(settings, k, v)
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    def _override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = _override
    return TestClient(app), engine


# --- security headers --------------------------------------------------------

def test_security_headers_present():
    client, engine = _build_client(rate_limit_enabled=False)
    try:
        r = client.get("/healthz")
        assert r.headers["X-Content-Type-Options"] == "nosniff"
        assert r.headers["X-Frame-Options"] == "DENY"
        assert "Strict-Transport-Security" in r.headers
        assert "Content-Security-Policy" in r.headers
    finally:
        engine.dispose()


# --- rate limiting -----------------------------------------------------------

def test_rate_limit_returns_429_over_limit():
    client, engine = _build_client(rate_limit_enabled=True, rate_limit_default="2/minute")
    try:
        assert client.get("/healthz").status_code == 200
        assert client.get("/healthz").status_code == 200
        # Third within the window trips the limiter
        assert client.get("/healthz").status_code == 429
    finally:
        # Restore default so other tests aren't throttled
        settings.rate_limit_default = "120/minute"
        engine.dispose()


def test_rate_limit_disabled_passthrough():
    client, engine = _build_client(rate_limit_enabled=False)
    try:
        for _ in range(5):
            assert client.get("/healthz").status_code == 200
    finally:
        engine.dispose()


# --- input sanitisation ------------------------------------------------------

def test_sanitize_strips_control_chars():
    dirty = "hello\x00\x07world\x1b[31m"
    assert sanitize_text(dirty) == "helloworld[31m"


def test_sanitize_preserves_arabic_and_newlines():
    text = "المدعى عليه\nطرف ثانٍ\tمسافة"
    out = sanitize_text(text)
    assert "المدعى عليه" in out
    assert "\n" in out and "\t" in out


def test_sanitize_caps_length():
    assert len(sanitize_text("x" * 50_000, max_chars=100)) == 100


def test_sanitize_none_passthrough():
    assert sanitize_text(None) is None


def test_sanitize_citations_bounds_and_cleans():
    cites = ["82/2002:113", "  12/2003:82\x00 ", 123, "x" * 500] + ["a"] * 100
    out = sanitize_citations(cites, max_items=50)
    assert len(out) <= 50
    assert "82/2002:113" in out
    assert "12/2003:82" in out  # control char + whitespace stripped
    assert all(len(c) <= 128 for c in out)


# --- health / readiness ------------------------------------------------------

def test_healthz_is_liveness_only():
    client, engine = _build_client(rate_limit_enabled=False)
    try:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}
    finally:
        engine.dispose()


def test_readyz_ok_when_db_up():
    client, engine = _build_client(rate_limit_enabled=False)
    try:
        r = client.get("/readyz")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"
        assert body["checks"]["db"] == "ok"
        # No broker configured in tests → eager
        assert body["checks"]["redis"] == "eager (no broker)"
    finally:
        engine.dispose()
