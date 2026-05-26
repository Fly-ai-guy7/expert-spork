import logging

from sqlalchemy.orm import Session

from app.agents.base import AgentContext
from app.disclaimer import SYSTEM_DISCLAIMER_PREFIX
from app.i18n import Lang
from app.llm import CacheBlock, get_llm
from app.models import (
    Case,
    CaseSource,
    EvidenceKind,
    Party,
    PartyKind,
    PartyRole,
)
from app.models.evidence import Evidence
from app.models.fact import Fact

logger = logging.getLogger(__name__)


SYSTEM = (
    "You generate realistic but synthetic Egyptian legal practice cases for "
    "trainee lawyers. The case must be coherent, statute-grounded, and contain "
    "genuine ambiguity so the trainee must reason rather than memorize."
)


PROMPT_TEMPLATE = (
    "Generate a practice case in area_of_law='{area}', difficulty={difficulty}/5 "
    "(1=clear-cut, 5=heavily disputed multi-claim), primary language='{lang}'.\n\n"
    "Return JSON with this exact shape:\n"
    "{{\n"
    '  "title_en": "...", "title_ar": "...",\n'
    '  "summary_en": "two-paragraph factual summary", "summary_ar": "ملخص فقرتين",\n'
    '  "parties": [\n'
    '    {{"role": "PLAINTIFF", "kind": "NATURAL|LEGAL", "name_en": "...", "name_ar": "..."}},\n'
    '    {{"role": "DEFENDANT", "kind": "NATURAL|LEGAL", "name_en": "...", "name_ar": "..."}}\n'
    "  ],\n"
    '  "facts": [\n'
    '    {{"text_en": "...", "text_ar": "...", "disputed": true|false, "order_index": 0}}\n'
    "  ],\n"
    '  "evidence": [\n'
    '    {{"kind": "DOCUMENT|WITNESS|PHYSICAL", "title_en": "...", "title_ar": "...", "missing": false}}\n'
    "  ],\n"
    '  "suggested_statutes": ["82/2002", "..."]\n'
    "}}\n\n"
    "Provide 5-8 facts (at least 1 disputed at difficulty>=2), 3-5 evidence items "
    "(1-2 marked missing if difficulty>=3), and 2-3 parties total."
)


async def generate_case(
    db: Session,
    area_of_law: str,
    difficulty: int,
    language: str,
    user_id: str | None = None,
) -> Case:
    lang = Lang(language)
    prompt = PROMPT_TEMPLATE.format(area=area_of_law, difficulty=difficulty, lang=lang.value)
    llm = get_llm("claude-opus")
    resp = await llm.complete(
        system=[CacheBlock(text=SYSTEM_DISCLAIMER_PREFIX + SYSTEM, cacheable=False)],
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        response_format="json",
    )
    # Reuse the safe JSON parser from LegalAgent
    from app.agents.base import LegalAgent
    data = LegalAgent._parse_json(resp.content)

    case = Case(
        title_en=data.get("title_en"),
        title_ar=data.get("title_ar"),
        summary_en=data.get("summary_en"),
        summary_ar=data.get("summary_ar"),
        language_primary=lang.value,
        source=CaseSource.AI_GENERATED,
        difficulty=difficulty,
        area_of_law=area_of_law,
        created_by=user_id,
    )
    db.add(case)
    db.flush()

    for p in data.get("parties", []) or []:
        try:
            role = PartyRole(p.get("role", "PLAINTIFF"))
        except ValueError:
            role = PartyRole.PLAINTIFF
        try:
            kind = PartyKind(p.get("kind", "NATURAL"))
        except ValueError:
            kind = PartyKind.NATURAL
        db.add(
            Party(
                case_id=case.id, role=role, kind=kind,
                name_en=p.get("name_en"), name_ar=p.get("name_ar"),
            )
        )

    for i, f in enumerate(data.get("facts", []) or []):
        db.add(
            Fact(
                case_id=case.id,
                text_en=f.get("text_en"), text_ar=f.get("text_ar"),
                disputed=bool(f.get("disputed", False)),
                order_index=int(f.get("order_index", i)),
            )
        )

    for e in data.get("evidence", []) or []:
        try:
            kind = EvidenceKind(e.get("kind", "DOCUMENT"))
        except ValueError:
            kind = EvidenceKind.DOCUMENT
        db.add(
            Evidence(
                case_id=case.id, kind=kind,
                title_en=e.get("title_en"), title_ar=e.get("title_ar"),
                description=e.get("description"), missing=bool(e.get("missing", False)),
            )
        )

    db.commit()
    db.refresh(case)
    return case
