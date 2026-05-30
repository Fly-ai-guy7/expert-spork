"""Audit trail tests.

Covers the recorder helper, the mutation hooks (register / case create /
case run / trainee submit / switch-org), the admin endpoint, and cross-org
isolation of the trail.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.tenant import set_context
from app.db import Base, get_db
from app.main import create_app
from app.models import AuditEvent, Membership, Role


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
    yield TestClient(app), Session
    set_context(None)
    engine.dispose()


def _register(client, email="a@x.com", org="Org") -> tuple[str, str]:
    r = client.post("/api/v1/auth/register", json={
        "email": email, "password": "12345678", "organization_name": org,
    })
    r.raise_for_status()
    body = r.json()
    return body["access_token"], body["org_id"]


def _auth(t: str) -> dict:
    return {"Authorization": f"Bearer {t}"}


def _by_action(rows, action):
    return [r for r in rows if r.action == action]


# --- mutation hooks ----------------------------------------------------------

def test_register_emits_audit_event(app_client):
    client, Session = app_client
    _register(client)
    with Session() as db:
        events = db.execute(select(AuditEvent)).scalars().all()
        regs = _by_action(events, "USER_REGISTER")
        assert len(regs) == 1
        assert regs[0].actor_email == "a@x.com"
        assert regs[0].after["email"] == "a@x.com"
        assert regs[0].resource_type == "user"


def test_case_create_and_run_audited(app_client):
    client, Session = app_client
    token, _ = _register(client)

    case_id = client.post("/api/v1/cases", json={
        "title_en": "Audited", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                headers=_auth(token)).raise_for_status()

    with Session() as db:
        events = db.execute(select(AuditEvent)).scalars().all()
        actions = [e.action for e in events]
        assert "CASE_CREATE" in actions
        assert "CASE_RUN" in actions
        create = _by_action(events, "CASE_CREATE")[0]
        run = _by_action(events, "CASE_RUN")[0]
        assert create.resource_id == case_id
        assert run.resource_id == case_id
        assert run.after["max_rounds"] == 1
        assert run.after["job_id"]


def test_trainee_submit_audited(app_client):
    from datetime import UTC, datetime

    from app.models import TraineeRole, TrainingSession
    client, Session = app_client
    token, _ = _register(client)

    case_id = client.post("/api/v1/cases", json={
        "title_en": "T", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]

    with Session() as db:
        ts = TrainingSession(
            user_id="trainee", case_id=uuid.UUID(case_id),
            trainee_role=TraineeRole.DEFENSE, difficulty=2,
            started_at=datetime.now(UTC),
        )
        db.add(ts)
        db.commit()

    # Run pipeline to hit the trainee pause
    run = client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                      headers=_auth(token)).json()
    assert run["status"] == "PAUSED"

    with Session() as db:
        from app.models import HilCheckpoint, HilStage, HilStatus
        cp = db.execute(
            select(HilCheckpoint).where(
                HilCheckpoint.case_id == uuid.UUID(case_id),
                HilCheckpoint.stage == HilStage.TRAINEE_TURN,
                HilCheckpoint.status == HilStatus.PENDING,
            )
        ).scalars().first()
        cp_id = str(cp.id)

    client.post(f"/api/v1/hil/{cp_id}/submit-trainee", json={
        "content_en": "argument", "citations": ["82/2002:115"],
    }, headers=_auth(token)).raise_for_status()

    with Session() as db:
        events = db.execute(select(AuditEvent)).scalars().all()
        submits = _by_action(events, "TRAINEE_SUBMIT")
        assert len(submits) == 1
        assert submits[0].after["checkpoint_id"] == cp_id
        assert submits[0].after["citation_count"] == 1


def test_switch_org_audited(app_client):
    """Multi-org user: register two orgs from the same email won't work
    (dup email), so we wire a second membership directly."""
    from app.models import Organization
    client, Session = app_client
    a_token, a_org = _register(client)

    # Add a second org + membership for this user
    with Session() as db:
        from app.models import User
        u = db.execute(select(User).where(User.email == "a@x.com")).scalar_one()
        org2 = Organization(name="Second", slug="second")
        db.add(org2)
        db.flush()
        db.add(Membership(user_id=u.id, org_id=org2.id, role=Role.ADMIN))
        db.commit()
        org2_id = str(org2.id)

    r = client.post("/api/v1/auth/switch-org", json={"org_id": org2_id},
                    headers=_auth(a_token))
    assert r.status_code == 200

    with Session() as db:
        events = db.execute(
            select(AuditEvent).where(AuditEvent.action == "SWITCH_ORG")
        ).scalars().all()
        assert len(events) == 1
        assert events[0].resource_id == org2_id


# --- admin endpoint ---------------------------------------------------------

def test_admin_audit_endpoint_lists_events(app_client):
    client, _ = app_client
    token, _ = _register(client)

    case_id = client.post("/api/v1/cases", json={
        "title_en": "X", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]
    client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                headers=_auth(token))

    r = client.get("/api/v1/admin/audit", headers=_auth(token))
    assert r.status_code == 200, r.text
    body = r.json()
    actions = [e["action"] for e in body["items"]]
    assert "CASE_RUN" in actions
    assert "CASE_CREATE" in actions
    assert "USER_REGISTER" in actions


def test_admin_audit_filter_by_action(app_client):
    client, _ = app_client
    token, _ = _register(client)
    case_id = client.post("/api/v1/cases", json={
        "title_en": "Y", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(token)).json()["id"]
    client.post(f"/api/v1/cases/{case_id}/run", json={"max_rounds": 1},
                headers=_auth(token))

    r = client.get("/api/v1/admin/audit?action=CASE_RUN", headers=_auth(token))
    assert r.status_code == 200
    items = r.json()["items"]
    assert items
    assert all(e["action"] == "CASE_RUN" for e in items)


def test_admin_audit_is_tenant_scoped(app_client):
    client, _ = app_client
    a_token, _ = _register(client, email="a@x.com", org="OrgA")
    b_token, _ = _register(client, email="b@x.com", org="OrgB")

    # B creates a case (audited)
    client.post("/api/v1/cases", json={
        "title_en": "BCase", "language_primary": "en", "area_of_law": "IP",
    }, headers=_auth(b_token)).raise_for_status()

    # A's audit feed must not contain B's CASE_CREATE
    a_feed = client.get("/api/v1/admin/audit", headers=_auth(a_token)).json()["items"]
    actors = {e["actor_email"] for e in a_feed}
    assert "b@x.com" not in actors


def test_admin_audit_requires_admin(app_client):
    client, Session = app_client
    token, _ = _register(client, email="t@x.com", org="TOrg")

    with Session() as db:
        m = db.query(Membership).one()
        m.role = Role.TRAINEE
        db.commit()

    r = client.get("/api/v1/admin/audit", headers=_auth(token))
    assert r.status_code == 403
