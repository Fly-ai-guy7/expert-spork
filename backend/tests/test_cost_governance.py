"""LLM cost governance: usage accounting, budget enforcement, admin rollup."""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import (
    Case,
    CaseSource,
    CaseStatus,
    LlmUsage,
    Membership,
    Organization,
    Role,
    Statute,
    StatuteArticle,
)
from app.services import orchestrator, usage_recorder
from tests.scenarios import SCENARIOS
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


# --- unit: cost + accounting -------------------------------------------------

def test_cost_usd_known_models():
    # 1M input + 1M output of opus = 15 + 75
    assert usage_recorder.cost_usd("claude-opus-4-7", 1_000_000, 1_000_000) == pytest.approx(90.0)
    assert usage_recorder.cost_usd("deepseek-chat", 1_000_000, 0) == pytest.approx(0.27)


def test_cost_usd_unknown_model_is_zero():
    assert usage_recorder.cost_usd("mystery-model", 1_000_000, 1_000_000) == 0.0


def test_record_and_flush_attributes_rows(sqlite_db):
    org = Organization(name="Flush Org", slug="flush-org")
    sqlite_db.add(org)
    sqlite_db.commit()
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    case = sqlite_db.get(Case, case_id)
    case.org_id = org.id
    sqlite_db.commit()

    usage_recorder.record("claude-opus", "claude-opus-4-7", {"input_tokens": 100, "output_tokens": 50})
    usage_recorder.record("deepseek", "deepseek-chat", {"input_tokens": 200, "output_tokens": 80})

    n = usage_recorder.flush(sqlite_db, org_id=org.id, case_id=case_id)
    assert n == 2

    rows = sqlite_db.query(LlmUsage).filter_by(org_id=org.id).all()
    assert len(rows) == 2
    assert all(r.case_id == case_id for r in rows)
    assert all(r.cost_usd > 0 for r in rows)
    # Flushing again is empty — the sink was drained
    assert usage_recorder.flush(sqlite_db, org_id=org.id, case_id=case_id) == 0


def test_month_to_date_excludes_prior_months(sqlite_db):
    org = Organization(name="MTD Org", slug="mtd-org")
    sqlite_db.add(org)
    sqlite_db.commit()
    org_id = org.id
    # This month
    sqlite_db.add(LlmUsage(org_id=org_id, provider="p", model="m", input_tokens=100, output_tokens=50))
    # Last month — should be excluded
    old = LlmUsage(org_id=org_id, provider="p", model="m", input_tokens=999, output_tokens=999)
    sqlite_db.add(old)
    sqlite_db.flush()
    old.created_at = datetime.now(UTC) - timedelta(days=40)
    sqlite_db.commit()

    assert usage_recorder.month_to_date_tokens(sqlite_db, org_id) == 150


def test_is_over_budget(sqlite_db):
    org = Organization(name="Budget Org", slug="budget-org", monthly_token_budget=100)
    sqlite_db.add(org)
    sqlite_db.commit()

    assert usage_recorder.is_over_budget(sqlite_db, org.id) is False
    sqlite_db.add(LlmUsage(org_id=org.id, provider="p", model="m", input_tokens=80, output_tokens=30))
    sqlite_db.commit()
    assert usage_recorder.is_over_budget(sqlite_db, org.id) is True  # 110 >= 100


def test_no_budget_means_never_over(sqlite_db):
    org = Organization(name="Free Org", slug="free-org", monthly_token_budget=None)
    sqlite_db.add(org)
    sqlite_db.commit()
    sqlite_db.add(LlmUsage(org_id=org.id, provider="p", model="m", input_tokens=10**9, output_tokens=0))
    sqlite_db.commit()
    assert usage_recorder.is_over_budget(sqlite_db, org.id) is False


# --- integration: orchestrator budget gate -----------------------------------

def test_pipeline_aborts_when_org_over_budget(sqlite_db, mock_llm):
    org = Organization(name="Capped", slug="capped", monthly_token_budget=50)
    sqlite_db.add(org)
    sqlite_db.commit()
    # Burn the budget
    sqlite_db.add(LlmUsage(org_id=org.id, provider="p", model="m", input_tokens=60, output_tokens=0))
    sqlite_db.commit()

    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    case = sqlite_db.get(Case, case_id)
    case.org_id = org.id
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))
    assert result["status"] == "FAILED"
    assert result["reason"] == "monthly_token_budget_exceeded"

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.status == CaseStatus.FAILED
    assert case.ruling is None  # never ran


def test_pipeline_runs_when_under_budget(sqlite_db, mock_llm):
    org = Organization(name="Roomy", slug="roomy", monthly_token_budget=10**9)
    sqlite_db.add(org)
    sqlite_db.commit()

    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    case = sqlite_db.get(Case, case_id)
    case.org_id = org.id
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))
    assert result["status"] == "COMPLETE"


# --- API: /api/admin/usage ----------------------------------------------------

@pytest.fixture
def admin_client():
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
    set_context(None)
    yield TestClient(app), Session
    set_context(None)
    engine.dispose()


def _register(client, email="admin@x.com", org="AdminOrg") -> tuple[str, str]:
    r = client.post("/api/auth/register", json={
        "email": email, "password": "12345678", "organization_name": org,
    })
    r.raise_for_status()
    body = r.json()
    return body["access_token"], body["org_id"]


def test_admin_usage_rollup(admin_client):
    client, Session = admin_client
    token, org_id = _register(client)

    with Session() as db:
        oid = uuid.UUID(org_id)
        db.add(LlmUsage(org_id=oid, provider="claude-opus", model="claude-opus-4-7",
                        input_tokens=1000, output_tokens=500, cost_usd=0.0525))
        db.add(LlmUsage(org_id=oid, provider="deepseek", model="deepseek-chat",
                        input_tokens=2000, output_tokens=800, cost_usd=0.00142))
        db.commit()

    r = client.get("/api/admin/usage", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_tokens"] == 1000 + 500 + 2000 + 800
    models = {m["model"] for m in body["by_model"]}
    assert models == {"claude-opus-4-7", "deepseek-chat"}
    assert body["total_cost_usd"] > 0


def test_admin_usage_requires_admin_role(admin_client):
    client, Session = admin_client
    token, _ = _register(client, email="t@x.com", org="TOrg")

    # Demote to TRAINEE; token role is cross-checked against live membership.
    with Session() as db:
        m = db.query(Membership).one()
        m.role = Role.TRAINEE
        db.commit()

    r = client.get("/api/admin/usage", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_usage_is_tenant_scoped(admin_client):
    client, Session = admin_client
    a_token, a_org = _register(client, email="a@x.com", org="OrgA")
    _b_token, b_org = _register(client, email="b@x.com", org="OrgB")

    with Session() as db:
        db.add(LlmUsage(org_id=uuid.UUID(b_org), provider="p", model="m",
                        input_tokens=9999, output_tokens=0, cost_usd=1.0))
        db.commit()

    # A's rollup must not see B's usage
    r = client.get("/api/admin/usage", headers={"Authorization": f"Bearer {a_token}"})
    assert r.json()["total_tokens"] == 0
