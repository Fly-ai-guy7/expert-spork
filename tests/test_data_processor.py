"""Tests for DataProcessor — full coverage."""

import pytest
from expert_spork.data_processor import DataProcessor


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_invalid_construction():
    with pytest.raises(TypeError):
        DataProcessor("not a list")


# ---------------------------------------------------------------------------
# filter_numeric
# ---------------------------------------------------------------------------

def test_filter_numeric_basic():
    dp = DataProcessor([1, 2, "three", True, 4.5])
    assert dp.filter_numeric() == [1, 2, 4.5]


def test_filter_numeric_all_non_numeric():
    dp = DataProcessor(["a", "b", True, False])
    assert dp.filter_numeric() == []


def test_filter_numeric_empty():
    dp = DataProcessor([])
    assert dp.filter_numeric() == []


# ---------------------------------------------------------------------------
# normalize
# ---------------------------------------------------------------------------

def test_normalize_basic():
    dp = DataProcessor([0, 5, 10])
    result = dp.normalize()
    assert result == [0.0, 0.5, 1.0]


def test_normalize_returns_empty_for_no_numerics():
    dp = DataProcessor(["a", "b"])
    assert dp.normalize() == []


def test_normalize_zero_range_raises():
    dp = DataProcessor([7, 7, 7])
    with pytest.raises(ValueError, match="identical"):
        dp.normalize()


# ---------------------------------------------------------------------------
# summarize
# ---------------------------------------------------------------------------

def test_summarize_basic():
    dp = DataProcessor([2, 4, 6, 8, 10])
    result = dp.summarize()
    assert result["count"] == 5.0
    assert result["min"] == 2.0
    assert result["max"] == 10.0
    assert result["mean"] == 6.0
    assert result["median"] == 6.0
    assert result["stdev"] > 0


def test_summarize_single_element():
    dp = DataProcessor([42])
    result = dp.summarize()
    assert result["count"] == 1.0
    assert result["min"] == 42.0
    assert result["max"] == 42.0
    assert result["stdev"] == 0.0


def test_summarize_empty():
    dp = DataProcessor([])
    assert dp.summarize() == {}


# ---------------------------------------------------------------------------
# filter_records
# ---------------------------------------------------------------------------

def test_filter_records_match():
    data = [{"status": "active"}, {"status": "inactive"}, {"status": "active"}]
    dp = DataProcessor(data)
    result = dp.filter_records("status", "active")
    assert len(result) == 2
    assert all(r["status"] == "active" for r in result)


def test_filter_records_no_match():
    dp = DataProcessor([{"status": "active"}])
    assert dp.filter_records("status", "deleted") == []


def test_filter_records_skips_non_dicts():
    dp = DataProcessor([42, "string", {"status": "active"}])
    result = dp.filter_records("status", "active")
    assert result == [{"status": "active"}]


# ---------------------------------------------------------------------------
# pluck
# ---------------------------------------------------------------------------

def test_pluck_basic():
    dp = DataProcessor([{"name": "Alice"}, {"name": "Bob"}, {"age": 30}])
    assert dp.pluck("name") == ["Alice", "Bob"]


def test_pluck_missing_key_skipped():
    dp = DataProcessor([{"x": 1}, {"y": 2}])
    assert dp.pluck("x") == [1]


def test_pluck_empty():
    dp = DataProcessor([])
    assert dp.pluck("key") == []


# ---------------------------------------------------------------------------
# group_by
# ---------------------------------------------------------------------------

def test_group_by_basic():
    data = [
        {"dept": "eng", "name": "Alice"},
        {"dept": "hr", "name": "Bob"},
        {"dept": "eng", "name": "Charlie"},
    ]
    dp = DataProcessor(data)
    groups = dp.group_by("dept")
    assert len(groups["eng"]) == 2
    assert len(groups["hr"]) == 1


def test_group_by_skips_non_dicts():
    dp = DataProcessor([1, 2, {"dept": "eng"}])
    groups = dp.group_by("dept")
    assert "eng" in groups
    assert 1 not in groups


def test_group_by_missing_key_grouped_under_none():
    dp = DataProcessor([{"dept": "eng"}, {"name": "Bob"}])
    groups = dp.group_by("dept")
    assert None in groups
    assert "eng" in groups


# ---------------------------------------------------------------------------
# sort_records
# ---------------------------------------------------------------------------

def test_sort_records_ascending():
    data = [{"score": 3}, {"score": 1}, {"score": 2}]
    dp = DataProcessor(data)
    result = dp.sort_records("score")
    assert [r["score"] for r in result] == [1, 2, 3]


def test_sort_records_descending():
    data = [{"score": 3}, {"score": 1}, {"score": 2}]
    dp = DataProcessor(data)
    result = dp.sort_records("score", reverse=True)
    assert [r["score"] for r in result] == [3, 2, 1]


def test_sort_records_excludes_missing_key():
    data = [{"score": 2}, {"name": "no score"}, {"score": 1}]
    dp = DataProcessor(data)
    result = dp.sort_records("score")
    assert len(result) == 2
    assert result[0]["score"] == 1


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

def test_deduplicate_primitives():
    dp = DataProcessor([1, 2, 2, 3, 1])
    assert dp.deduplicate() == [1, 2, 3]


def test_deduplicate_dicts():
    data = [{"id": 1}, {"id": 2}, {"id": 1}]
    dp = DataProcessor(data)
    result = dp.deduplicate()
    assert len(result) == 2


def test_deduplicate_preserves_order():
    dp = DataProcessor([3, 1, 2, 1, 3])
    assert dp.deduplicate() == [3, 1, 2]


def test_deduplicate_empty():
    dp = DataProcessor([])
    assert dp.deduplicate() == []


def test_deduplicate_unhashable_items_included():
    # Lists are unhashable — the except TypeError path keeps them as-is
    dp = DataProcessor([[1, 2], [3, 4], [1, 2]])
    result = dp.deduplicate()
    assert [1, 2] in result
    assert [3, 4] in result
