"""Dashboard aggregation service (v3 case-intelligence dashboard).

Surfaces four panels for trainers/research leads:

- **open issue counts** — cases by status, plus pending HIL checkpoints
- **overdue items** — PENDING checkpoints (esp. TRAINEE_TURN) waiting past a threshold
- **risk heatmap** — average `Outcome.risk_score` across area-of-law × difficulty
- **recent activity** — latest cases, rulings, completed sessions, checkpoint responses

The query layer is thin; the bucketing logic lives in pure helpers
(`classify_overdue`, `build_risk_heatmap`) so it is unit-testable without a DB.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.disclaimer import disclaimer_block
from app.models import (
    Case,
    CaseStatus,
    HilCheckpoint,
    HilStage,
    HilStatus,
    Outcome,
    Ruling,
    TrainingSession,
)

# A checkpoint awaiting a human for longer than this is "overdue".
OVERDUE_THRESHOLD_HOURS = 24
DIFFICULTIES = (1, 2, 3, 4, 5)

# Statuses that still need attention vs. terminal ones.
OPEN_STATUSES = (CaseStatus.DRAFT, CaseStatus.RUNNING, CaseStatus.PAUSED_HIL)


def _hours_since(ts: datetime, now: datetime) -> float:
    return (now - ts).total_seconds() / 3600.0


def classify_overdue(
    items: list[dict],
    now: datetime,
    threshold_hours: float = OVERDUE_THRESHOLD_HOURS,
) -> list[dict]:
    """Return the items whose ``created_at`` is older than ``threshold_hours``.

    Each returned item is annotated with ``age_hours`` and sorted oldest-first.
    """
    out: list[dict] = []
    for it in items:
        age = _hours_since(it["created_at"], now)
        if age >= threshold_hours:
            out.append({**it, "age_hours": round(age, 1)})
    out.sort(key=lambda x: x["age_hours"], reverse=True)
    return out


def build_risk_heatmap(rows: list[dict], difficulties=DIFFICULTIES) -> dict:
    """Aggregate (area_of_law, difficulty, risk_score) rows into a heatmap.

    Returns the distinct areas (rows), difficulty columns, and one cell per
    populated (area, difficulty) pair carrying the mean risk and sample count.
    """
    agg: dict[tuple[str, int | None], dict] = defaultdict(lambda: {"sum": 0.0, "count": 0})
    areas: list[str] = []
    seen: set[str] = set()
    for r in rows:
        area = r["area_of_law"] or "—"
        diff = r["difficulty"]
        if area not in seen:
            seen.add(area)
            areas.append(area)
        bucket = agg[(area, diff)]
        bucket["sum"] += float(r["risk_score"])
        bucket["count"] += 1

    cells: list[dict] = []
    max_risk = 0.0
    for (area, diff), v in agg.items():
        avg = v["sum"] / v["count"] if v["count"] else 0.0
        max_risk = max(max_risk, avg)
        cells.append(
            {"area_of_law": area, "difficulty": diff, "avg_risk": round(avg, 1), "count": v["count"]}
        )

    areas.sort()
    cells.sort(key=lambda c: (c["area_of_law"], c["difficulty"] if c["difficulty"] is not None else 0))
    return {
        "areas": areas,
        "difficulties": list(difficulties),
        "cells": cells,
        "max_risk": round(max_risk, 1),
    }


def _recent_activity(db: Session, limit: int) -> list[dict]:
    """Merge the latest events across cases, rulings, sessions, checkpoints."""
    events: list[dict] = []

    cases = db.execute(
        select(Case).order_by(Case.created_at.desc()).limit(limit)
    ).scalars().all()
    for c in cases:
        events.append(
            {
                "type": "case_created",
                "at": c.created_at,
                "case_id": str(c.id),
                "title_en": c.title_en,
                "title_ar": c.title_ar,
                "detail": c.status.value,
            }
        )

    rulings = db.execute(
        select(Ruling, Case.title_en, Case.title_ar)
        .join(Case, Case.id == Ruling.case_id)
        .order_by(Ruling.created_at.desc())
        .limit(limit)
    ).all()
    for r, ten, tar in rulings:
        events.append(
            {
                "type": "ruling_issued",
                "at": r.created_at,
                "case_id": str(r.case_id),
                "title_en": ten,
                "title_ar": tar,
                "detail": f"{round(r.plaintiff_success_prob)}% plaintiff",
            }
        )

    sessions = db.execute(
        select(TrainingSession, Case.title_en, Case.title_ar)
        .join(Case, Case.id == TrainingSession.case_id)
        .where(TrainingSession.completed_at.is_not(None))
        .order_by(TrainingSession.completed_at.desc())
        .limit(limit)
    ).all()
    for s, ten, tar in sessions:
        score = f"{round(s.total_score)}" if s.total_score is not None else "—"
        events.append(
            {
                "type": "training_completed",
                "at": s.completed_at,
                "case_id": str(s.case_id),
                "title_en": ten,
                "title_ar": tar,
                "detail": f"{s.trainee_role.value} · {score}",
            }
        )

    responded = db.execute(
        select(HilCheckpoint, Case.title_en, Case.title_ar)
        .join(Case, Case.id == HilCheckpoint.case_id)
        .where(HilCheckpoint.responded_at.is_not(None))
        .order_by(HilCheckpoint.responded_at.desc())
        .limit(limit)
    ).all()
    for cp, ten, tar in responded:
        events.append(
            {
                "type": "checkpoint_responded",
                "at": cp.responded_at,
                "case_id": str(cp.case_id),
                "title_en": ten,
                "title_ar": tar,
                "detail": f"{cp.stage.value} · {cp.status.value}",
            }
        )

    events.sort(key=lambda e: e["at"], reverse=True)
    return events[:limit]


def build_dashboard(
    db: Session,
    overdue_hours: float = OVERDUE_THRESHOLD_HOURS,
    recent_limit: int = 12,
) -> dict:
    """Assemble the full dashboard payload."""
    now = datetime.now(timezone.utc)

    # --- open issue counts ---
    status_rows = db.execute(
        select(Case.status, func.count()).group_by(Case.status)
    ).all()
    by_status = {s.value: 0 for s in CaseStatus}
    for status, count in status_rows:
        by_status[status.value] = count
    open_total = sum(by_status[s.value] for s in OPEN_STATUSES)

    pending = db.execute(
        select(HilCheckpoint, Case.title_en, Case.title_ar)
        .join(Case, Case.id == HilCheckpoint.case_id)
        .where(HilCheckpoint.status == HilStatus.PENDING)
    ).all()
    pending_items = [
        {
            "checkpoint_id": str(cp.id),
            "case_id": str(cp.case_id),
            "title_en": ten,
            "title_ar": tar,
            "stage": cp.stage.value,
            "created_at": cp.created_at,
        }
        for cp, ten, tar in pending
    ]
    awaiting_trainee = sum(1 for cp, _, _ in pending if cp.stage == HilStage.TRAINEE_TURN)

    # --- overdue items ---
    overdue = classify_overdue(pending_items, now, overdue_hours)

    # --- risk heatmap ---
    risk_rows = db.execute(
        select(Case.area_of_law, Case.difficulty, Outcome.risk_score)
        .join(Outcome, Outcome.case_id == Case.id)
    ).all()
    heatmap = build_risk_heatmap(
        [{"area_of_law": a, "difficulty": d, "risk_score": rs} for a, d, rs in risk_rows]
    )

    return {
        "generated_at": now,
        "open_issues": {
            "by_status": by_status,
            "open_total": open_total,
            "pending_checkpoints": len(pending_items),
            "awaiting_trainee": awaiting_trainee,
        },
        "overdue": {
            "threshold_hours": overdue_hours,
            "count": len(overdue),
            "items": overdue,
        },
        "risk_heatmap": heatmap,
        "recent_activity": _recent_activity(db, recent_limit),
        "disclaimer": disclaimer_block(),
    }
