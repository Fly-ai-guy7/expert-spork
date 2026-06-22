from datetime import datetime, timezone

from app.services.instructor_service import compute_overview


def _session(
    id: str,
    user_id: str,
    *,
    grade: str | None = "B",
    total: float | None = 70.0,
    completed: bool = True,
    role: str = "DEFENSE",
    council: str | None = "WON",
    counsel_calls: int = 0,
    missed: list[str] | None = None,
    weak: list[str] | None = None,
    minutes_ago: int = 0,
) -> dict:
    completed_at = (
        datetime(2026, 6, 1, 12, minutes_ago, tzinfo=timezone.utc) if completed else None
    )
    report = (
        {
            "grade": grade,
            "missed_citations": missed or [],
            "weak_patterns": weak or [],
            "council_alignment": council,
            "counsel_calls_count": counsel_calls,
        }
        if completed
        else {}
    )
    return {
        "id": id,
        "user_id": user_id,
        "trainee_role": role,
        "total_score": total,
        "completed_at": completed_at,
        "coaching_report": report,
    }


def test_empty_sessions_returns_zero_metrics():
    out = compute_overview([])
    assert out["total_sessions"] == 0
    assert out["completed_sessions"] == 0
    assert out["avg_score"] == 0.0
    assert out["per_user"] == []
    assert out["council_lost_rate"] is None
    assert out["needs_attention"] == []


def test_aggregate_counts_grades_and_average():
    out = compute_overview([
        _session("a", "u1", grade="A", total=90),
        _session("b", "u2", grade="B", total=70),
        _session("c", "u2", grade="B", total=80),
        _session("d", "u3", grade="C", total=60, completed=False),  # ignored
    ])
    assert out["total_sessions"] == 4
    assert out["completed_sessions"] == 3
    assert out["avg_score"] == 80.0
    assert out["grade_distribution"] == {"A": 1, "B": 2}


def test_per_user_rollup_sorts_by_session_count():
    out = compute_overview([
        _session("a", "alice", grade="A", total=90),
        _session("b", "bob", grade="B", total=70),
        _session("c", "bob", grade="C", total=60),
    ])
    assert [u["user_id"] for u in out["per_user"]] == ["bob", "alice"]
    bob = out["per_user"][0]
    assert bob["sessions"] == 2
    assert bob["avg_score"] == 65.0
    assert bob["latest_grade"] in ("B", "C")


def test_top_missed_citations_and_weak_patterns():
    out = compute_overview([
        _session("a", "u1", missed=["82/2002:113", "131/1948:163"], weak=["weak claims"]),
        _session("b", "u1", missed=["82/2002:113"], weak=["weak claims", "thin cites"]),
    ])
    cits = out["top_missed_citations"]
    assert cits[0] == {"citation": "82/2002:113", "count": 2}
    pats = [p["pattern"] for p in out["top_weak_patterns"]]
    assert pats[0] == "weak claims"


def test_needs_attention_flags_low_grade_lost_council_and_heavy_counsel_use():
    out = compute_overview([
        _session("ok", "u1", grade="A", total=92, council="WON", counsel_calls=1),
        _session("lo", "u2", grade="F", total=20, council="WON"),
        _session("lp", "u3", grade="B", total=72, council="LOST"),
        _session("hc", "u4", grade="B", total=68, council="WON", counsel_calls=7),
    ])
    flagged = {r["session_id"] for r in out["needs_attention"]}
    assert flagged == {"lo", "lp", "hc"}
    # most recent first by completed_at — all share the same date here, so just len
    assert len(out["needs_attention"]) == 3


def test_council_lost_rate():
    out = compute_overview([
        _session("a", "u1", council="WON"),
        _session("b", "u2", council="LOST"),
        _session("c", "u3", council="LOST"),
        _session("d", "u4", council=None),  # no alignment recorded → excluded
    ])
    assert out["council_lost_rate"] == 2 / 3
