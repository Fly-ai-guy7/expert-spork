import uuid

import pytest

from app.agents import (
    AdvisoryCounselAgent,
    DefenseAgent,
    EvidenceMigrationAgent,
    JudicialAgent,
    JudicialCouncilAgent,
    ProsecutionAgent,
    ScoringAgent,
)
from app.agents.base import AgentContext
from app.i18n import Lang


@pytest.fixture
def ctx() -> AgentContext:
    return AgentContext(
        case_id=uuid.uuid4(),
        lang=Lang.EN,
        case_snapshot={"parties": [], "facts": [], "evidence": []},
        statute_block="(test statute block)",
    )


async def test_evidence_migration(mock_llm, ctx):
    out = await EvidenceMigrationAgent().run(ctx)
    assert out.raw.get("facts") is not None
    assert out.content_en or out.content_ar


async def test_prosecution(mock_llm, ctx):
    ctx.extra = {"round_no": 1}
    out = await ProsecutionAgent().run(ctx)
    assert out.content_en or out.content_ar
    assert "82/2002" in str(out.raw.get("citations", []))


async def test_defense(mock_llm, ctx):
    ctx.extra = {"round_no": 1}
    out = await DefenseAgent().run(ctx)
    assert out.content_en or out.content_ar


async def test_judicial(mock_llm, ctx):
    out = await JudicialAgent().run(ctx)
    assert 0 <= out.raw["plaintiff_success_prob"] <= 100
    assert out.content_en or out.content_ar


async def test_scoring(mock_llm, ctx):
    ctx.extra = {"argument": "Defendant infringed the mark.", "citations": ["82/2002:113"]}
    out = await ScoringAgent().run(ctx)
    for k in ("factual", "provable", "unbiased", "legal_law_based", "overall"):
        assert 0 <= out.raw[k] <= 100


async def test_judicial_council(mock_llm, ctx):
    out = await JudicialCouncilAgent(members=["claude-opus", "claude-sonnet", "deepseek"]).run(ctx)
    raw = out.raw
    assert raw["council_size"] == 3
    assert len(raw["panel"]) == 3
    assert 0 <= raw["plaintiff_success_prob"] <= 100
    vote = raw["council_vote"]
    assert vote["for_plaintiff"] + vote["for_defendant"] == 3
    assert raw["majority_verdict"] in ("FOR_PLAINTIFF", "FOR_DEFENDANT")
    assert out.content_en


async def test_advisory_counsel(mock_llm, ctx):
    ctx.extra = {"trainee_role": "DEFENSE", "draft": "Prior use since 2019.", "citations": ["82/2002:115"]}
    out = await AdvisoryCounselAgent().run(ctx)
    assert out.raw.get("suggested_citations") is not None
    assert out.content_en or out.content_ar
