"""Data transformation and aggregation utilities."""

from statistics import mean, median, stdev
from typing import Any


class DataProcessor:
    """Processes lists of numeric or record data."""

    def __init__(self, data: list[Any]):
        if not isinstance(data, list):
            raise TypeError("data must be a list")
        self._data = data

    # ------------------------------------------------------------------
    # Numeric operations
    # ------------------------------------------------------------------

    def filter_numeric(self) -> list[float]:
        """Return only numeric values from the dataset."""
        return [x for x in self._data if isinstance(x, (int, float)) and not isinstance(x, bool)]

    def normalize(self) -> list[float]:
        """Min-max normalize numeric values to [0, 1].

        Raises ValueError if all values are identical (zero range).
        """
        nums = self.filter_numeric()
        if not nums:
            return []
        lo, hi = min(nums), max(nums)
        if lo == hi:
            raise ValueError("Cannot normalize: all values are identical")
        return [(x - lo) / (hi - lo) for x in nums]

    def summarize(self) -> dict[str, float]:
        """Return descriptive statistics for numeric values.

        Returns:
            Dict with keys: count, min, max, mean, median, stdev
            stdev is 0.0 if there is only one data point.
        """
        nums = self.filter_numeric()
        if not nums:
            return {}
        return {
            "count": float(len(nums)),
            "min": float(min(nums)),
            "max": float(max(nums)),
            "mean": mean(nums),
            "median": median(nums),
            "stdev": stdev(nums) if len(nums) > 1 else 0.0,
        }

    # ------------------------------------------------------------------
    # Record (dict) operations
    # ------------------------------------------------------------------

    def filter_records(self, key: str, value: Any) -> list[dict]:
        """Return records (dicts) where record[key] == value."""
        return [
            item for item in self._data
            if isinstance(item, dict) and item.get(key) == value
        ]

    def pluck(self, key: str) -> list[Any]:
        """Extract a single field from each record in the dataset."""
        return [
            item[key] for item in self._data
            if isinstance(item, dict) and key in item
        ]

    def group_by(self, key: str) -> dict[Any, list[dict]]:
        """Group records by the value of a given key."""
        groups: dict[Any, list[dict]] = {}
        for item in self._data:
            if not isinstance(item, dict):
                continue
            group_val = item.get(key)
            groups.setdefault(group_val, []).append(item)
        return groups

    def sort_records(self, key: str, reverse: bool = False) -> list[dict]:
        """Sort records by a given key. Non-dict items are excluded."""
        records = [item for item in self._data if isinstance(item, dict) and key in item]
        return sorted(records, key=lambda r: r[key], reverse=reverse)

    def deduplicate(self) -> list[Any]:
        """Return data with duplicate values removed (preserving order)."""
        seen: set = set()
        result = []
        for item in self._data:
            # dicts are not hashable — use tuple of items as key
            try:
                key = item if not isinstance(item, dict) else tuple(sorted(item.items()))
                if key not in seen:
                    seen.add(key)
                    result.append(item)
            except TypeError:
                result.append(item)
        return result
