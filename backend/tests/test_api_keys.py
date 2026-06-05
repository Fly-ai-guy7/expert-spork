"""API key issuance, lookup, revocation, and auth integration."""
from __future__ import annotations

import hashlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import api_keys as api_keys_svc
from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import ApiKey, AuditEvent


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


def _register(client) -> str:
    r = client.post("/api/v1/auth/register", json={
        "email": "k@x.com", "password": "12345678", "organization_name": "KOrg",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


# --- issuance & storage ------------------------------------------------------

def test_create_returns_raw_token_once(app_client):
    client, Session = app_client
    token = _register(client)
    r = client.post("/api/v1/admin/api-keys", json={"name": "ci-bot"}, headers=_auth(token))
    assert r.status_code == 201, r.text
    body = r.json()
    raw = body["raw_token"]
    assert raw.startswith("eq_")
    assert body["prefix"].startswith("eq_")
    assert body["prefix"] != raw  # only a short display prefix

    with Session() as db:
        row = db.execute(select(ApiKey)).scalar_one()
        # Raw stored only as SHA-256
        assert row.token_hash == hashlib.sha256(raw.encode()).hexdigest()
        assert row.token_hash != raw
        assert len(row.token_hash) == 64


def test_list_hides_secret(app_client):
    client, _ = app_client
    token = _register(client)
    raw = client.post(
        "/api/v1/admin/api-keys", json={"name": "k1"}, headers=_auth(token)
    ).json()["raw_token"]

    listed = client.get("/api/v1/admin/api-keys", headers=_auth(token)).json()
    assert len(listed["items"]) == 1
    body = listed["items"][0]
    assert "raw_token" not in body
    assert raw not in str(body)  # secret nowhere in the list response
    assert body["prefix"].startswith("eq_")


# --- auth using an API key --------------------------------------------------

def test_api_key_authenticates_subsequent_calls(app_client):
    client, _ = app_client
    token = _register(client)
    raw = client.post(
        "/api/v1/admin/api-keys", json={"name": "deploy"}, headers=_auth(token)
    ).json()["raw_token"]

    # Use the API key on a regular endpoint
    r = client.get("/api/v1/cases", headers=_auth(raw))
    assert r.status_code == 200, r.text
    assert "items" in r.json()


def test_api_key_can_reach_admin_endpoints(app_client):
    client, _ = app_client
    token = _register(client)
    raw = client.post(
        "/api/v1/admin/api-keys", json={"name": "admin-bot"}, headers=_auth(token)
    ).json()["raw_token"]
    # Creator is ADMIN, so the key inherits ADMIN privileges
    r = client.get("/api/v1/admin/usage", headers=_auth(raw))
    assert r.status_code == 200


def test_api_key_bumps_last_used_at(app_client):
    client, Session = app_client
    token = _register(client)
    raw = client.post(
        "/api/v1/admin/api-keys", json={"name": "k"}, headers=_auth(token)
    ).json()["raw_token"]

    with Session() as db:
        assert db.execute(select(ApiKey)).scalar_one().last_used_at is None

    client.get("/api/v1/cases", headers=_auth(raw)).raise_for_status()

    with Session() as db:
        assert db.execute(select(ApiKey)).scalar_one().last_used_at is not None


def test_revoked_api_key_returns_401(app_client):
    client, _ = app_client
    token = _register(client)
    created = client.post(
        "/api/v1/admin/api-keys", json={"name": "doomed"}, headers=_auth(token)
    ).json()
    raw, key_id = created["raw_token"], created["id"]

    r = client.delete(f"/api/v1/admin/api-keys/{key_id}", headers=_auth(token))
    assert r.status_code == 204

    # Revoked key no longer authenticates
    r2 = client.get("/api/v1/cases", headers=_auth(raw))
    assert r2.status_code == 401


def test_unknown_api_key_returns_401(app_client):
    client, _ = app_client
    r = client.get("/api/v1/cases", headers=_auth("eq_not_a_real_key_value_at_all_xxx"))
    assert r.status_code == 401


# --- tenant isolation -------------------------------------------------------

def test_api_key_from_org_a_cannot_see_org_b_cases(app_client):
    client, _ = app_client
    a_token = _register(client)
    a_raw = client.post(
        "/api/v1/admin/api-keys", json={"name": "a-key"}, headers=_auth(a_token)
    ).json()["raw_token"]

    # Register org B and create a case in it via human auth
    b_token = client.post("/api/v1/auth/register", json={
        "email": "b@x.com", "password": "12345678", "organization_name": "BOrg",
    }).json()["access_token"]
    b_case = client.post("/api/v1/cases", json={
        "title_en": "B private", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(b_token)).json()["id"]

    # A's API key MUST NOT see B's case (tenant filter still applies)
    a_list = client.get("/api/v1/cases", headers=_auth(a_raw)).json()
    assert a_list["items"] == []
    r = client.get(f"/api/v1/cases/{b_case}", headers=_auth(a_raw))
    assert r.status_code == 404


# --- auditing ---------------------------------------------------------------

def test_create_and_revoke_are_audited(app_client):
    client, Session = app_client
    token = _register(client)
    body = client.post(
        "/api/v1/admin/api-keys", json={"name": "audited"}, headers=_auth(token)
    ).json()
    client.delete(f"/api/v1/admin/api-keys/{body['id']}", headers=_auth(token))

    with Session() as db:
        actions = {e.action for e in db.execute(select(AuditEvent)).scalars().all()}
    assert "API_KEY_CREATE" in actions
    assert "API_KEY_REVOKE" in actions


# --- service-level checks ---------------------------------------------------

def test_looks_like_api_key():
    assert api_keys_svc.looks_like_api_key("eq_abc")
    assert not api_keys_svc.looks_like_api_key("eyJabc")  # JWT
    assert not api_keys_svc.looks_like_api_key("")
