"""Multi-tenant isolation — the security-critical test.

Two orgs, each with their own user. Verifies that:
- a case created by org A is invisible to org B's list
- org B fetching org A's case id gets 404 (not 403 — no existence leak)
- the SQLAlchemy tenant-filter event hook enforces this even though the
  router's _load_case has no explicit org_id predicate

Runs the full HTTP path with real JWTs against in-memory SQLite + seeded
corpus.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import Statute, StatuteArticle  # noqa: F401 — registers tables

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


@pytest.fixture
def client_and_session():
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

    # Seed a minimal corpus so case creation + statute reads work.
    with Session() as db:
        for path in sorted(CORPUS_DIR.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            statute = Statute(
                law_number=data["law_number"], year=data["year"],
                short_code=data["short_code"], title_en=data.get("title_en"),
                title_ar=data.get("title_ar"), domain_tags=data.get("domain_tags", []),
            )
            db.add(statute)
            db.flush()
            for art in data.get("articles", []):
                db.add(StatuteArticle(
                    statute_id=statute.id, article_number=art["number"],
                    text_en=art.get("text_en"), text_ar=art.get("text_ar"),
                    tags=art.get("tags", []),
                ))
        db.commit()

    def _override():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = _override
    set_context(None)
    yield TestClient(app)
    set_context(None)
    engine.dispose()


def _register(client, email: str, org: str) -> str:
    r = client.post("/api/auth/register", json={
        "email": email, "password": "12345678", "organization_name": org,
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_org_b_cannot_see_org_a_case(client_and_session):
    client = client_and_session
    a_token = _register(client, "a@x.com", "Org A")
    b_token = _register(client, "b@x.com", "Org B")

    # Org A creates a case
    r = client.post("/api/cases", json={"title_en": "A's secret case", "language_primary": "en"},
                    headers=_auth(a_token))
    assert r.status_code == 201, r.text
    case_id = r.json()["id"]

    # Org A can read its own case
    assert client.get(f"/api/cases/{case_id}", headers=_auth(a_token)).status_code == 200

    # Org B cannot — 404, not 403 (no existence leak)
    rb = client.get(f"/api/cases/{case_id}", headers=_auth(b_token))
    assert rb.status_code == 404, rb.text


def test_case_list_is_tenant_scoped(client_and_session):
    client = client_and_session
    a_token = _register(client, "a@x.com", "Org A")
    b_token = _register(client, "b@x.com", "Org B")

    client.post("/api/cases", json={"title_en": "A1", "language_primary": "en"},
                headers=_auth(a_token)).raise_for_status()
    client.post("/api/cases", json={"title_en": "A2", "language_primary": "en"},
                headers=_auth(a_token)).raise_for_status()
    client.post("/api/cases", json={"title_en": "B1", "language_primary": "en"},
                headers=_auth(b_token)).raise_for_status()

    a_list = client.get("/api/cases", headers=_auth(a_token)).json()["items"]
    b_list = client.get("/api/cases", headers=_auth(b_token)).json()["items"]

    assert {c["title_en"] for c in a_list} == {"A1", "A2"}
    assert {c["title_en"] for c in b_list} == {"B1"}


def test_unauthenticated_request_is_rejected(client_and_session):
    client = client_and_session
    assert client.get("/api/cases").status_code == 401
    assert client.post("/api/cases", json={"title_en": "x"}).status_code == 401


def test_trainee_cannot_access_cohort_dashboard(client_and_session):
    """RBAC: cohort analytics is INSTRUCTOR/ADMIN only. A fresh self-registered
    user is ADMIN of their own org, so we demote them to TRAINEE to test the gate."""
    from app.models import Membership, Role
    client = client_and_session
    token = _register(client, "t@x.com", "Org T")

    # Demote to TRAINEE out-of-band, then re-login to get a TRAINEE token
    # (token role is cross-checked against live membership on each request).
    for db in client.app.dependency_overrides[get_db]():
        m = db.query(Membership).one()
        m.role = Role.TRAINEE
        db.commit()
        break

    # Existing token now reflects TRAINEE via membership cross-check
    r = client.get("/api/training/cohort", headers=_auth(token))
    assert r.status_code == 403, r.text


def test_instructor_can_access_cohort_dashboard(client_and_session):
    client = client_and_session
    token = _register(client, "i@x.com", "Org I")  # ADMIN by default
    r = client.get("/api/training/cohort", headers=_auth(token))
    assert r.status_code == 200, r.text
