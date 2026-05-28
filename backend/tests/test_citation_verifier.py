"""Citation hallucination guardrail tests.

`verify_citations` is the single source of truth for whether an LLM's cited
short_code:article actually exists in our loaded statute corpus. These tests
exercise it directly (unit) and through the orchestrator (integration with a
patched mock LLM that emits a bogus citation).
"""
from __future__ import annotations

import asyncio
import json
import uuid

import pytest

from app.models import Argument, Case
from app.models.argument import AgentRole
from app.services import orchestrator
from app.services.corpus_service import verify_citations
from tests.scenarios import SCENARIOS
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401


def test_verify_real_citation_resolves(sqlite_db):
    valid, unverified = verify_citations(sqlite_db, ["82/2002:113"])
    assert len(valid) == 1
    assert unverified == []


def test_verify_fake_article_number_flagged(sqlite_db):
    valid, unverified = verify_citations(sqlite_db, ["82/2002:99999"])
    assert valid == []
    assert unverified == ["82/2002:99999"]


def test_verify_fake_law_number_flagged(sqlite_db):
    valid, unverified = verify_citations(sqlite_db, ["999/1899:1"])
    assert valid == []
    assert unverified == ["999/1899:1"]


def test_verify_mixed_real_and_fake(sqlite_db):
    valid, unverified = verify_citations(
        sqlite_db, ["82/2002:113", "82/2002:99999", "12/2003:1"]
    )
    assert len(valid) == 2
    assert unverified == ["82/2002:99999"]


def test_verify_malformed_ref_flagged(sqlite_db):
    valid, unverified = verify_citations(sqlite_db, ["nonsense", "", "82/2002"])
    assert valid == []
    # Empty strings are ignored; "nonsense" and "82/2002" (no article) are flagged
    assert sorted(unverified) == sorted(["nonsense", "82/2002"])


def test_verify_alt_separator_format(sqlite_db):
    valid, unverified = verify_citations(sqlite_db, ["82/2002 art. 113"])
    assert len(valid) == 1
    assert unverified == []


def test_scenario_arguments_have_no_hallucinations(sqlite_db, mock_llm):
    """The canned mock cites real articles, so every argument should be clean."""
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    for arg in case.arguments:
        assert (arg.unverified_citations or []) == [], (
            f"{arg.agent.value} round {arg.round_no} flagged: {arg.unverified_citations}"
        )


def test_hallucinated_citation_is_caught(sqlite_db, mock_llm, monkeypatch):
    """When the LLM emits a fake article number, it lands in unverified_citations
    on the persisted Argument — not in the verified `citations` list."""
    from tests import conftest as cf

    real_canned = cf._canned_response

    def _with_fake_citation(prompt: str) -> dict:
        resp = real_canned(prompt)
        # Prosecution prompt is the only one with `requested_relief`; inject a
        # bogus citation alongside the real one for that agent only.
        if "requested_relief" in prompt.lower():
            resp = dict(resp)
            resp["citations"] = ["82/2002:113", "82/2002:99999", "made-up-law:42"]
        return resp

    monkeypatch.setattr(cf, "_canned_response", _with_fake_citation)

    # Patch the MockLLMClient.complete to use the wrapped function
    from app.llm.base import LLMResponse

    async def _complete(self, system, messages, max_tokens=4096, response_format="text"):
        prompt = messages[-1]["content"] if messages else ""
        if response_format == "json":
            content = json.dumps(_with_fake_citation(prompt))
        else:
            content = "Mock response."
        return LLMResponse(content=content, model=self.model, usage={"input_tokens": 100, "output_tokens": 50})

    monkeypatch.setattr(cf.MockLLMClient, "complete", _complete)

    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    prosecution_args = [a for a in case.arguments if a.agent == AgentRole.PROSECUTION]
    assert prosecution_args, "no prosecution argument persisted"
    for arg in prosecution_args:
        unverified = arg.unverified_citations or []
        assert "82/2002:99999" in unverified, f"fake article not caught: {unverified}"
        assert "made-up-law:42" in unverified, f"fake law not caught: {unverified}"
        # The real citation should still resolve to a UUID, not get dropped
        assert len(arg.citations or []) == 1, (
            f"valid citation lost; got {arg.citations}"
        )


def test_trainee_submission_hallucinations_caught(sqlite_db, mock_llm):
    """Trainee-submitted citations go through the same verifier."""
    from datetime import datetime, timezone
    from app.models import TraineeRole, TrainingSession

    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    ts = TrainingSession(
        user_id="trainee",
        case_id=case_id,
        trainee_role=TraineeRole.DEFENSE,
        difficulty=2,
        started_at=datetime.now(timezone.utc),
    )
    sqlite_db.add(ts)
    sqlite_db.commit()

    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))
    assert result["status"] == "PAUSED_HIL"

    asyncio.run(orchestrator.submit_trainee_argument(
        sqlite_db, result["checkpoint_id"],
        content_en="Defense argument citing one real and one fake article.",
        content_ar=None,
        citations=["82/2002:115", "82/2002:99999"],
    ))

    sqlite_db.expire_all()
    case = sqlite_db.get(Case, case_id)
    trainee_args = [a for a in case.arguments if a.agent == AgentRole.TRAINEE]
    assert trainee_args, "trainee argument not persisted"
    arg = trainee_args[0]
    assert (arg.unverified_citations or []) == ["82/2002:99999"]
    assert len(arg.citations or []) == 1
