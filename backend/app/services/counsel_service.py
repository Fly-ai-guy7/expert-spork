import uuid

from sqlalchemy.orm import Session

from app.agents import AdvisoryCounselAgent, AgentContext
from app.disclaimer import disclaimer_block
from app.i18n import Lang
from app.services.corpus_service import build_statute_block
from app.services.orchestrator import _build_prior, _case_snapshot, _load_case


async def generate_counsel(
    db: Session,
    case_id: uuid.UUID,
    trainee_role: str,
    draft_en: str | None = None,
    draft_ar: str | None = None,
    citations: list[str] | None = None,
) -> dict:
    case = _load_case(db, case_id)
    lang = Lang(case.language_primary)
    ctx = AgentContext(
        case_id=case_id,
        lang=lang,
        case_snapshot=_case_snapshot(case),
        prior_arguments=_build_prior(case),
        statute_block=build_statute_block(db, None, lang),
        extra={
            "trainee_role": trainee_role,
            "draft": draft_en or draft_ar or "",
            "citations": citations or [],
        },
    )
    out = await AdvisoryCounselAgent().run(ctx)
    return {"disclaimer": disclaimer_block(), "advice": out.raw, "llm_used": out.llm_used}
