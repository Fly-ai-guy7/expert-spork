"""Cross-session analytics for trainees and instructors.

Aggregates over the `training_sessions` table + each session's `coaching_report`
JSON. Three views:

- progress(user_id)     — one trainee's improvement signal over time
- cohort()              — instructor view across all trainees
- recommendations(uid)  — what to practice next, derived from weak dimensions
                          and unpracticed areas of law
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import TrainingSession

DIMENSIONS = ("factual", "provable", "unbiased", "legal_law_based")
DIMENSION_LABEL = {
    "factual": "Factual grounding",
    "provable": "Evidence-supported reasoning",
    "unbiased": "Argumentation quality",
    "legal_law_based": "Statute-based grounding",
}
# 7 area-of-law tags from tests/scenarios.py
ALL_AREAS = ("IP", "LABOUR", "COMMERCIAL", "CONSUMER", "PRIVACY", "CORPORATE", "CIVIL")


def _completed_sessions(db: Session, user_id: str | None = None) -> list[TrainingSession]:
    stmt = (
        select(TrainingSession)
        .options(selectinload(TrainingSession.case))
        .where(TrainingSession.completed_at.is_not(None))
        .order_by(TrainingSession.completed_at.asc())
    )
    if user_id:
        stmt = stmt.where(TrainingSession.user_id == user_id)
    return list(db.execute(stmt).scalars().all())


def _dimension_averages(sessions: list[TrainingSession]) -> dict[str, float]:
    sums = {d: 0.0 for d in DIMENSIONS}
    counts = {d: 0 for d in DIMENSIONS}
    for s in sessions:
        report = s.coaching_report or {}
        for r in report.get("per_round", []) or []:
            for d in DIMENSIONS:
                v = r.get(d)
                if isinstance(v, (int, float)):
                    sums[d] += float(v)
                    counts[d] += 1
    return {d: (sums[d] / counts[d]) if counts[d] else 0.0 for d in DIMENSIONS}


def progress(db: Session, user_id: str) -> dict[str, Any]:
    """One trainee's learning signal: where they are, where they're weak,
    where they're trending."""
    sessions = _completed_sessions(db, user_id)
    if not sessions:
        return {
            "user_id": user_id,
            "sessions_completed": 0,
            "average_score": 0.0,
            "dimension_averages": {d: 0.0 for d in DIMENSIONS},
            "weakest_dimension": None,
            "areas_practiced": [],
            "trend": {"recent_avg": 0.0, "all_time_avg": 0.0, "direction": "FLAT"},
            "recent_sessions": [],
        }

    scores = [s.total_score for s in sessions if s.total_score is not None]
    avg = sum(scores) / len(scores) if scores else 0.0
    dim_avgs = _dimension_averages(sessions)
    weakest = min(dim_avgs.items(), key=lambda kv: kv[1])[0] if any(dim_avgs.values()) else None

    areas: dict[str, dict[str, Any]] = {}
    for s in sessions:
        area = (s.case.area_of_law if s.case else None) or "UNKNOWN"
        bucket = areas.setdefault(area, {"area_of_law": area, "sessions": 0, "score_sum": 0.0})
        bucket["sessions"] += 1
        if s.total_score is not None:
            bucket["score_sum"] += s.total_score
    for b in areas.values():
        b["average_score"] = b["score_sum"] / b["sessions"] if b["sessions"] else 0.0
        del b["score_sum"]

    recent_n = min(3, len(scores))
    recent_avg = sum(scores[-recent_n:]) / recent_n if recent_n else 0.0
    if recent_avg > avg + 2:
        direction = "IMPROVING"
    elif recent_avg < avg - 2:
        direction = "REGRESSING"
    else:
        direction = "FLAT"

    return {
        "user_id": user_id,
        "sessions_completed": len(sessions),
        "average_score": avg,
        "dimension_averages": dim_avgs,
        "weakest_dimension": weakest,
        "weakest_dimension_label": DIMENSION_LABEL.get(weakest) if weakest else None,
        "areas_practiced": sorted(areas.values(), key=lambda x: -x["sessions"]),
        "trend": {
            "recent_avg": recent_avg,
            "all_time_avg": avg,
            "direction": direction,
        },
        "recent_sessions": [
            {
                "id": str(s.id),
                "case_id": str(s.case_id),
                "area_of_law": s.case.area_of_law if s.case else None,
                "difficulty": s.difficulty,
                "grade": (s.coaching_report or {}).get("grade"),
                "total_score": s.total_score,
                "completed_at": s.completed_at,
            }
            for s in sessions[-5:][::-1]
        ],
    }


