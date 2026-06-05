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


# --- per-route limits on LLM-spending endpoints ------------------------------

def _register(client):
    r = client.post("/api/v1/auth/register", json={
        "email": "rl@x.com", "password": "12345678", "organization_name": "RLOrg",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def test_run_endpoint_has_tighter_per_route_limit():
    """The per-route limit fires before the route handler, so hitting /run
    on a bogus case_id is enough to observe it — we don't need to actually
    spin up the pipeline. Pin to 2/min so we can observe it in 3 calls."""
    client, engine = _build_client(
        rate_limit_enabled=True,
        rate_limit_default="1000/minute",  # generous, so the default never trips
        rate_limit_run="2/minute",
    )
    try:
        token = _register(client)
        h = {"Authorization": f"Bearer {token}"}
        fake = "00000000-0000-0000-0000-000000000099"
        # First two return 404 (case missing) but still count toward the limit.
        assert client.post(f"/api/v1/cases/{fake}/run", json={"max_rounds": 1}, headers=h).status_code == 404
        assert client.post(f"/api/v1/cases/{fake}/run", json={"max_rounds": 1}, headers=h).status_code == 404
        # Third trips the per-route ceiling
        assert client.post(f"/api/v1/cases/{fake}/run", json={"max_rounds": 1}, headers=h).status_code == 429
    finally:
        settings.rate_limit_default = "120/minute"
        settings.rate_limit_run = "10/minute"
        engine.dispose()


def test_generate_endpoint_has_tighter_per_route_limit(monkeypatch):
    """/generate hits the LLM, which would 500 in the test env. We stub the
    generator so the first call succeeds and the second trips the limit."""
    import app.routers.cases as cases_router
    from app.models import Case as CaseModel

    async def _fake_generate(db, **kwargs):
        c = CaseModel(title_en="stub", language_primary="en", area_of_law="IP")
        db.add(c)
        db.commit()
        db.refresh(c)
        return c

    monkeypatch.setattr(cases_router.case_generator, "generate_case", _fake_generate)

    client, engine = _build_client(
        rate_limit_enabled=True,
        rate_limit_default="1000/minute",
        rate_limit_generate="1/minute",
    )
    try:
        token = _register(client)
        h = {"Authorization": f"Bearer {token}"}
        body = {"area_of_law": "IP", "difficulty": 2, "language": "en"}
        first = client.post("/api/v1/cases/generate", json=body, headers=h)
        assert first.status_code == 201
        second = client.post("/api/v1/cases/generate", json=body, headers=h)
        assert second.status_code == 429
    finally:
        settings.rate_limit_default = "120/minute"
        settings.rate_limit_generate = "5/minute"
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
