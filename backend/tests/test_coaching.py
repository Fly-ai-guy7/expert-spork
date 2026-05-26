from app.services.coaching_service import _weak_patterns


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
