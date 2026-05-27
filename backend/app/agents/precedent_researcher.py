from app.agents.base import AgentContext, AgentOutput, LegalAgent


class PrecedentResearcherAgent(LegalAgent):
    """Surfaces Court of Cassation doctrine and analogous precedents relevant to
    the case. Runs before the Judicial Reasoning agent so the judge has explicit
    precedent context. This is conceptual — there is no precedent DB in the
    scaffold; the LLM draws on its training."""

    name = "precedent_researcher"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Precedent Researcher agent for an Egyptian legal simulation. "
        "Identify Court of Cassation doctrine and analogous precedent themes that "
        "bear on this case. Reference doctrinal principles rather than fabricated "
        "case numbers — name the legal principle and the typical court reasoning. "
        "Output is consumed by the Judicial Reasoning agent."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Prior debate arguments:\n{prior}\n\n"
        "Return JSON: {{\n"
        '  "doctrines": [\n'
        '    {{"name": "...", "principle_en": "...", "principle_ar": "...", "supports_side": "PLAINTIFF|DEFENDANT|NEUTRAL"}}\n'
        "  ],\n"
        '  "analogous_themes": ["theme 1", "..."],\n'
        '  "summary_en": "1-paragraph precedent landscape",\n'
        '  "summary_ar": "ملخص المشهد السوابقي"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            prior=ctx.prior_arguments or "(none)",
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("summary_en"),
            content_ar=data.get("summary_ar"),
            raw=data,
            llm_used=resp.model,
        )
