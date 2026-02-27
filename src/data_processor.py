"""Data processing and transformation utilities."""

from statistics import mean, median, stdev
from typing import Any


def normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    min_val = min(values)
    max_val = max(values)
    if min_val == max_val:
        return [0.0] * len(values)
    return [(v - min_val) / (max_val - min_val) for v in values]


def chunk(lst: list, size: int) -> list[list]:
    if size <= 0:
        raise ValueError("Chunk size must be positive")
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def deduplicate(lst: list) -> list:
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def summarize(values: list[float]) -> dict[str, Any]:
    if not values:
        return {}
    result = {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "median": median(values),
    }
    if len(values) > 1:
        result["stdev"] = stdev(values)
    return result


def group_by(lst: list[dict], key: str) -> dict[Any, list[dict]]:
    result: dict[Any, list[dict]] = {}
    for item in lst:
        k = item.get(key)
        result.setdefault(k, []).append(item)
    return result


def filter_by(lst: list[dict], key: str, value: Any) -> list[dict]:
    return [item for item in lst if item.get(key) == value]
