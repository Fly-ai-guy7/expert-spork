from datetime import datetime, timedelta, timezone

from app.services.dashboard_service import build_risk_heatmap, classify_overdue


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
