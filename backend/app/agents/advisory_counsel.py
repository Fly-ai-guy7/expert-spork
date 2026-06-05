from app.agents.base import AgentContext, AgentOutput, LegalAgent


class AdvisoryCounselAgent(LegalAgent):
    """A private mentor for the trainee. It coaches — it does not argue the case.

    Given the case, the debate so far, and the trainee's draft, it returns strategic
    guidance, statutes the trainee may have missed, and the weak points an opponent
    would attack — before the trainee commits their argument.
    """

    name = "advisory_counsel"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are Advisory Counsel — a senior Egyptian lawyer privately mentoring a "
        "trainee who is about to make their argument. You do NOT argue the case "
        "yourself and you do not write the argument for them. You coach: surface the "
        "statutes they should cite, the strongest line of reasoning for their side, "
        "and the weaknesses opposing counsel will exploit. Be specific and grounded "
        "in the Egyptian statute corpus. Cite articles by short_code (e.g. "
        "'82/2002 art. 115')."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "You are advising the {role} side (the trainee).\n\n"
        "Debate so far:\n{prior}\n\n"
        "The trainee's current draft argument (may be empty):\n{draft}\n\n"
        "Draft citations: {citations}\n\n"
        "Return JSON: {{\n"
        '  "strategy_en": "2-4 sentences of strategic guidance",\n'
        '  "strategy_ar": "إرشاد استراتيجي",\n'
        '  "suggested_citations": ["short_code:article_number", ...],\n'
        '  "strengths": ["points the trainee should press"],\n'
        '  "risks": ["weaknesses the opponent will attack"],\n'
        '  "missing_arguments": ["arguments the trainee has not yet made"]\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            role=ctx.extra.get("trainee_role", "DEFENSE"),
            prior=ctx.prior_arguments or "(none yet)",
            draft=ctx.extra.get("draft") or "(trainee has not drafted anything yet)",
            citations=ctx.extra.get("citations", []),
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("strategy_en"),
            content_ar=data.get("strategy_ar"),
            raw=data,
            llm_used=resp.model,
        )
