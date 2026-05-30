"""Tier 1.2 SSE event stream.

Verifies the in-memory event bus + the GET /events SSE endpoint, including
the orchestrator publishing terminal events from a real run.
"""
from __future__ import annotations

import asyncio
import json
import uuid
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
from app.services import event_bus, orchestrator
from tests.scenarios import SCENARIOS
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


@pytest.fixture(autouse=True)
def _reset_bus():
    event_bus.reset()
    yield
    event_bus.reset()


# --- bus unit ----------------------------------------------------------------

async def test_publish_then_subscribe_replays_history():
    case_id = uuid.uuid4()
    event_bus.publish(case_id, {"status": "running", "stage": "started"})
    event_bus.publish(case_id, {"status": "complete"})

    collected = []
    async for evt in event_bus.subscribe(case_id, replay=True, timeout_seconds=1):
        collected.append(evt)

    assert [e["status"] for e in collected] == ["running", "complete"]
    # Terminal event closed the iterator without waiting for the timeout
    assert all("ts" in e for e in collected)


async def test_subscribe_tails_live_events_and_closes_on_terminal():
    case_id = uuid.uuid4()

    async def _publisher():
        # Give the subscriber a tick to register, then push events.
        await asyncio.sleep(0.02)
        event_bus.publish(case_id, {"status": "running", "stage": "evidence"})
        await asyncio.sleep(0.01)
        event_bus.publish(case_id, {"status": "complete"})

    task = asyncio.create_task(_publisher())
    collected = []
    async for evt in event_bus.subscribe(case_id, replay=False, timeout_seconds=2):
        collected.append(evt)
    await task

    assert [e["status"] for e in collected] == ["running", "complete"]


async def test_subscribe_returns_on_idle_timeout():
    case_id = uuid.uuid4()
    collected = []
    async for evt in event_bus.subscribe(case_id, replay=False, timeout_seconds=0.05):
        collected.append(evt)
    # No events published, terminal never arrived — closes cleanly on timeout
    assert collected == []


def test_reset_clears_state():
    case_id = uuid.uuid4()
    event_bus.publish(case_id, {"status": "running"})
    event_bus.reset()
    # New channel after reset has empty history
    ch = event_bus._channel(case_id)
    assert list(ch.history) == []


# --- orchestrator integration ------------------------------------------------

def test_orchestrator_publishes_terminal_complete_event(sqlite_db, mock_llm):
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))

    history = list(event_bus._channel(case_id).history)
    statuses = [e["status"] for e in history]
    assert statuses[0] == "running"
    assert "complete" in statuses


def test_orchestrator_publishes_paused_event_for_trainee_turn(sqlite_db, mock_llm):
    from datetime import UTC, datetime

    from app.models import TraineeRole, TrainingSession

    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    ts = TrainingSession(
        user_id="t", case_id=case_id, trainee_role=TraineeRole.DEFENSE,
        difficulty=2, started_at=datetime.now(UTC),
    )
    sqlite_db.add(ts)
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))
    assert result["status"] == "PAUSED_HIL"

    history = list(event_bus._channel(case_id).history)
    statuses = [e["status"] for e in history]
    assert "paused" in statuses
    paused = next(e for e in history if e["status"] == "paused")
    assert paused["side"] == "DEFENSE"


# --- SSE endpoint ------------------------------------------------------------

@pytest.fixture
def sse_client():
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
    yield TestClient(app)
    set_context(None)
    engine.dispose()


def _token(client) -> str:
    r = client.post("/api/auth/register", json={
        "email": "s@x.com", "password": "12345678", "organization_name": "SOrg",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


def test_sse_endpoint_streams_replayed_events(sse_client):
    token = _token(sse_client)
    case_id = sse_client.post(
        "/api/v1/cases", json={"title_en": "SSE", "language_primary": "en", "area_of_law": "IP"},
        headers=_auth(token),
    ).json()["id"]

    # Pre-publish events into the bus, including a terminal one so the SSE
    # subscriber closes the stream after replay (no waiting on the idle timeout).
    event_bus.publish(case_id, {"status": "running", "stage": "evidence"})
    event_bus.publish(case_id, {"status": "complete"})

    with sse_client.stream(
        "GET", f"/api/v1/cases/{case_id}/events", headers=_auth(token)
    ) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        events = []
        for line in r.iter_lines():
            if line.startswith("data: "):
                events.append(json.loads(line[len("data: "):]))
                if events[-1].get("status") in {"complete", "failed"}:
                    break

    assert [e["status"] for e in events] == ["running", "complete"]


def test_sse_endpoint_requires_auth(sse_client):
    r = sse_client.get(f"/api/v1/cases/{uuid.uuid4()}/events")
    assert r.status_code == 401


def test_sse_endpoint_tenant_scoped(sse_client):
    a_token = _token(sse_client)
    case_id = sse_client.post(
        "/api/v1/cases", json={"title_en": "A", "language_primary": "en", "area_of_law": "IP"},
        headers=_auth(a_token),
    ).json()["id"]

    # Org B can't reach org A's SSE stream → 404 (no existence leak)
    sse_client.post("/api/auth/register", json={
        "email": "b@x.com", "password": "12345678", "organization_name": "OrgB",
    }).raise_for_status()
    b_token = sse_client.post("/api/auth/login", json={
        "email": "b@x.com", "password": "12345678",
    }).json()["access_token"]

    r = sse_client.get(f"/api/v1/cases/{case_id}/events", headers=_auth(b_token))
    assert r.status_code == 404
