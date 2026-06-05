"""API contract matrix.

Locks in the security baseline so a future developer can't add a route
that silently skips `Depends(current_user)` or `require_role(...)`.

Three guarantees:
1. Every non-public endpoint returns 401 without a bearer token.
2. Every role-gated endpoint returns 403 for a TRAINEE-role token.
3. The matrix is *complete*: every route the app exposes is either on the
   public allowlist or in the protected matrix. New endpoints fail this
   test until they're explicitly classified.
"""
from __future__ import annotations

import re

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import Membership, Role

DUMMY_UUID = "00000000-0000-0000-0000-000000000001"

# These resolve without a bearer. Tuples are (method, path).
PUBLIC = {
    ("GET", "/health"),
    ("GET", "/healthz"),
    ("GET", "/readyz"),
    ("GET", "/metrics"),
    ("POST", "/api/v1/auth/register"),
    ("POST", "/api/v1/auth/login"),
    # Legacy (/api/...) mirrors — also public for the bootstrap pair.
    ("POST", "/api/auth/register"),
    ("POST", "/api/auth/login"),
}

# Every protected endpoint. body/query are the minimum needed to clear
# request validation so the auth dependency actually runs (otherwise FastAPI
# 422s before checking the bearer).
# Format: (method, path_template, body_json, query_string)
PROTECTED: list[tuple[str, str, dict | None, str]] = [
    ("GET", "/api/v1/auth/me", None, ""),
    ("POST", "/api/v1/auth/switch-org", {"org_id": DUMMY_UUID}, ""),
    ("GET", "/api/v1/cases", None, ""),
    ("POST", "/api/v1/cases", {}, ""),
    ("POST", "/api/v1/cases/generate", {}, ""),
    ("GET", f"/api/v1/cases/{DUMMY_UUID}", None, ""),
    ("POST", f"/api/v1/cases/{DUMMY_UUID}/run", {}, ""),
    ("POST", f"/api/v1/cases/{DUMMY_UUID}/cancel", {}, ""),
    ("POST", f"/api/v1/cases/{DUMMY_UUID}/run-training", {}, ""),
    ("GET", f"/api/v1/cases/{DUMMY_UUID}/status", None, ""),
    ("GET", f"/api/v1/cases/{DUMMY_UUID}/report", None, ""),
    ("GET", f"/api/v1/cases/{DUMMY_UUID}/report.pdf", None, ""),
    ("GET", f"/api/v1/cases/{DUMMY_UUID}/events", None, ""),
    ("GET", "/api/v1/statutes", None, ""),
    ("GET", "/api/v1/statutes/search", None, "q=test"),
    ("GET", f"/api/v1/statutes/{DUMMY_UUID}", None, ""),
    ("GET", "/api/v1/hil/pending", None, ""),
    ("POST", f"/api/v1/hil/{DUMMY_UUID}/approve", {}, ""),
    ("POST", f"/api/v1/hil/{DUMMY_UUID}/modify", {}, ""),
    ("POST", f"/api/v1/hil/{DUMMY_UUID}/halt", {}, ""),
    ("POST", f"/api/v1/hil/{DUMMY_UUID}/submit-trainee", {}, ""),
    ("GET", f"/api/v1/training/{DUMMY_UUID}/coaching", None, ""),
    ("GET", f"/api/v1/training/{DUMMY_UUID}/coaching.pdf", None, ""),
    ("GET", "/api/v1/training/progress", None, "user_id=x"),
    ("GET", "/api/v1/training/cohort", None, ""),
    ("GET", "/api/v1/training/recommendations", None, "user_id=x"),
    ("GET", "/api/v1/training/sessions", None, ""),
    ("GET", "/api/v1/admin/usage", None, ""),
    ("GET", "/api/v1/admin/audit", None, ""),
]

