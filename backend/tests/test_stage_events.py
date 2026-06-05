"""Per-stage SSE event coverage.

Runs a scenario end-to-end and asserts every stage boundary publishes a
non-terminal `running` event with the expected `stage` name. Pins the
event contract so the SPA can render a live pipeline timeline.
"""
from __future__ import annotations

import asyncio

from app.services import event_bus, orchestrator
from tests.scenarios import SCENARIOS
from tests.test_scenarios import _create_case_from_fixture, sqlite_db  # noqa: F401

# Conditional stages (skipped when their precondition is already satisfied or
# absent) are excluded here and tested separately:
#   - evidence_migration_complete : only when the case starts with no facts
#   - expert_witness_complete     : only when disputed facts exist
#   - coaching_complete           : only in training mode
EXPECTED_STAGES = {
    "court_clerk_complete",
    "procedural_specialist_complete",
    "precedent_researcher_complete",
    "judicial_complete",
    "damages_complete",
    "mediator_complete",
    "outcome_complete",
    "cassation_complete",
}


def test_pipeline_publishes_every_stage_event(sqlite_db, mock_llm):
    event_bus.reset()
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    result = asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))
    assert result["status"] == "COMPLETE"

    history = list(event_bus._channel(case_id).history)
    stages = {e.get("stage") for e in history if e.get("stage")}
    missing = EXPECTED_STAGES - stages
    assert not missing, f"missing stage events: {missing}; saw: {stages}"

    # Stage events are non-terminal so the SSE subscriber keeps listening
    for evt in history:
        if evt.get("stage") and evt["stage"] not in {"started", "cancel_requested"}:
            assert evt.get("status") == "running", f"non-running stage event: {evt}"


def test_round_events_have_round_number(sqlite_db, mock_llm):
    event_bus.reset()
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=2))

    history = list(event_bus._channel(case_id).history)
    round_events = [e for e in history if (e.get("stage") or "").startswith("round_")]
    assert len(round_events) == 2
    rounds = {e["round_no"] for e in round_events}
    assert rounds == {1, 2}


def test_expert_witness_event_only_when_run(sqlite_db, mock_llm):
    """Expert witness only fires when disputed facts exist; its stage event
    must match that."""
    event_bus.reset()
    # IP scenario has disputed facts → expert witness runs
    case_id = _create_case_from_fixture(sqlite_db, SCENARIOS["ip"])
    asyncio.run(orchestrator.run_simulation(sqlite_db, case_id, max_rounds=1))
    history = list(event_bus._channel(case_id).history)
    has_expert = any(e.get("stage") == "expert_witness_complete" for e in history)
    has_disputed_facts = any(f.disputed for f in sqlite_db.get(__import__("app.models", fromlist=["Case"]).Case, case_id).facts)
    if has_disputed_facts:
        assert has_expert, "expert_witness_complete missing despite disputed facts"
