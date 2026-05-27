from app.agents.base import AgentContext, AgentOutput, LegalAgent


class DamagesCalculatorAgent(LegalAgent):
    """Estimates likely damages awarded if the plaintiff prevails. Runs after the
    Ruling, before the Outcome. Output feeds the Outcome's risk/value calculation."""

    name = "damages_calculator"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Damages Calculator agent for an Egyptian legal simulation. "
        "Estimate the likely damages award if the plaintiff prevails. Cover: "
        "material damages (direct loss + expenses + lost profits), moral damages "
        "(where the law permits, e.g. 170 Civil Code, 113 IP Law), and any "
        "statutory remedies (seizure, recall, injunction). Quote ranges in EGP "
        "where data supports it. Be explicit about uncertainty."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Plaintiff success probability (from Judicial agent): {plaintiff_prob}%\n"
        "Ruling summary: {ruling_summary}\n\n"
        "Return JSON: {{\n"
        '  "material_damages_egp_min": 0,\n'
        '  "material_damages_egp_max": 0,\n'
        '  "moral_damages_egp": 0,\n'
        '  "non_monetary_remedies": ["e.g. seizure of infringing goods"],\n'
        '  "rationale_en": "1-2 paragraphs explaining the calculation",\n'
        '  "rationale_ar": "تعليل الحساب"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            plaintiff_prob=ctx.extra.get("plaintiff_prob", 50),
            ruling_summary=ctx.extra.get("ruling_summary", ""),
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
