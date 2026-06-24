"""OpenAPI hygiene.

Locks in: the spec generates, has the expected versioned + legacy prefixes,
no duplicate (method, path) under v1, and every v1 path is classified by
the contract matrix (PUBLIC or PROTECTED).
"""
from __future__ import annotations

import re

from app.main import create_app
from tests.test_api_contract import DUMMY_UUID, PROTECTED, PUBLIC


def _normalise(path: str) -> str:
    return re.sub(r"\{[^}]+\}", DUMMY_UUID, path)


def test_openapi_spec_builds():
    schema = create_app().openapi()
    assert schema["openapi"].startswith("3.")
    assert schema["info"]["title"] == "EQUALISE Egypt API"


def test_v1_and_legacy_prefixes_both_present():
    schema = create_app().openapi()
    paths = list(schema["paths"])
    v1 = [p for p in paths if p.startswith("/api/v1/")]
    legacy = [p for p in paths if p.startswith("/api/") and not p.startswith("/api/v1/")]
    assert len(v1) > 0 and len(legacy) > 0
    # The two prefixes mirror each other 1:1 — same number of paths.
    assert len(v1) == len(legacy)


def test_no_duplicate_method_path_under_v1():
    schema = create_app().openapi()
    seen: set[tuple[str, str]] = set()
    dups: list[tuple[str, str]] = []
    for path, ops in schema["paths"].items():
        if not path.startswith("/api/v1/"):
            continue
        for method in ops:
            if method in {"parameters", "summary", "description"}:
                continue
            key = (method.upper(), path)
            if key in seen:
                dups.append(key)
            seen.add(key)
    assert not dups, f"duplicate operations: {dups}"


def test_every_v1_path_is_classified_by_contract_matrix():
    """If a v1 endpoint exists in the spec it MUST be classified PUBLIC or
    listed in PROTECTED. Catches a developer adding a route without also
    extending the security test surface."""
    schema = create_app().openapi()
    protected = {(m, p) for (m, p, _, _) in PROTECTED}
    unclassified: list[tuple[str, str]] = []
    for path, ops in schema["paths"].items():
        if not path.startswith("/api/v1/"):
            continue
        normalised = _normalise(path)
        for method in ops:
            if method in {"parameters", "summary", "description"}:
                continue
            key = (method.upper(), normalised)
            if key in PUBLIC or key in protected:
                continue
            unclassified.append(key)
    assert not unclassified, (
        "OpenAPI exposes routes the contract matrix doesn't classify: "
        + ", ".join(f"{m} {p}" for m, p in unclassified)
    )
