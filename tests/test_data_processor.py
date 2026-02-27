"""Tests for data_processor module."""

import pytest
from src.data_processor import normalize, chunk, flatten, deduplicate, summarize, group_by, filter_by


class TestNormalize:
    def test_basic_range(self):
        result = normalize([0.0, 5.0, 10.0])
        assert result == pytest.approx([0.0, 0.5, 1.0])

    def test_empty_list(self):
        assert normalize([]) == []

    def test_all_same_value_returns_zeros(self):
        # min == max guard — avoids division by zero
        assert normalize([7.0, 7.0, 7.0]) == [0.0, 0.0, 0.0]

    def test_single_element(self):
        assert normalize([42.0]) == [0.0]

    def test_negative_values(self):
        result = normalize([-10.0, 0.0, 10.0])
        assert result == pytest.approx([0.0, 0.5, 1.0])

    def test_output_bounds(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = normalize(values)
        assert min(result) == pytest.approx(0.0)
        assert max(result) == pytest.approx(1.0)


class TestChunk:
    def test_even_split(self):
        assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]

    def test_remainder_chunk(self):
        assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]

    def test_size_larger_than_list(self):
        assert chunk([1, 2], 10) == [[1, 2]]

    def test_size_one(self):
        assert chunk([1, 2, 3], 1) == [[1], [2], [3]]

    def test_empty_list(self):
        assert chunk([], 3) == []

    def test_invalid_size_raises(self):
        with pytest.raises(ValueError, match="Chunk size must be positive"):
            chunk([1, 2, 3], 0)

    def test_negative_size_raises(self):
        with pytest.raises(ValueError):
            chunk([1, 2, 3], -1)


class TestFlatten:
    def test_already_flat(self):
        assert flatten([1, 2, 3]) == [1, 2, 3]

    def test_one_level_nested(self):
        assert flatten([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    def test_deeply_nested(self):
        assert flatten([1, [2, [3, [4]]]]) == [1, 2, 3, 4]

    def test_empty_list(self):
        assert flatten([]) == []

    def test_nested_empty_lists(self):
        assert flatten([[], [1], []]) == [1]

    def test_mixed_types(self):
        assert flatten([1, "a", [2, "b"]]) == [1, "a", 2, "b"]

    def test_no_mutation_of_input(self):
        original = [[1, 2], [3]]
        flatten(original)
        assert original == [[1, 2], [3]]


class TestDeduplicate:
    def test_removes_duplicates(self):
        assert deduplicate([1, 2, 2, 3, 1]) == [1, 2, 3]

    def test_preserves_order(self):
        assert deduplicate([3, 1, 2, 1, 3]) == [3, 1, 2]

    def test_no_duplicates_unchanged(self):
        assert deduplicate([1, 2, 3]) == [1, 2, 3]

    def test_empty_list(self):
        assert deduplicate([]) == []

    def test_all_duplicates(self):
        assert deduplicate([5, 5, 5]) == [5]

    def test_strings(self):
        assert deduplicate(["a", "b", "a"]) == ["a", "b"]


class TestSummarize:
    def test_empty_list_returns_empty_dict(self):
        assert summarize([]) == {}

    def test_single_element_no_stdev(self):
        result = summarize([42.0])
        assert result["count"] == 1
        assert result["min"] == 42.0
        assert result["max"] == 42.0
        assert result["mean"] == pytest.approx(42.0)
        assert result["median"] == pytest.approx(42.0)
        assert "stdev" not in result  # stdev branch not triggered for n==1

    def test_multiple_elements_has_stdev(self):
        result = summarize([1.0, 2.0, 3.0, 4.0, 5.0])
        assert result["count"] == 5
        assert result["min"] == 1.0
        assert result["max"] == 5.0
        assert result["mean"] == pytest.approx(3.0)
        assert result["median"] == pytest.approx(3.0)
        assert "stdev" in result
        assert result["stdev"] == pytest.approx(1.5811, rel=1e-3)

    def test_all_same_values(self):
        result = summarize([7.0, 7.0, 7.0])
        assert result["min"] == result["max"] == result["mean"] == 7.0
        assert result["stdev"] == pytest.approx(0.0)


class TestGroupBy:
    def test_basic_grouping(self):
        data = [
            {"type": "a", "val": 1},
            {"type": "b", "val": 2},
            {"type": "a", "val": 3},
        ]
        result = group_by(data, "type")
        assert len(result["a"]) == 2
        assert len(result["b"]) == 1

    def test_empty_list(self):
        assert group_by([], "key") == {}

    def test_key_absent_groups_under_none(self):
        data = [{"x": 1}, {"y": 2}]
        result = group_by(data, "x")
        assert 1 in result
        assert None in result

    def test_single_group(self):
        data = [{"k": "same"}, {"k": "same"}]
        result = group_by(data, "k")
        assert list(result.keys()) == ["same"]
        assert len(result["same"]) == 2


class TestFilterBy:
    def test_basic_filter(self):
        data = [{"role": "admin"}, {"role": "user"}, {"role": "admin"}]
        result = filter_by(data, "role", "admin")
        assert len(result) == 2
        assert all(r["role"] == "admin" for r in result)

    def test_no_matches_returns_empty(self):
        data = [{"role": "user"}]
        assert filter_by(data, "role", "admin") == []

    def test_empty_list(self):
        assert filter_by([], "role", "admin") == []

    def test_key_absent_in_items(self):
        data = [{"other": "value"}]
        assert filter_by(data, "role", "admin") == []

    def test_filter_by_none_value(self):
        data = [{"status": None}, {"status": "active"}]
        result = filter_by(data, "status", None)
        assert len(result) == 1