# Endpoints that require INSTRUCTOR or ADMIN. A TRAINEE should get 403.
ROLE_GATED: list[tuple[str, str, dict | None, str]] = [
    ("GET", "/api/v1/admin/usage", None, ""),
    ("GET", "/api/v1/admin/audit", None, ""),
    ("GET", "/api/v1/training/cohort", None, ""),
]


# --- fixture ----------------------------------------------------------------

@pytest.fixture
def client():
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
    yield TestClient(app), Session, app
    set_context(None)
    engine.dispose()


def _call(client_obj: TestClient, method: str, path: str, body, query: str, headers=None):
    url = f"{path}?{query}" if query else path
    if method == "GET":
        return client_obj.get(url, headers=headers)
    if method == "POST":
        return client_obj.post(url, json=body, headers=headers)
    raise NotImplementedError(method)


# --- (1) every protected endpoint refuses 401 without auth ------------------

@pytest.mark.parametrize("method,path,body,query", PROTECTED)
def test_protected_endpoint_refuses_unauthenticated(client, method, path, body, query):
    tc, _, _ = client
    r = _call(tc, method, path, body, query)
    assert r.status_code == 401, (
        f"{method} {path} returned {r.status_code} without auth — expected 401. "
        f"Body: {r.text[:200]}"
    )


# --- (2) role-gated endpoints refuse 403 for a TRAINEE ----------------------

def _trainee_token(client_obj: TestClient, Session) -> str:
    """Register (defaults to ADMIN), then demote to TRAINEE so the
    membership cross-check downgrades the token."""
    r = client_obj.post("/api/v1/auth/register", json={
        "email": "trainee@x.com", "password": "12345678", "organization_name": "TOrg",
    })
    r.raise_for_status()
    token = r.json()["access_token"]
    with Session() as db:
        m = db.query(Membership).one()
        m.role = Role.TRAINEE
        db.commit()
    return token


@pytest.mark.parametrize("method,path,body,query", ROLE_GATED)
def test_role_gated_endpoint_refuses_non_privileged(client, method, path, body, query):
    tc, Session, _ = client
    token = _trainee_token(tc, Session)
    r = _call(tc, method, path, body, query, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403, (
        f"{method} {path} returned {r.status_code} for TRAINEE — expected 403. "
        f"Body: {r.text[:200]}"
    )


# --- (3) completeness: every exposed route is classified --------------------

def _normalise_template(path: str) -> str:
    """Replace {param} with the dummy uuid so we can compare against the
    PROTECTED matrix entries (which already use a literal uuid)."""
    return re.sub(r"\{[^}]+\}", DUMMY_UUID, path)


def test_every_route_is_classified(client):
    _, _, app = client
    protected_set = {(m, p) for (m, p, _, _) in PROTECTED}
    unclassified: list[tuple[str, str]] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        path = _normalise_template(route.path)
        for method in sorted(route.methods - {"HEAD", "OPTIONS"}):
            # Skip the legacy /api/ mirrors — they're auto-generated from the
            # same routers as /api/v1/ so the v1 entry covers them.
            if path.startswith("/api/") and not path.startswith("/api/v1/"):
                continue
            if (method, path) in PUBLIC:
                continue
            if (method, path) in protected_set:
                continue
            unclassified.append((method, path))

    assert not unclassified, (
        "The following routes are neither PUBLIC nor in the PROTECTED matrix. "
        "Add them to one or the other: " + ", ".join(f"{m} {p}" for m, p in unclassified)
    )


# --- bonus: legacy /api mirrors enforce the same auth as /api/v1 ------------

@pytest.mark.parametrize("v1_path", [
    "/api/v1/cases",
    f"/api/v1/cases/{DUMMY_UUID}",
    "/api/v1/admin/usage",
])
def test_legacy_prefix_enforces_same_auth(client, v1_path):
    tc, _, _ = client
    legacy = v1_path.replace("/api/v1", "/api", 1)
    r1 = tc.get(v1_path)
    r2 = tc.get(legacy)
    assert r1.status_code == r2.status_code == 401
