from app.agents.base import AgentContext, AgentOutput, LegalAgent


class DefenseAgent(LegalAgent):
    name = "defense"
    default_llm = "deepseek"

    SYSTEM = (
        "You are the Defense agent in an Egyptian legal simulation. You construct "
        "the defendant's argument: procedural defenses (jurisdiction, standing, "
        "limitation periods), substantive defenses, and counterclaims, grounded in "
        "Egyptian law. Cite specific articles by short_code. Attack the prosecution's "
        "weakest evidentiary points."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Prior arguments (most recent is the prosecution's case):\n{prior}\n\n"
        "Produce your defense for round {round_no}. "
        "Return JSON: {{\n"
        '  "argument_en": "...",\n'
        '  "argument_ar": "...",\n'
        '  "citations": ["short_code:article_number", ...],\n'
        '  "procedural_defenses": ["..."],\n'
        '  "substantive_defenses": ["..."],\n'
        '  "counterclaims": ["..."]\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            prior=ctx.prior_arguments or "(none)",
            round_no=ctx.extra.get("round_no", 1),
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("argument_en"),
            content_ar=data.get("argument_ar"),
            raw=data,
            llm_used=resp.model,
        )
