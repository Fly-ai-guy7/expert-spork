"""Auth flow tests: register, login, me, JWT validation, RBAC, switch-org.

Uses FastAPI TestClient against an in-memory SQLite DB. The app dependency
`get_db` is overridden per test so the auth tables live in the same engine
as the rest of the test fixtures.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import issue_token
from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import Membership, Organization, Role, User  # noqa: F401 — registers tables


@pytest.fixture
def app_client():
    # TestClient hits the app in a worker thread; share one in-memory SQLite
    # connection across threads via StaticPool.
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

    def _get_db_override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = _get_db_override
    client = TestClient(app)
    # Reset tenant context between tests
    set_context(None)
    yield client, Session
    set_context(None)
    engine.dispose()


def test_register_creates_user_org_membership(app_client):
    client, Session = app_client
    r = client.post(
        "/api/auth/register",
        json={
            "email": "alice@example.com",
            "password": "correct horse battery",
            "display_name": "Alice",
            "organization_name": "Alice Law LLC",
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["role"] == "ADMIN"
    assert body["org_id"]

    with Session() as db:
        u = db.query(User).filter_by(email="alice@example.com").one()
        assert u.password_hash != "correct horse battery"
        org = db.query(Organization).filter_by(slug="alice-law-llc").one()
        m = db.query(Membership).filter_by(user_id=u.id).one()
        assert m.org_id == org.id
        assert m.role == Role.ADMIN


def test_register_rejects_duplicate_email(app_client):
    client, _ = app_client
    payload = {
        "email": "dup@example.com",
        "password": "correct horse battery",
        "organization_name": "Org A",
    }
    client.post("/api/auth/register", json=payload).raise_for_status()
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 409


def test_register_slugifies_and_dedupes_org_slug(app_client):
    client, Session = app_client
    client.post("/api/auth/register", json={
        "email": "a@x.com", "password": "12345678", "organization_name": "Cairo Bar",
    }).raise_for_status()
    client.post("/api/auth/register", json={
        "email": "b@x.com", "password": "12345678", "organization_name": "Cairo Bar",
    }).raise_for_status()
    with Session() as db:
        slugs = {o.slug for o in db.query(Organization).all()}
    assert "cairo-bar" in slugs
    assert "cairo-bar-2" in slugs


def test_login_returns_jwt_then_me_works(app_client):
    client, _ = app_client
    client.post("/api/auth/register", json={
        "email": "u@x.com", "password": "12345678", "organization_name": "Org",
    }).raise_for_status()

    r = client.post("/api/auth/login", json={"email": "u@x.com", "password": "12345678"})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "u@x.com"
    assert len(body["memberships"]) == 1
    assert body["memberships"][0]["role"] == "ADMIN"


def test_login_rejects_wrong_password(app_client):
    client, _ = app_client
    client.post("/api/auth/register", json={
        "email": "u@x.com", "password": "12345678", "organization_name": "Org",
    }).raise_for_status()
    r = client.post("/api/auth/login", json={"email": "u@x.com", "password": "WRONG"})
    assert r.status_code == 401


def test_me_requires_bearer_token(app_client):
    client, _ = app_client
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_me_rejects_garbage_token(app_client):
    client, _ = app_client
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer NOT_A_JWT"})
    assert r.status_code == 401


def test_password_hash_is_argon2(app_client):
    client, Session = app_client
    client.post("/api/auth/register", json={
        "email": "h@x.com", "password": "supersecret123", "organization_name": "X",
    }).raise_for_status()
    with Session() as db:
        u = db.query(User).filter_by(email="h@x.com").one()
    # passlib argon2 hashes start with "$argon2"
    assert u.password_hash.startswith("$argon2")


def test_switch_org_rejects_non_member(app_client):
    client, Session = app_client
    # User A registers (gets their own org).
    r = client.post("/api/auth/register", json={
        "email": "a@x.com", "password": "12345678", "organization_name": "Org A",
    })
    a_token = r.json()["access_token"]

    # User B registers (different org).
    r = client.post("/api/auth/register", json={
        "email": "b@x.com", "password": "12345678", "organization_name": "Org B",
    })
    b_org_id = r.json()["org_id"]

    # A tries to switch into B's org → 403
    r = client.post(
        "/api/auth/switch-org",
        json={"org_id": b_org_id},
        headers={"Authorization": f"Bearer {a_token}"},
    )
    assert r.status_code == 403


def test_jwt_for_nonexistent_user_is_rejected(app_client):
    """An attacker forging a JWT with the right secret can't bypass the
    db-existence check."""
    import uuid

    client, _ = app_client
    fake_token = issue_token(uuid.uuid4(), None, "ADMIN")
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {fake_token}"})
    assert r.status_code == 401


def test_disabled_user_cannot_use_token(app_client):
    client, Session = app_client
    client.post("/api/auth/register", json={
        "email": "off@x.com", "password": "12345678", "organization_name": "Org",
    }).raise_for_status()
    login = client.post("/api/auth/login", json={"email": "off@x.com", "password": "12345678"})
    token = login.json()["access_token"]

    # Disable the user out-of-band
    with Session() as db:
        u = db.query(User).filter_by(email="off@x.com").one()
        u.is_active = False
        db.commit()

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_revoked_membership_token_is_rejected(app_client):
    """If a user's membership is revoked, their existing token can no longer
    use the claimed org."""
    client, Session = app_client
    r = client.post("/api/auth/register", json={
        "email": "rev@x.com", "password": "12345678", "organization_name": "RevOrg",
    })
    token = r.json()["access_token"]

    # Delete the membership
    with Session() as db:
        m = db.query(Membership).filter_by().one()
        db.delete(m)
        db.commit()

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403
