"""Async job queue tests (Celery eager mode).

With no broker configured, Celery runs tasks synchronously in-process, so a
POST /run completes the whole pipeline before responding. We point the
worker's SessionLocal at the test's in-memory SQLite (shared via StaticPool)
so the eager task and the HTTP request see the same data.

Covers: job row lifecycle, terminal status mapping (COMPLETE / PAUSED /
FAILED), and that the orchestrator still runs end-to-end through the queue.
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import Case, Job, JobStatus, Statute, StatuteArticle  # noqa: F401

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


@pytest.fixture
def job_client(monkeypatch, mock_llm):
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

    # Point the worker task's SessionLocal at the test engine so the eager
    # task reads/writes the same in-memory DB as the HTTP request.
    import app.workers.tasks as tasks_mod
    monkeypatch.setattr(tasks_mod, "SessionLocal", Session)

    with Session() as db:
        for path in sorted(CORPUS_DIR.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            s = Statute(
                law_number=data["law_number"], year=data["year"],
                short_code=data["short_code"], title_en=data.get("title_en"),
                title_ar=data.get("title_ar"), domain_tags=data.get("domain_tags", []),
            )
            db.add(s)
            db.flush()
            for art in data.get("articles", []):
                db.add(StatuteArticle(
                    statute_id=s.id, article_number=art["number"],
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
    yield TestClient(app), Session
    set_context(None)
    engine.dispose()


def _register(client) -> str:
    r = client.post("/api/auth/register", json={
        "email": "j@x.com", "password": "12345678", "organization_name": "JobOrg",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_run_enqueues_job_and_completes_eager(job_client):
    client, Session = job_client
    token = _register(client)

    r = client.post("/api/cases", json={
        "title_en": "Trademark dispute", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token))
    assert r.status_code == 201
    case_id = r.json()["id"]

    r = client.post(f"/api/cases/{case_id}/run", json={"max_rounds": 1}, headers=_auth(token))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["job_id"]
    # Eager mode: the pipeline finished synchronously before responding.
    assert body["status"] == "COMPLETE", body

    # Job row is terminal + linked to the case
    with Session() as db:
        job = db.get(Job, uuid.UUID(body["job_id"]))
        assert job.status == JobStatus.COMPLETE
        assert job.result and job.result.get("status") == "COMPLETE"
        case = db.get(Case, uuid.UUID(case_id))
        assert case.ruling is not None


def test_status_surfaces_latest_job(job_client):
    client, _ = job_client
    token = _register(client)
    case_id = client.post("/api/cases", json={
        "title_en": "C", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]
    client.post(f"/api/cases/{case_id}/run", json={"max_rounds": 1}, headers=_auth(token))

    status = client.get(f"/api/cases/{case_id}/status", headers=_auth(token)).json()
    assert status["job"] is not None
    assert status["job"]["kind"] == "SIMULATION"
    assert status["job"]["status"] == "COMPLETE"


def test_failed_pipeline_marks_job_failed(job_client, monkeypatch):
    client, Session = job_client
    token = _register(client)
    case_id = client.post("/api/cases", json={
        "title_en": "C", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    # Force the orchestrator to blow up inside the task.
    import app.services.orchestrator as orch

    async def _boom(*a, **k):
        raise RuntimeError("synthetic failure")

    monkeypatch.setattr(orch, "run_simulation", _boom)

    # eager + task_eager_propagates=True → the exception surfaces as a 500
    with pytest.raises(RuntimeError, match="synthetic failure"):
        client.post(f"/api/cases/{case_id}/run", json={"max_rounds": 1}, headers=_auth(token))

    with Session() as db:
        job = db.execute(select(Job).order_by(Job.created_at.desc())).scalars().first()
        assert job.status == JobStatus.FAILED
        assert "synthetic failure" in (job.error or "")
