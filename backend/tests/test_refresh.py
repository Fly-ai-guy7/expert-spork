"""Refresh token issuance, rotation, and replay detection."""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import AuditEvent, RefreshToken


@pytest.fixture
def app_client():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

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
    set_context(None)
    yield TestClient(app), Session
    set_context(None)
    engine.dispose()


def _register(client, email="r@x.com", org="ROrg") -> dict:
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "12345678", "organization_name": org,
    })
    r.raise_for_status()
    return r.json()


# --- issuance ---------------------------------------------------------------

def test_register_returns_refresh_token(app_client):
    client, _ = app_client
    body = _register(client)
    assert body["refresh_token"]
    assert body["access_token"]
    assert body["access_token"] != body["refresh_token"]


def test_login_returns_refresh_token(app_client):
    client, _ = app_client
    _register(client)
    r = client.post("/api/v1/auth/login", json={
        "email": "r@x.com", "password": "12345678",
    })
    assert r.status_code == 200
    assert r.json()["refresh_token"]


def test_refresh_token_stored_only_as_hash(app_client):
    """The DB must never contain the raw token — only its SHA-256."""
    client, Session = app_client
    body = _register(client)
    raw = body["refresh_token"]
    with Session() as db:
        rt = db.execute(select(RefreshToken)).scalar_one()
        assert rt.token_hash == hashlib.sha256(raw.encode()).hexdigest()
        assert rt.token_hash != raw
        assert len(rt.token_hash) == 64  # sha256 hex


# --- exchange (rotation) ----------------------------------------------------

def test_refresh_returns_new_pair_and_revokes_old(app_client):
    client, Session = app_client
    body = _register(client)
    old_refresh = body["refresh_token"]

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r.status_code == 200, r.text
    new = r.json()
    assert new["access_token"] != body["access_token"]
    assert new["refresh_token"] != old_refresh

    with Session() as db:
        # Old token is revoked; new token is active in the same family
        old_h = hashlib.sha256(old_refresh.encode()).hexdigest()
        new_h = hashlib.sha256(new["refresh_token"].encode()).hexdigest()
        rows = db.execute(select(RefreshToken).order_by(RefreshToken.created_at)).scalars().all()
        assert len(rows) == 2
        old_row = next(r for r in rows if r.token_hash == old_h)
        new_row = next(r for r in rows if r.token_hash == new_h)
        assert old_row.revoked_at is not None
        assert new_row.revoked_at is None
        assert old_row.family_id == new_row.family_id


def test_refresh_with_unknown_token_returns_401(app_client):
    client, _ = app_client
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-real-token"})
    assert r.status_code == 401


def test_refresh_with_expired_token_returns_401(app_client):
    client, Session = app_client
    body = _register(client)
    with Session() as db:
        rt = db.execute(select(RefreshToken)).scalar_one()
        rt.expires_at = datetime.now(UTC) - timedelta(days=1)
        db.commit()
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert r.status_code == 401


# --- replay detection -------------------------------------------------------

def test_replaying_revoked_refresh_revokes_whole_family(app_client):
    """Stolen refresh-token replay: present an already-rotated token. The
    server detects the replay, revokes the entire family, and the (real)
    user's current token also stops working."""
    client, Session = app_client
    body = _register(client)
    first_refresh = body["refresh_token"]

    # Legit user rotates once
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert r.status_code == 200
    legit_refresh = r.json()["refresh_token"]

    # Attacker replays the original (now revoked) refresh
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": first_refresh})
    assert r2.status_code == 401

    # Legit user's current refresh is now also burned — the family is dead.
    r3 = client.post("/api/v1/auth/refresh", json={"refresh_token": legit_refresh})
    assert r3.status_code == 401

    with Session() as db:
        for rt in db.execute(select(RefreshToken)).scalars():
            assert rt.revoked_at is not None


# --- logout -----------------------------------------------------------------

def test_logout_revokes_token_family(app_client):
    client, Session = app_client
    body = _register(client)
    refresh = body["refresh_token"]

    r = client.post("/api/v1/auth/logout", json={"refresh_token": refresh})
    assert r.status_code == 204

    # Subsequent refresh on the same token is 401
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 401

    with Session() as db:
        # Audit row written
        rows = db.execute(
            select(AuditEvent).where(AuditEvent.action == "LOGOUT")
        ).scalars().all()
        assert len(rows) == 1


def test_logout_with_unknown_token_is_idempotent(app_client):
    client, _ = app_client
    r = client.post("/api/v1/auth/logout", json={"refresh_token": "nonexistent"})
    assert r.status_code == 204


# --- auditing ---------------------------------------------------------------

def test_refresh_is_audited(app_client):
    client, Session = app_client
    body = _register(client)
    client.post("/api/v1/auth/refresh", json={"refresh_token": body["refresh_token"]})
    with Session() as db:
        rows = db.execute(
            select(AuditEvent).where(AuditEvent.action == "REFRESH")
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].actor_email == "r@x.com"
