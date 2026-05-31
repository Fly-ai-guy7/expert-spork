from datetime import datetime, timedelta, timezone

from app.services.dashboard_service import (
    build_dashboard,
    build_risk_heatmap,
    classify_overdue,
)
from tests.conftest import pg_required


def _now():
    return datetime(2026, 5, 31, 12, 0, tzinfo=timezone.utc)


def test_classify_overdue_filters_and_sorts_by_age():
    now = _now()
    items = [
        {"checkpoint_id": "a", "created_at": now - timedelta(hours=2)},   # fresh
        {"checkpoint_id": "b", "created_at": now - timedelta(hours=30)},  # overdue
        {"checkpoint_id": "c", "created_at": now - timedelta(hours=72)},  # most overdue
    ]
    overdue = classify_overdue(items, now, threshold_hours=24)
    assert [it["checkpoint_id"] for it in overdue] == ["c", "b"]
    assert overdue[0]["age_hours"] == 72.0
    assert all("age_hours" in it for it in overdue)


def test_classify_overdue_threshold_is_inclusive():
    now = _now()
    items = [{"checkpoint_id": "x", "created_at": now - timedelta(hours=24)}]
    assert len(classify_overdue(items, now, threshold_hours=24)) == 1


def test_build_risk_heatmap_averages_per_cell():
    rows = [
        {"area_of_law": "IP", "difficulty": 2, "risk_score": 60},
        {"area_of_law": "IP", "difficulty": 2, "risk_score": 80},
        {"area_of_law": "IP", "difficulty": 4, "risk_score": 30},
        {"area_of_law": "LABOUR", "difficulty": 2, "risk_score": 50},
    ]
    hm = build_risk_heatmap(rows)
    assert hm["areas"] == ["IP", "LABOUR"]
    cell = next(c for c in hm["cells"] if c["area_of_law"] == "IP" and c["difficulty"] == 2)
    assert cell["avg_risk"] == 70.0
    assert cell["count"] == 2
    assert hm["max_risk"] == 70.0


def test_build_risk_heatmap_handles_missing_area():
    hm = build_risk_heatmap([{"area_of_law": None, "difficulty": 1, "risk_score": 10}])
    assert hm["areas"] == ["—"]
    assert hm["cells"][0]["avg_risk"] == 10.0


def test_build_risk_heatmap_empty():
    hm = build_risk_heatmap([])
    assert hm["areas"] == []
    assert hm["cells"] == []
    assert hm["max_risk"] == 0.0


@pg_required
def test_build_dashboard_end_to_end(db_session):
    """Seed a realistic mix and assert the assembled dashboard payload."""
    from app.models import (
        Case,
        CaseStatus,
        HilCheckpoint,
        HilStage,
        HilStatus,
        Outcome,
        Ruling,
        TraineeRole,
        TrainingSession,
    )

    now = datetime.now(timezone.utc)

    # Two scored IP cases (risk 60 + 80 → avg 70) and one LABOUR case (risk 30).
    ip_a = Case(status=CaseStatus.COMPLETE, area_of_law="IP", difficulty=2)
    ip_b = Case(status=CaseStatus.COMPLETE, area_of_law="IP", difficulty=2)
    labour = Case(status=CaseStatus.RUNNING, area_of_law="LABOUR", difficulty=4)
    # Open cases driving the counts.
    paused = Case(status=CaseStatus.PAUSED_HIL, area_of_law="IP", difficulty=3)
    draft = Case(status=CaseStatus.DRAFT, area_of_law="IP", difficulty=1)
    db_session.add_all([ip_a, ip_b, labour, paused, draft])
    db_session.flush()

    db_session.add_all(
        [
            Outcome(case_id=ip_a.id, risk_score=60),
            Outcome(case_id=ip_b.id, risk_score=80),
            Outcome(case_id=labour.id, risk_score=30),
        ]
    )

    # Overdue trainee turn (30h old) + a fresh, non-overdue checkpoint.
    db_session.add_all(
        [
            HilCheckpoint(
                case_id=paused.id,
                stage=HilStage.TRAINEE_TURN,
                status=HilStatus.PENDING,
                created_at=now - timedelta(hours=30),
            ),
            HilCheckpoint(
                case_id=draft.id,
                stage=HilStage.POST_EVIDENCE,
                status=HilStatus.PENDING,
                created_at=now - timedelta(hours=1),
            ),
        ]
    )

    # Recent-activity sources.
    db_session.add(Ruling(case_id=ip_a.id, plaintiff_success_prob=62))
    db_session.add(
        TrainingSession(
            user_id="trainee",
            case_id=ip_a.id,
            trainee_role=TraineeRole.DEFENSE,
            difficulty=2,
            total_score=71,
            completed_at=now,
        )
    )
    db_session.flush()

    dash = build_dashboard(db_session, overdue_hours=24)

    # open issue counts
    by_status = dash["open_issues"]["by_status"]
    assert by_status["COMPLETE"] == 2
    assert by_status["RUNNING"] == 1
    assert by_status["PAUSED_HIL"] == 1
    assert by_status["DRAFT"] == 1
    assert dash["open_issues"]["open_total"] == 3  # RUNNING + PAUSED_HIL + DRAFT
    assert dash["open_issues"]["pending_checkpoints"] == 2
    assert dash["open_issues"]["awaiting_trainee"] == 1

    # overdue items
    assert dash["overdue"]["count"] == 1
    overdue_item = dash["overdue"]["items"][0]
    assert overdue_item["stage"] == "TRAINEE_TURN"
    assert overdue_item["age_hours"] >= 24

    # risk heatmap
    hm = dash["risk_heatmap"]
    assert hm["areas"] == ["IP", "LABOUR"]
    ip2 = next(c for c in hm["cells"] if c["area_of_law"] == "IP" and c["difficulty"] == 2)
    assert ip2["avg_risk"] == 70.0
    assert ip2["count"] == 2
    assert hm["max_risk"] == 70.0

    # recent activity
    types = {e["type"] for e in dash["recent_activity"]}
    assert {"case_created", "ruling_issued", "training_completed"} <= types
    assert dash["disclaimer"]["en"].startswith("AI Simulation Only")
