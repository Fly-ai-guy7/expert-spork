from app.agents.base import AgentContext, AgentOutput, LegalAgent


class ScoringAgent(LegalAgent):
    name = "scoring"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Scoring agent for an Egyptian legal simulation. You evaluate "
        "a single legal argument on four dimensions on a 0-100 scale:\n"
        "  - factual: accuracy of factual claims against the case snapshot\n"
        "  - provable: how well the argument is supported by the available evidence\n"
        "  - unbiased: argumentation quality, free of unsupported assertions\n"
        "  - legal_law_based: grounding in the cited Egyptian statutes\n"
        "Also compute 'overall' as a weighted average."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Argument under evaluation:\n{argument}\n\n"
        "Cited statutes: {citations}\n\n"
        "Return JSON: {{\n"
        '  "factual": 0-100,\n'
        '  "provable": 0-100,\n'
        '  "unbiased": 0-100,\n'
        '  "legal_law_based": 0-100,\n'
        '  "overall": 0-100,\n'
        '  "rationale_en": "1-2 sentences",\n'
        '  "rationale_ar": "تعليل من جملة أو جملتين"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            argument=ctx.extra.get("argument", ""),
            citations=ctx.extra.get("citations", []),
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("rationale_en"),
            content_ar=data.get("rationale_ar"),
            raw=data,
            llm_used=resp.model,
        )
