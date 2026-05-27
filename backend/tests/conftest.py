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
    """Route to a canned response based on UNIQUE tokens in each agent's user prompt.

    Matching uses tokens that appear ONLY in one agent's JSON schema template, in
    most-specific-first order. The first match wins.
    """
    p = prompt.lower()

    # Damages — unique token "material_damages_egp_min"
    if "material_damages_egp_min" in p:
        return {
            "material_damages_egp_min": 50000,
            "material_damages_egp_max": 250000,
            "moral_damages_egp": 50000,
            "non_monetary_remedies": ["seizure and destruction of infringing goods under 82/2002 art. 113"],
            "rationale_en": "Damages bracket reflects documented sales volume; moral damages capped per typical Cassation guidance.",
            "rationale_ar": "نطاق التعويض يعكس حجم المبيعات الموثق، والتعويض الأدبي ضمن نطاق محكمة النقض.",
        }

    # Procedural Specialist — unique tokens "jurisdiction_issues" + "competent_court"
    if "jurisdiction_issues" in p and "competent_court" in p:
        return {
            "jurisdiction_issues": [],
            "standing_issues": [],
            "limitation_concerns": ["claim filed within applicable limitation period"],
            "mandatory_pre_litigation": [],
            "competent_court": "civil court",
            "summary_en": "Procedurally clean — standard civil-court action.",
            "summary_ar": "موقف إجرائي سليم — دعوى مدنية اعتيادية.",
        }

    # Precedent Researcher — unique tokens "doctrines" + "analogous_themes"
    if "doctrines" in p and "analogous_themes" in p:
        return {
            "doctrines": [
                {"name": "prior-use defense", "principle_en": "Bona fide prior use limits enforcement.", "principle_ar": "الاستخدام السابق بحسن النية يحد من الإنفاذ.", "supports_side": "DEFENDANT"},
            ],
            "analogous_themes": ["bad-faith adoption", "evidentiary burden on prior use"],
            "summary_en": "Doctrinal landscape favors plaintiff if bad faith is proven; otherwise prior-use defense is viable.",
            "summary_ar": "المشهد السوابقي يدعم المدعي إن ثبت سوء النية، وإلا فدفع الاستخدام السابق وارد.",
        }

    # Judicial — unique token "plaintiff_success_prob"
    if "plaintiff_success_prob" in p:
        return {
            "plaintiff_success_prob": 62,
            "critical_evidence_gaps": ["proof of bad faith"],
            "precedent_refs": ["Cassation doctrine on prior use"],
            "ruling_en": "Plaintiff has the stronger position.",
            "ruling_ar": "موقف المدعي أقوى.",
            "override_applied": False,
            "override_reason": "",
        }

    # Scoring — unique combination "factual" + "provable" + "legal_law_based"
    if "factual" in p and "provable" in p and "legal_law_based" in p:
        return {
            "factual": 75, "provable": 60, "unbiased": 80, "legal_law_based": 70,
            "overall": 71,
            "rationale_en": "Solid citations, thin on intent.",
            "rationale_ar": "استشهادات جيدة، الدليل ضعيف.",
        }

    # Prosecution — unique token "requested_relief"
    if "requested_relief" in p:
        return {
            "argument_en": "Defendant infringed the registered mark and bears liability.",
            "argument_ar": "اعتدى المدعى عليه على العلامة المسجلة وتترتب عليه المسؤولية.",
            "citations": ["82/2002:113"],
            "strengths": ["registered mark", "documented sales"],
            "requested_relief": "compensation and seizure",
        }

    # Defense — unique token "counterclaims" (procedural_defenses + substantive_defenses also unique together)
    if "counterclaims" in p and "procedural_defenses" in p:
        return {
            "argument_en": "Defendant has bona fide prior use since 2019 and the claim is time-barred.",
            "argument_ar": "للمدعى عليه استخدام سابق بحسن النية منذ 2019، والدعوى متقادمة.",
            "citations": ["82/2002:115"],
            "procedural_defenses": ["limitation"],
            "substantive_defenses": ["prior use"],
            "counterclaims": [],
        }

    # Case Generator — unique token "suggested_statutes"
    if "suggested_statutes" in p:
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

    # Evidence Migration — unique combination "structured chronology" OR ("facts" + "evidence" + "order_index" in template)
    if "structured chronology" in p or ("order_index" in p and '"facts"' in p):
        return {
            "facts": [
                {"text_en": "Defendant began selling product X in 2024.", "text_ar": "بدأ بيع س في 2024.", "disputed": False, "order_index": 0},
                {"text_en": "Plaintiff registered trademark in 2021.", "text_ar": "سُجّلت العلامة 2021.", "disputed": False, "order_index": 1},
            ],
            "evidence": [{"kind": "DOCUMENT", "title_en": "Trademark cert", "title_ar": "شهادة", "missing": False}],
            "summary_en": "Trademark dispute.",
            "summary_ar": "نزاع علامة.",
        }

    if "generate a practice case" in p or "synthetic egyptian" in p:
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
