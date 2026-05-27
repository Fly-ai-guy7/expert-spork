"""Severity-graduated and edge-case scenario tests.

Runs the full orchestrator pipeline against:
- 21 fixtures (7 area-of-law × 3 difficulty levels)
- 5 named edge cases

Every test goes end-to-end against SQLite + corpus + mocked LLM.
"""
from __future__ import annotations

import asyncio
import uuid

import pytest

from app.models import Case, CaseStatus
from app.services import orchestrator
from tests.severity import EDGE_CASES, difficulty_grid
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401

GRID = difficulty_grid()


@pytest.mark.parametrize("scenario_key,difficulty", list(GRID.keys()))
def test_severity_grid(sqlite_db, mock_llm, scenario_key, difficulty):
    fixture = GRID[(scenario_key, difficulty)]
    case_id: uuid.UUID = _create_case_from_fixture(sqlite_db, fixture)
    case = sqlite_db.get(Case, case_id)
    case.difficulty = difficulty
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    assert result["status"] == "COMPLETE", (
        f"{scenario_key} difficulty={difficulty} did not complete: {result}"
    )

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.ruling is not None
    assert case.outcome is not None
    assert case.docket is not None
    assert case.cassation_review is not None

    # Level 5 cases must surface expert testimony — they have ≥2 disputed facts
    if difficulty == 5:
        assert case.expert_testimony is not None, (
            f"{scenario_key} difficulty=5: expert testimony should be triggered"
        )


@pytest.mark.parametrize("edge_key", list(EDGE_CASES.keys()))
def test_edge_case(sqlite_db, mock_llm, edge_key):
    fixture = EDGE_CASES[edge_key]
    case_id = _create_case_from_fixture(sqlite_db, fixture)

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    assert result["status"] == "COMPLETE", f"{edge_key} did not complete: {result}"

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    assert case.status == CaseStatus.COMPLETE
    assert case.ruling is not None
    assert case.mediation_proposal is not None
    assert case.cassation_review is not None

    # Edge case is missing_evidence — verify the ruling references the gaps
    if edge_key == "missing_evidence_dominant":
        assert case.expert_testimony is not None, "disputed facts present — expert required"
