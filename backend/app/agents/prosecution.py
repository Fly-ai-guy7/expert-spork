from app.agents.base import AgentContext, AgentOutput, LegalAgent


class ProsecutionAgent(LegalAgent):
    name = "prosecution"
    default_llm = "claude-opus"

    SYSTEM = (
        "You are the Prosecution agent in an Egyptian legal simulation. You "
        "construct the plaintiff's argument grounded in the Egyptian Civil Code, "
        "Commercial Code, IP Rights Law, and other applicable statutes provided. "
        "Your goal: prove the defendant's liability. Cite specific articles by "
        "short_code (e.g. '82/2002 art. 113'). Identify evidentiary strengths."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Prior arguments in this debate:\n{prior}\n\n"
        "Produce your prosecution argument for round {round_no}. "
        "Return JSON: {{\n"
        '  "argument_en": "...",\n'
        '  "argument_ar": "...",\n'
        '  "citations": ["short_code:article_number", ...],\n'
        '  "strengths": ["..."],\n'
        '  "requested_relief": "..."\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            prior=ctx.prior_arguments or "(none — opening argument)",
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
