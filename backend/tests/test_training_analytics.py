"""Cross-session analytics tests.

Seeds a small set of completed TrainingSessions (no orchestrator run — we
construct realistic coaching_report payloads directly) and exercises:

- progress(user) — averages, weakest dim, trend direction, areas practiced
- cohort()      — grade distribution, top missed statutes, by-area averages
- recommendations(user) — explore unpracticed areas + focus on weakest dim
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.models import Case, CaseSource, CaseStatus, TraineeRole, TrainingSession
from app.services import training_analytics
from tests.test_scenarios import sqlite_db  # noqa: F401


def _mk_case(db, area: str, title: str = "T") -> Case:
    case = Case(
        title_en=title,
        language_primary="en",
        area_of_law=area,
        source=CaseSource.AI_GENERATED,
        status=CaseStatus.COMPLETE,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def _mk_session(
    db,
    user_id: str,
    case: Case,
    *,
    total_score: float,
    grade: str,
    per_round_dims: dict[str, float],
    missed_citations: list[str] | None = None,
    difficulty: int = 2,
    completed_offset_days: int = 0,
) -> TrainingSession:
    now = datetime.now(timezone.utc) + timedelta(days=completed_offset_days)
    ts = TrainingSession(
        user_id=user_id,
        case_id=case.id,
        trainee_role=TraineeRole.PROSECUTION,
        difficulty=difficulty,
        started_at=now,
        completed_at=now,
        total_score=total_score,
        coaching_report={
            "grade": grade,
            "total_score": total_score,
            "per_round": [
                {
                    "round_no": 1,
                    "factual": per_round_dims.get("factual", 70),
                    "provable": per_round_dims.get("provable", 70),
                    "unbiased": per_round_dims.get("unbiased", 70),
                    "legal_law_based": per_round_dims.get("legal_law_based", 70),
                    "overall": total_score,
                }
            ],
            "missed_citations": missed_citations or [],
            "evidence_gaps_to_address": [],
            "weak_patterns": [],
        },
    )
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return ts


def test_progress_empty_for_unknown_user(sqlite_db):
    result = training_analytics.progress(sqlite_db, "nobody")
    assert result["sessions_completed"] == 0
    assert result["average_score"] == 0.0
    assert result["weakest_dimension"] is None
    assert result["trend"]["direction"] == "FLAT"


def test_progress_aggregates_one_trainee(sqlite_db):
    ip = _mk_case(sqlite_db, "IP")
    labour = _mk_case(sqlite_db, "LABOUR")
    _mk_session(
        sqlite_db, "alice", ip,
        total_score=60, grade="C",
        per_round_dims={"factual": 80, "provable": 80, "unbiased": 80, "legal_law_based": 30},
        completed_offset_days=-3,
    )
    _mk_session(
        sqlite_db, "alice", labour,
        total_score=75, grade="B",
        per_round_dims={"factual": 85, "provable": 80, "unbiased": 75, "legal_law_based": 40},
        completed_offset_days=-1,
    )

    result = training_analytics.progress(sqlite_db, "alice")
    assert result["sessions_completed"] == 2
    assert 67 <= result["average_score"] <= 68
    # legal_law_based is by far the lowest dimension across both sessions
    assert result["weakest_dimension"] == "legal_law_based"
    assert result["weakest_dimension_label"] == "Statute-based grounding"
    areas = {a["area_of_law"] for a in result["areas_practiced"]}
    assert areas == {"IP", "LABOUR"}


def test_progress_trend_improving(sqlite_db):
    ip = _mk_case(sqlite_db, "IP")
    for i, score in enumerate([40, 50, 55, 80, 85]):
        _mk_session(
            sqlite_db, "bob", ip,
            total_score=score, grade="C",
            per_round_dims={"factual": score},
            completed_offset_days=-5 + i,
        )
    result = training_analytics.progress(sqlite_db, "bob")
    # recent 3 avg = (55+80+85)/3 ≈ 73; all-time = 62 — should flag IMPROVING
    assert result["trend"]["direction"] == "IMPROVING"
    assert result["trend"]["recent_avg"] > result["trend"]["all_time_avg"]


def test_cohort_aggregates_across_trainees(sqlite_db):
    ip = _mk_case(sqlite_db, "IP")
    labour = _mk_case(sqlite_db, "LABOUR")
    _mk_session(sqlite_db, "alice", ip, total_score=90, grade="A",
                per_round_dims={}, missed_citations=["82/2002:115"])
    _mk_session(sqlite_db, "bob", ip, total_score=72, grade="B",
                per_round_dims={}, missed_citations=["82/2002:115", "82/2002:113"])
    _mk_session(sqlite_db, "carol", labour, total_score=45, grade="D",
                per_round_dims={}, missed_citations=["12/2003:82"])

    result = training_analytics.cohort(sqlite_db)
    assert result["trainees"] == 3
    assert result["sessions_completed"] == 3
    assert result["grade_distribution"]["A"] == 1
    assert result["grade_distribution"]["B"] == 1
    assert result["grade_distribution"]["D"] == 1
    # 82/2002:115 missed by 2 trainees — should top the list
    top = result["most_missed_statutes"][0]
    assert top["citation"] == "82/2002:115"
    assert top["missed_by_n_trainees"] == 2
    areas = {row["area_of_law"]: row["average_score"] for row in result["average_score_by_area"]}
    assert areas["IP"] == pytest.approx(81.0)
    assert areas["LABOUR"] == pytest.approx(45.0)


def test_recommendations_suggests_unpracticed_and_weakness(sqlite_db):
    ip = _mk_case(sqlite_db, "IP")
    _mk_session(
        sqlite_db, "dave", ip,
        total_score=85, grade="A",
        per_round_dims={"factual": 95, "provable": 90, "unbiased": 90, "legal_law_based": 65},
        difficulty=3,
    )
    result = training_analytics.recommendations(sqlite_db, "dave")
    # Strong avg → bump difficulty
    assert result["suggested_difficulty"] == 4
    # Unpracticed areas should be present
    assert "LABOUR" in result["unpracticed_areas"]
    assert "IP" not in result["unpracticed_areas"]
    priorities = {r["priority"] for r in result["recommendations"]}
    assert {"EXPLORE", "FOCUS", "CHALLENGE"} <= priorities
    # Weakest dim is legal_law_based → FOCUS rec should point to IP
    focus = next(r for r in result["recommendations"] if r["priority"] == "FOCUS")
    assert focus["area_of_law"] == "IP"


def test_recommendations_empty_for_new_user(sqlite_db):
    result = training_analytics.recommendations(sqlite_db, "first-day")
    assert result["sessions_completed"] if "sessions_completed" in result else True
    # No completed sessions → all 7 areas unpracticed, 2 EXPLORE recs, no FOCUS
    assert len(result["unpracticed_areas"]) == 7
    priorities = [r["priority"] for r in result["recommendations"]]
    assert priorities.count("EXPLORE") == 2
    assert "FOCUS" not in priorities


def test_recommendations_drops_difficulty_when_struggling(sqlite_db):
    ip = _mk_case(sqlite_db, "IP")
    _mk_session(
        sqlite_db, "eve", ip,
        total_score=35, grade="F",
        per_round_dims={"factual": 30, "provable": 35, "unbiased": 40, "legal_law_based": 35},
        difficulty=4,
    )
    result = training_analytics.recommendations(sqlite_db, "eve")
    assert result["suggested_difficulty"] == 3, "should step down after low score"