def cohort(db: Session) -> dict[str, Any]:
    """Instructor view across all trainees."""
    sessions = _completed_sessions(db)
    if not sessions:
        return {
            "trainees": 0,
            "sessions_completed": 0,
            "grade_distribution": {g: 0 for g in ("A", "B", "C", "D", "F")},
            "dimension_averages": {d: 0.0 for d in DIMENSIONS},
            "average_score_by_area": [],
            "most_missed_statutes": [],
        }

    grade_counts = Counter((s.coaching_report or {}).get("grade") for s in sessions)
    grade_dist = {g: int(grade_counts.get(g, 0)) for g in ("A", "B", "C", "D", "F")}

    by_area: dict[str, list[float]] = {}
    for s in sessions:
        area = (s.case.area_of_law if s.case else None) or "UNKNOWN"
        if s.total_score is not None:
            by_area.setdefault(area, []).append(s.total_score)
    area_rows = [
        {
            "area_of_law": a,
            "sessions": len(scores),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
        }
        for a, scores in sorted(by_area.items())
    ]

    missed_counter: Counter = Counter()
    for s in sessions:
        for ref in (s.coaching_report or {}).get("missed_citations", []) or []:
            missed_counter[ref] += 1
    top_missed = [
        {"citation": ref, "missed_by_n_trainees": n}
        for ref, n in missed_counter.most_common(10)
    ]

    return {
        "trainees": len({s.user_id for s in sessions}),
        "sessions_completed": len(sessions),
        "grade_distribution": grade_dist,
        "dimension_averages": _dimension_averages(sessions),
        "average_score_by_area": area_rows,
        "most_missed_statutes": top_missed,
    }


def recommendations(db: Session, user_id: str) -> dict[str, Any]:
    """What to practice next.

    Strategy:
    1. Areas of law the trainee has never touched → 'EXPLORE' priority.
    2. Their weakest dimension → suggest 1 case in the area where that
       dimension is most exercised (heuristic: LABOUR for procedural,
       IP for legal_law_based, etc).
    3. Next-difficulty bump in their strongest area.
    """
    sessions = _completed_sessions(db, user_id)
    practiced_areas = {(s.case.area_of_law if s.case else None) for s in sessions}
    practiced_areas.discard(None)
    unpracticed = [a for a in ALL_AREAS if a not in practiced_areas]

    suggested_difficulty = 2
    if sessions:
        avg = sum(s.total_score or 0 for s in sessions) / len(sessions)
        last_diff = sessions[-1].difficulty or 2
        if avg >= 75 and last_diff < 5:
            suggested_difficulty = last_diff + 1
        elif avg < 50 and last_diff > 1:
            suggested_difficulty = last_diff - 1
        else:
            suggested_difficulty = last_diff

    recs: list[dict[str, Any]] = []
    for area in unpracticed[:2]:
        recs.append({
            "area_of_law": area,
            "difficulty": min(suggested_difficulty, 3),
            "reason": f"You haven't practiced {area} yet — broaden your coverage.",
            "priority": "EXPLORE",
        })

    if sessions:
        dim_avgs = _dimension_averages(sessions)
        weakest = min(dim_avgs.items(), key=lambda kv: kv[1])[0]
        focus_area_by_dim = {
            "factual": "CIVIL",
            "provable": "CONSUMER",
            "unbiased": "COMMERCIAL",
            "legal_law_based": "IP",
        }
        focus = focus_area_by_dim.get(weakest, "CIVIL")
        recs.append({
            "area_of_law": focus,
            "difficulty": suggested_difficulty,
            "reason": (
                f"Your weakest dimension is {DIMENSION_LABEL.get(weakest, weakest)} "
                f"({dim_avgs[weakest]:.0f}/100). Practice in {focus} drills this skill."
            ),
            "priority": "FOCUS",
        })

        # Difficulty bump in their strongest area
        by_area: dict[str, list[float]] = {}
        for s in sessions:
            area = (s.case.area_of_law if s.case else None) or "UNKNOWN"
            if s.total_score is not None:
                by_area.setdefault(area, []).append(s.total_score)
        if by_area:
            strongest = max(
                by_area.items(),
                key=lambda kv: sum(kv[1]) / len(kv[1]),
            )[0]
            recs.append({
                "area_of_law": strongest,
                "difficulty": min(5, suggested_difficulty + 1),
                "reason": f"You're strong in {strongest} — try a harder case.",
                "priority": "CHALLENGE",
            })

    return {
        "user_id": user_id,
        "suggested_difficulty": suggested_difficulty,
        "unpracticed_areas": unpracticed,
        "recommendations": recs,
    }
