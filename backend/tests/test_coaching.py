from app.services.coaching_service import _council_alignment, _weak_patterns


def test_weak_patterns_picks_two_lowest():
    per_round = [
        {"factual": 90, "provable": 40, "unbiased": 80, "legal_law_based": 30},
        {"factual": 85, "provable": 50, "unbiased": 75, "legal_law_based": 35},
    ]
    patterns = _weak_patterns(per_round)
    assert len(patterns) == 2
    joined = " ".join(patterns).lower()
    assert "statute" in joined or "evidence" in joined or "supported" in joined


def test_weak_patterns_empty():
    assert _weak_patterns([]) == []


def _verdicts(*pairs):
    return [{"member_llm": m, "verdict": v} for m, v in pairs]


def test_council_alignment_won_for_prosecution_trainee():
    out = _council_alignment(
        _verdicts(("a", "FOR_PLAINTIFF"), ("b", "FOR_PLAINTIFF"), ("c", "FOR_DEFENDANT")),
        "PROSECUTION",
    )
    assert out["council_alignment"] == "WON"
    assert out["council_for_trainee"] == 2
    assert out["council_against_trainee"] == 1
    assert out["council_supporters"] == ["a", "b"]
    assert out["council_dissenters"] == ["c"]


def test_council_alignment_lost_for_defense_trainee():
    out = _council_alignment(
        _verdicts(("a", "FOR_PLAINTIFF"), ("b", "FOR_PLAINTIFF"), ("c", "FOR_DEFENDANT")),
        "DEFENSE",
    )
    assert out["council_alignment"] == "LOST"
    assert out["council_for_trainee"] == 1
    assert out["council_supporters"] == ["c"]
    assert out["council_dissenters"] == ["a", "b"]


def test_council_alignment_tie_is_loss_for_trainee():
    out = _council_alignment(
        _verdicts(("a", "FOR_PLAINTIFF"), ("b", "FOR_DEFENDANT")),
        "PROSECUTION",
    )
    assert out["council_alignment"] == "LOST"


def test_council_alignment_empty():
    assert _council_alignment([], "DEFENSE") == {}
