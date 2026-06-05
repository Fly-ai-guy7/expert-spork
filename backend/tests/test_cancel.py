"""Cooperative job cancellation.

Cancel sets a flag on the case; the orchestrator checks at start + each
debate round boundary and halts with status CANCELLED. Verifies:

- cancel before run -> next /run is a no-op (CANCELLED pipeline result)
- cancel during run (eager path) -> orchestrator catches the flag at the
  per-round boundary
- cancel is audited
- cancel is tenant-scoped (404 cross-org via _load_case)
- cancel on a COMPLETE case is a benign no-op
"""
from __future__ import annotations

import asyncio
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import AuditEvent, Case, CaseStatus
from app.services import orchestrator
from tests.scenarios import SCENARIOS
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401


@pytest.fixture
def app_client(monkeypatch, mock_llm):
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
    yield TestClient(app), Session
    set_context(None)
    engine.dispose()


def _register(client, email="c@x.com", org="COrg") -> str:
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "12345678", "organization_name": org,
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


# --- orchestrator-level cancellation ----------------------------------------

def test_orchestrator_short_circuits_when_cancelled_before_start(sqlite_db, mock_llm):
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    case = sqlite_db.get(Case, case_id)
    case.cancel_requested = True
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    assert result["status"] == "CANCELLED"
    assert result["reason"] == "cancelled"

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.status == CaseStatus.CANCELLED
    assert case.ruling is None  # never ran


def test_orchestrator_halts_mid_pipeline_on_cancel_flag(sqlite_db, mock_llm, monkeypatch):
    """Flip cancel_requested mid-run by hooking the first agent. The check
    at the top of the round-2 loop iteration should bail."""
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])

    # Wrap _run_agent so that after the first prosecution argument lands,
    # the cancel flag flips on. The next round's cancellation check halts.
    original = orchestrator._run_agent
    flipped = {"done": False}

    async def _wrapped(db, agent, ctx, role, round_no, debate_round_id):
        out = await original(db, agent, ctx, role, round_no, debate_round_id)
        if not flipped["done"] and role.value == "PROSECUTION" and round_no == 1:
            case = db.get(Case, case_id)
            case.cancel_requested = True
            db.commit()
            flipped["done"] = True
        return out

    monkeypatch.setattr(orchestrator, "_run_agent", _wrapped)

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=3))
    assert result["status"] == "CANCELLED"
    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.status == CaseStatus.CANCELLED
    # Round 1 ran; round 2 must NOT have started.
    p_rounds = {a.round_no for a in case.arguments if a.agent.value == "PROSECUTION"}
    assert 2 not in p_rounds


# --- API endpoint -----------------------------------------------------------

def test_cancel_endpoint_sets_flag(app_client):
    client, Session = app_client
    token = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Cancellable", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    r = client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token))
    assert r.status_code == 200, r.text
    assert r.json()["cancel_requested"] is True

    with Session() as db:
        case = db.get(Case, uuid.UUID(case_id))
        assert case.cancel_requested is True


def test_cancel_then_run_yields_cancelled_pipeline(app_client):
    client, _ = app_client
    token = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Doomed", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token)).raise_for_status()

    # Eager run sees the flag immediately and returns CANCELLED.
    r = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                    headers=_auth(token))
    assert r.status_code == 200
    # Check via status endpoint
    status = client.get(f"/api/v1/cases/{case_id}/status", headers=_auth(token)).json()
    assert status["status"] == "CANCELLED"


def test_cancel_is_audited(app_client):
    client, Session = app_client
    token = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Audit me", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token)).raise_for_status()

    with Session() as db:
        events = db.execute(
            select(AuditEvent).where(AuditEvent.action == "CASE_CANCEL")
        ).scalars().all()
        assert len(events) == 1
        assert events[0].resource_id == case_id


def test_cancel_is_tenant_scoped(app_client):
    client, _ = app_client
    a_token = _register(client, email="a@x.com", org="OrgA")
    case_id = client.post("/api/v1/cases", json={
        "title_en": "A only", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(a_token)).json()["id"]

    b_token = _register(client, email="b@x.com", org="OrgB")
    # Org B can't see or cancel org A's case
    r = client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(b_token))
    assert r.status_code == 404


def test_cancel_on_completed_case_is_noop(app_client):
    client, _ = app_client
    token = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Done already", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    # Eager-run to completion first
    client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                headers=_auth(token)).raise_for_status()

    # Now cancel — should not flip status, just report current state
    r = client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token))
    assert r.status_code == 200
    assert r.json()["status"] == "COMPLETE"


def test_cancel_is_idempotent(app_client):
    client, _ = app_client
    token = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Twice", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token)).raise_for_status()
    r2 = client.post(f"/api/v1/cases/{case_id}/cancel", headers=_auth(token))
    assert r2.status_code == 200
    assert r2.json()["cancel_requested"] is True
