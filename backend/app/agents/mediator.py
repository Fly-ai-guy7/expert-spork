from app.agents.base import AgentContext, AgentOutput, LegalAgent


class MediatorAgent(LegalAgent):
    """Proposes pretrial settlement terms based on the case posture. Mandatory
    in labour disputes under Labour Law 12/2003 art. 82; valuable for trainees
    learning when to settle vs. proceed in any area. Runs after the Damages
    Calculator so the settlement proposal can reference the damages bracket."""

    name = "mediator"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are a Mediator in an Egyptian legal simulation. Propose realistic "
        "pretrial settlement terms taking into account the plaintiff success "
        "probability, damages estimate, and procedural posture. Your goal is to "
        "find a settlement that both sides could reasonably accept. Be specific "
        "about EGP figures, timing, and non-monetary terms."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Plaintiff success probability: {plaintiff_prob}%\n"
        "Damages estimate: {damages}\n\n"
        "Return JSON: {{\n"
        '  "recommended_settlement": "PROCEED|SETTLE|MIXED",\n'
        '  "settlement_value_egp": 0,\n'
        '  "settlement_terms": ["..."],\n'
        '  "rationale_en": "1-2 paragraphs explaining the recommendation",\n'
        '  "rationale_ar": "تعليل التوصية"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            plaintiff_prob=ctx.extra.get("plaintiff_prob", 50),
            damages=ctx.extra.get("damages_estimate", {}),
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("rationale_en"),
            content_ar=data.get("rationale_ar"),
            raw=data,
            llm_used=resp.model,
        )
