"""Tests for DataProcessor — very sparse coverage."""

import pytest
from expert_spork.data_processor import DataProcessor


def test_filter_numeric_basic():
    dp = DataProcessor([1, 2, "three", True, 4.5])
    assert dp.filter_numeric() == [1, 2, 4.5]


def test_invalid_construction():
    with pytest.raises(TypeError):
        DataProcessor("not a list")


# Missing: test_normalize (including zero-range ValueError)
# Missing: test_summarize (including empty and single-element cases)
# Missing: test_filter_records
# Missing: test_pluck
# Missing: test_group_by
# Missing: test_sort_records (including reverse=True)
# Missing: test_deduplicate (including dict deduplication)
