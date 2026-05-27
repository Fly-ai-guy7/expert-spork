from app.agents.base import AgentContext, AgentOutput, LegalAgent


class ExpertWitnessAgent(LegalAgent):
    """Court-appointed expert per Code of Civil and Commercial Procedures
    art. 104. Opines on disputed technical/factual matters that the judge
    cannot resolve on the face of the record (defective product, trademark
    confusion likelihood, accounting/valuation, etc.). Runs after Evidence
    Migration if any fact is marked `disputed`."""

    name = "expert_witness"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are a court-appointed Expert Witness in an Egyptian legal simulation, "
        "engaged per art. 104 of the Code of Civil and Commercial Procedures (13/1968). "
        "You opine ONLY on the disputed technical / factual matters supplied. You are "
        "neutral — your opinion belongs to neither side. Cite the methodology you would "
        "use in a real expert report. Be concise."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Disputed facts requiring expert opinion:\n{disputed_facts}\n\n"
        "Return JSON: {{\n"
        '  "expertise_area": "trademark similarity | product defect | valuation | ...",\n'
        '  "methodology": "1-2 lines describing how a real expert would approach this",\n'
        '  "findings": [\n'
        '    {{"fact_under_review": "...", "opinion_en": "...", "opinion_ar": "...", "confidence": "low|medium|high"}}\n'
        "  ],\n"
        '  "expert_opinion_en": "1-paragraph executive opinion",\n'
        '  "expert_opinion_ar": "رأي الخبير في فقرة موجزة"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        disputed = ctx.extra.get("disputed_facts") or [
            f for f in ctx.case_snapshot.get("facts", []) if f.get("disputed")
        ]
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            disputed_facts=disputed or "(none — agent should return empty findings)",
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("expert_opinion_en"),
            content_ar=data.get("expert_opinion_ar"),
            raw=data,
            llm_used=resp.model,
        )
