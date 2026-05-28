"""Test fixtures.

Agent-level tests run without a database (mocked LLM only).
DB-dependent tests use the docker-compose Postgres; they are skipped if
DATABASE_URL isn't reachable. Run via `make test-backend`.
"""
import json
import os
from typing import Literal

import pytest

from app.llm import factory
from app.llm.base import CacheBlock, LLMClient, LLMResponse


class MockLLMClient(LLMClient):
    name = "mock"

    def __init__(self, model: str = "mock"):
        self.model = model
        self.name = "mock"
        self.calls: list[dict] = []

    async def complete(
        self,
        system: str | list[CacheBlock],
        messages: list[dict],
        max_tokens: int = 4096,
        response_format: Literal["text", "json"] = "text",
    ) -> LLMResponse:
        prompt = messages[-1]["content"] if messages else ""
        self.calls.append({"prompt": prompt, "format": response_format})
        if response_format == "json":
            content = json.dumps(_canned_response(prompt))
        else:
            content = "Mock response."
        return LLMResponse(
            content=content,
            model=self.model,
            usage={"input_tokens": 100, "output_tokens": 50},
        )


def _canned_response(prompt: str) -> dict:
    p = prompt.lower()
    if "structured chronology" in p or "summary_en" in p and "summary_ar" in p and "evidence" in p:
        return {
            "facts": [
                {"text_en": "Defendant began selling product X in 2024.", "text_ar": "بدأ بيع س في 2024.", "disputed": False, "order_index": 0},
                {"text_en": "Plaintiff registered trademark in 2021.", "text_ar": "سُجّلت العلامة 2021.", "disputed": False, "order_index": 1},
            ],
            "evidence": [{"kind": "DOCUMENT", "title_en": "Trademark cert", "title_ar": "شهادة", "missing": False}],
            "summary_en": "Trademark dispute.",
            "summary_ar": "نزاع علامة.",
        }
    if "prosecution argument" in p or ('argument_en' in p and 'requested_relief' in p):
        return {
            "argument_en": "Defendant infringed the registered mark.",
            "argument_ar": "اعتدى المدعى عليه على العلامة.",
            "citations": ["82/2002:113"],
            "strengths": ["registered mark"],
            "requested_relief": "compensation",
        }
    if "defense" in p and ("procedural_defenses" in p or "substantive_defenses" in p):
        return {
            "argument_en": "Defendant has prior use since 2019.",
            "argument_ar": "للمدعى عليه استخدام سابق منذ 2019.",
            "citations": ["82/2002:115"],
            "procedural_defenses": ["limitation"],
            "substantive_defenses": ["prior use"],
            "counterclaims": [],
        }
    if "plaintiff_success_prob" in p or "ruling_en" in p:
        return {
            "plaintiff_success_prob": 62,
            "critical_evidence_gaps": ["proof of bad faith"],
            "precedent_refs": ["Cassation 1234/2019"],
            "ruling_en": "Plaintiff has the stronger position.",
            "ruling_ar": "موقف المدعي أقوى.",
            "override_applied": False,
            "override_reason": "",
        }
    if "factual" in p and "provable" in p and "unbiased" in p:
        return {
            "factual": 75, "provable": 60, "unbiased": 80, "legal_law_based": 70,
            "overall": 71,
            "rationale_en": "Solid citations, thin on intent.",
            "rationale_ar": "استشهادات جيدة، الدليل ضعيف.",
        }
    if "strategy_en" in p or "missing_arguments" in p or "advisory counsel" in p:
        return {
            "strategy_en": "Lead with the prior-use defense and force the plaintiff to prove bad faith.",
            "strategy_ar": "ابدأ بدفع الاستخدام السابق.",
            "suggested_citations": ["82/2002:115"],
            "strengths": ["clear prior use since 2019"],
            "risks": ["thin documentary trail"],
            "missing_arguments": ["limitation period"],
        }
    if "generate a practice case" in p or "synthetic egyptian" in p or "area_of_law" in p:
        return {
            "title_en": "ALPHA-T v. ALPHATEK",
            "title_ar": "ألفا-ت ضد ألفاتك",
            "summary_en": "Trademark confusion claim.",
            "summary_ar": "ادعاء لبس علامة.",
            "parties": [
                {"role": "PLAINTIFF", "kind": "LEGAL", "name_en": "Alpha Tech LLC", "name_ar": "ألفا تك"},
                {"role": "DEFENDANT", "kind": "LEGAL", "name_en": "Beta Corp", "name_ar": "بيتا"},
            ],
            "facts": [{"text_en": "Mark registered 2021.", "text_ar": "العلامة 2021.", "disputed": False, "order_index": 0}],
            "evidence": [{"kind": "DOCUMENT", "title_en": "Cert", "title_ar": "شهادة", "missing": False}],
            "suggested_statutes": ["82/2002"],
        }
    return {"content_en": "ok", "content_ar": "حسناً"}


@pytest.fixture
def mock_llm(monkeypatch):
    client = MockLLMClient()
    # Patch every consumer of get_llm so cached instances don't escape
    monkeypatch.setattr(factory, "get_llm", lambda _name=None: client)
    from app.agents import base as agent_base
    monkeypatch.setattr(agent_base, "get_llm", lambda _name=None: client)
    from app.services import case_generator as cg
    monkeypatch.setattr(cg, "get_llm", lambda _name=None: client)
    return client


def _can_connect_pg() -> bool:
    if not os.environ.get("DATABASE_URL"):
        return False
    try:
        from sqlalchemy import create_engine, text
        e = create_engine(os.environ["DATABASE_URL"])
        with e.connect() as c:
            c.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


pg_required = pytest.mark.skipif(not _can_connect_pg(), reason="Requires Postgres (run via docker-compose)")
