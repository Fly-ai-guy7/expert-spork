import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Argument, Ruling, TrainingSession
from app.models.argument import AgentRole


def generate_coaching_report(db: Session, training_session_id: uuid.UUID) -> dict:
    ts = db.execute(
        select(TrainingSession).where(TrainingSession.id == training_session_id)
    ).scalar_one()

    args = db.execute(
        select(Argument)
        .options(selectinload(Argument.score))
        .where(Argument.case_id == ts.case_id)
        .order_by(Argument.round_no, Argument.created_at)
    ).scalars().all()

    trainee_role = AgentRole(ts.trainee_role.value)
    trainee_args = [a for a in args if a.agent == trainee_role]
    opponent_role = AgentRole.DEFENSE if trainee_role == AgentRole.PROSECUTION else AgentRole.PROSECUTION
    opponent_args = [a for a in args if a.agent == opponent_role]

    per_round: list[dict] = []
    overall_scores: list[float] = []
    trainee_citations: set[str] = set()
    opponent_citations: set[str] = set()

    for a in trainee_args:
        score = a.score
        trainee_citations.update(a.citations or [])
        per_round.append({
            "round_no": a.round_no,
            "factual": score.factual if score else 0,
            "provable": score.provable if score else 0,
            "unbiased": score.unbiased if score else 0,
            "legal_law_based": score.legal_law_based if score else 0,
            "overall": score.overall if score else 0,
            "rationale_en": score.rationale_en if score else None,
            "rationale_ar": score.rationale_ar if score else None,
        })
        if score:
            overall_scores.append(score.overall)

    for a in opponent_args:
        opponent_citations.update(a.citations or [])

    missed_citations = list(opponent_citations - trainee_citations)

    ruling = db.execute(select(Ruling).where(Ruling.case_id == ts.case_id)).scalar_one_or_none()
    critical_gaps = (ruling.critical_evidence_gaps or []) if ruling else []

    total = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
    if total >= 85:
        grade = "A"
    elif total >= 70:
        grade = "B"
    elif total >= 55:
        grade = "C"
    elif total >= 40:
        grade = "D"
    else:
        grade = "F"

    report = {
        "grade": grade,
        "total_score": total,
        "per_round": per_round,
        "missed_citations": missed_citations[:5],
        "evidence_gaps_to_address": critical_gaps[:5],
        "weak_patterns": _weak_patterns(per_round),
    }

    ts.coaching_report = report
    ts.total_score = total
    ts.completed_at = datetime.now(UTC)
    db.commit()
    return report


def _weak_patterns(per_round: list[dict]) -> list[str]:
    if not per_round:
        return []
    dims = ["factual", "provable", "unbiased", "legal_law_based"]
    averages = {d: sum(r[d] for r in per_round) / len(per_round) for d in dims}
    weakest = sorted(averages.items(), key=lambda kv: kv[1])[:2]
    labels = {
        "factual": "Weak factual grounding — re-check claims against the record",
        "provable": "Arguments not supported by available evidence — anchor each claim",
        "unbiased": "Unsupported assertions / rhetorical leaps — argue from sources",
        "legal_law_based": "Insufficient statute citations — ground in Egyptian code",
    }
    return [labels[k] for k, _ in weakest]
