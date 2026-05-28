"""API maturity (1.3): versioning, cursor pagination, ETags, idempotency."""
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
def client(monkeypatch, mock_llm):
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

    # Eager worker shares the test DB.
    import app.workers.tasks as tasks_mod
    monkeypatch.setattr(tasks_mod, "SessionLocal", Session)

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


def _token(client) -> str:
    r = client.post("/api/auth/register", json={
        "email": "v@x.com", "password": "12345678", "organization_name": "VOrg",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


# --- versioning --------------------------------------------------------------

def test_v1_and_legacy_both_resolve(client):
    token = _token(client)
    assert client.get("/api/v1/cases", headers=_auth(token)).status_code == 200
    assert client.get("/api/cases", headers=_auth(token)).status_code == 200


def test_legacy_prefix_carries_deprecation_header(client):
    token = _token(client)
    legacy = client.get("/api/cases", headers=_auth(token))
    assert legacy.headers.get("Deprecation") == "true"
    assert 'rel="successor-version"' in legacy.headers.get("Link", "")
    assert "/api/v1/cases" in legacy.headers.get("Link", "")


def test_v1_prefix_has_no_deprecation_header(client):
    token = _token(client)
    v1 = client.get("/api/v1/cases", headers=_auth(token))
    assert "Deprecation" not in v1.headers


# --- cursor pagination -------------------------------------------------------

def test_pagination_walks_all_cases_without_overlap(client):
    token = _token(client)
    for i in range(7):
        client.post("/api/v1/cases", json={"title_en": f"C{i}", "language_primary": "en"},
                    headers=_auth(token)).raise_for_status()

    seen: list[str] = []
    cursor = None
    pages = 0
    while True:
        url = "/api/v1/cases?limit=3" + (f"&cursor={cursor}" if cursor else "")
        body = client.get(url, headers=_auth(token)).json()
        pages += 1
        seen.extend(c["id"] for c in body["items"])
        cursor = body["next_cursor"]
        if not cursor:
            break
        assert pages <= 5, "pagination did not terminate"

    assert len(seen) == 7
    assert len(set(seen)) == 7, "pages overlapped"
    assert pages == 3  # 3 + 3 + 1


def test_pagination_envelope_shape(client):
    token = _token(client)
    client.post("/api/v1/cases", json={"title_en": "Only", "language_primary": "en"},
                headers=_auth(token)).raise_for_status()
    body = client.get("/api/v1/cases", headers=_auth(token)).json()
    assert "items" in body and "next_cursor" in body
    assert body["next_cursor"] is None  # single page


def test_invalid_cursor_is_400(client):
    token = _token(client)
    r = client.get("/api/v1/cases?cursor=not-a-valid-cursor", headers=_auth(token))
    assert r.status_code == 400


# --- ETags -------------------------------------------------------------------

def test_etag_returned_and_304_on_match(client):
    token = _token(client)
    case_id = client.post("/api/v1/cases", json={"title_en": "E", "language_primary": "en"},
                          headers=_auth(token)).json()["id"]

    r1 = client.get(f"/api/v1/cases/{case_id}", headers=_auth(token))
    etag = r1.headers.get("ETag")
    assert etag and etag.startswith('W/"')

    r2 = client.get(f"/api/v1/cases/{case_id}",
                    headers={**_auth(token), "If-None-Match": etag})
    assert r2.status_code == 304


def test_etag_mismatch_returns_body(client):
    token = _token(client)
    case_id = client.post("/api/v1/cases", json={"title_en": "E2", "language_primary": "en"},
                          headers=_auth(token)).json()["id"]
    r = client.get(f"/api/v1/cases/{case_id}",
                   headers={**_auth(token), "If-None-Match": 'W/"stale"'})
    assert r.status_code == 200
    assert r.json()["id"] == case_id


# --- idempotency -------------------------------------------------------------

def test_run_idempotency_key_dedupes_job(client):
    token = _token(client)
    case_id = client.post("/api/v1/cases", json={"title_en": "Idem", "language_primary": "en",
                          "area_of_law": "IP"}, headers=_auth(token)).json()["id"]

    h = {**_auth(token), "Idempotency-Key": "abc-123"}
    r1 = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1}, headers=h)
    assert r1.status_code == 200
    job1 = r1.json()["job_id"]

    # Same key → same job, no second run kicked off
    r2 = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1}, headers=h)
    assert r2.json()["job_id"] == job1


def test_rerun_completed_case_without_key_conflicts(client):
    """Without an idempotency key, re-running a case that already completed
    (eager) is a 409 — the status guard applies. The idempotent replay above
    is the only path that returns the original job for a finished case."""
    token = _token(client)
    case_id = client.post("/api/v1/cases", json={"title_en": "NoIdem", "language_primary": "en",
                          "area_of_law": "IP"}, headers=_auth(token)).json()["id"]
    r1 = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1}, headers=_auth(token))
    assert r1.status_code == 200
    r2 = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1}, headers=_auth(token))
    assert r2.status_code == 409
