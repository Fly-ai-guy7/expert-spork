"""Scenario integration tests.

Each test boots a SQLite in-memory DB, loads the statute corpus from the
on-disk JSON files, creates a Case from one of the scenario fixtures, and
runs the full orchestrator pipeline against the MockLLMClient. Asserts the
case completes with a Ruling, Outcome, and all three specialist outputs.

Mocked LLMs only — no API keys, no network, no Docker, no Postgres needed.
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401 — registers all tables
from app.db import Base
from app.models import (
    Case,
    CaseSource,
    CaseStatus,
    Evidence,
    EvidenceKind,
    Fact,
    Party,
    PartyKind,
    PartyRole,
    Statute,
    StatuteArticle,
)
from app.services import orchestrator
from tests.scenarios import SCENARIOS

CORPUS_DIR = Path(__file__).resolve().parent.parent.parent / "corpus"


@pytest.fixture
def sqlite_db():
    """Per-test fresh SQLite + seeded corpus."""
    engine = create_engine("sqlite:///:memory:", future=True)

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db = Session()
    _seed_corpus(db)
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_corpus(db) -> None:
    for path in sorted(CORPUS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        statute = Statute(
            law_number=data["law_number"],
            year=data["year"],
            short_code=data["short_code"],
            title_en=data.get("title_en"),
            title_ar=data.get("title_ar"),
            domain_tags=data.get("domain_tags", []),
        )
        db.add(statute)
        db.flush()
        for art in data.get("articles", []):
            db.add(StatuteArticle(
                statute_id=statute.id,
                article_number=art["number"],
                text_en=art.get("text_en"),
                text_ar=art.get("text_ar"),
                tags=art.get("tags", []),
            ))
    db.commit()


def _create_case_from_fixture(db, fixture: dict) -> uuid.UUID:
    case = Case(
        title_en=fixture.get("title_en"),
        title_ar=fixture.get("title_ar"),
        language_primary=fixture.get("language_primary", "en"),
        area_of_law=fixture.get("area_of_law"),
        source=CaseSource.USER_AUTHORED,
        status=CaseStatus.DRAFT,
    )
    db.add(case)
    db.flush()
    for p in fixture.get("parties", []):
        db.add(Party(
            case_id=case.id,
            role=PartyRole(p["role"]),
            kind=PartyKind(p.get("kind", "NATURAL")),
            name_en=p.get("name_en"), name_ar=p.get("name_ar"),
        ))
    for f in fixture.get("facts", []):
        db.add(Fact(
            case_id=case.id,
            text_en=f.get("text_en"), text_ar=f.get("text_ar"),
            disputed=bool(f.get("disputed", False)),
            order_index=f.get("order_index", 0),
        ))
    for e in fixture.get("evidence", []):
        db.add(Evidence(
            case_id=case.id,
            kind=EvidenceKind(e.get("kind", "DOCUMENT")),
            title_en=e.get("title_en"), title_ar=e.get("title_ar"),
            missing=bool(e.get("missing", False)),
        ))
    db.commit()
    return case.id


@pytest.mark.parametrize("scenario_key", list(SCENARIOS.keys()))
def test_scenario_runs_end_to_end(sqlite_db, mock_llm, scenario_key):
    fixture = SCENARIOS[scenario_key]
    case_id = _create_case_from_fixture(sqlite_db, fixture)

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))

    assert result["status"] == "COMPLETE", f"{scenario_key} did not complete: {result}"

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.status == CaseStatus.COMPLETE

    # Specialist agent outputs persisted
    assert case.procedural_analysis is not None, f"{scenario_key}: procedural_analysis missing"
    assert case.precedent_analysis is not None, f"{scenario_key}: precedent_analysis missing"
    assert case.damages_estimate is not None, f"{scenario_key}: damages_estimate missing"

    # Courtroom agent outputs persisted
    assert case.docket is not None, f"{scenario_key}: docket missing"
    assert case.mediation_proposal is not None, f"{scenario_key}: mediation_proposal missing"
    assert case.cassation_review is not None, f"{scenario_key}: cassation_review missing"
    assert case.cassation_review.get("panel_decision") in ("AFFIRM", "REVERSE", "REMAND")
    assert len(case.cassation_review.get("judges", [])) == 3, "panel should have 3 judges"

    # Expert witness only when there are disputed facts
    has_disputed = any(f.disputed for f in case.facts)
    if has_disputed:
        assert case.expert_testimony is not None, f"{scenario_key}: expert_testimony missing despite disputed facts"

    # Ruling + Outcome produced
    assert case.ruling is not None, f"{scenario_key}: no ruling"
    assert 0 <= case.ruling.plaintiff_success_prob <= 100
    assert case.outcome is not None, f"{scenario_key}: no outcome"

    # Debate produced both sides for both rounds
    prosecution_rounds = {a.round_no for a in case.arguments if a.agent.value == "PROSECUTION"}
    defense_rounds = {a.round_no for a in case.arguments if a.agent.value == "DEFENSE"}
    assert prosecution_rounds == {1, 2}, f"{scenario_key}: prosecution rounds {prosecution_rounds}"
    assert defense_rounds == {1, 2}, f"{scenario_key}: defense rounds {defense_rounds}"

    # Every argument got scored
    for arg in case.arguments:
        assert arg.score is not None, f"{scenario_key}: argument {arg.id} unscored"
        assert 0 <= arg.score.overall <= 100


@pytest.mark.parametrize("trainee_role_str", ["PROSECUTION", "DEFENSE"])
def test_training_mode_pause_and_resume(sqlite_db, mock_llm, trainee_role_str):
    """Trainee plays one side; orchestrator pauses at TRAINEE_TURN, trainee
    submits an argument, pipeline resumes and produces a coaching report."""
    from datetime import datetime

    from app.models import TraineeRole, TrainingSession

    fixture = SCENARIOS["ip"]
    case_id = _create_case_from_fixture(sqlite_db, fixture)
    ts = TrainingSession(
        user_id="trainee",
        case_id=case_id,
        trainee_role=TraineeRole(trainee_role_str),
        difficulty=2,
        started_at=datetime.now(UTC),
    )
    sqlite_db.add(ts)
    sqlite_db.commit()
    ts_id = ts.id

    # Trainee argues every round of their side — loop until pipeline completes.
    # Bound iterations to (max_rounds + 1) to fail loudly on infinite-pause bugs.
    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    pause_count = 0
    while result["status"] == "PAUSED_HIL":
        pause_count += 1
        assert pause_count <= 2, f"too many pauses: {pause_count} — possible loop bug"
        result = asyncio.run(orchestrator.submit_trainee_argument(
            sqlite_db, result["checkpoint_id"],
            content_en=f"My {trainee_role_str} argument round {pause_count} cites 82/2002:113",
            content_ar=None,
            citations=["82/2002:113"],
        ))
    assert result["status"] == "COMPLETE", f"expected complete, got {result}"
    assert pause_count == 2, f"expected 2 trainee turns over 2 rounds, got {pause_count}"

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    trainee_args = [a for a in case.arguments if a.agent.value == "TRAINEE"]
    assert len(trainee_args) >= 1, "trainee argument not persisted"
    assert trainee_args[0].score is not None, "trainee argument unscored"

    ts = sqlite_db.get(TrainingSession, ts_id)
    assert ts.coaching_report is not None
    assert ts.coaching_report.get("grade") in ("A", "B", "C", "D", "F")
    assert ts.completed_at is not None


def test_orchestrator_is_idempotent(sqlite_db, mock_llm):
    """A second run on the same completed case is a no-op (no new arguments)."""
    fixture = SCENARIOS["ip"]
    case_id = _create_case_from_fixture(sqlite_db, fixture)
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    arg_count_before = len(case.arguments)

    # Reset status so run_simulation enters the loop again
    case.status = CaseStatus.RUNNING
    sqlite_db.commit()

    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert len(case.arguments) == arg_count_before, "rerun produced duplicate arguments"
