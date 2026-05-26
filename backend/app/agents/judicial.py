from app.agents.base import AgentContext, AgentOutput, LegalAgent


class JudicialAgent(LegalAgent):
    name = "judicial"
    default_llm = "claude-opus"

    SYSTEM = (
        "You are the Judicial Reasoning agent — an impartial Egyptian jurist with "
        "knowledge of Court of Cassation doctrine. After reviewing the prosecution "
        "and defense arguments and the statute corpus, you: (1) assign a plaintiff "
        "success probability (0-100); (2) identify critical evidence gaps; (3) "
        "reference relevant precedents conceptually; (4) issue a reasoned ruling. "
        "You also serve as the Ultimate Authority override — you may overrule the "
        "scoring layer if you detect a critical legal-fundamentals error."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Debate transcript:\n{prior}\n\n"
        "Return JSON: {{\n"
        '  "plaintiff_success_prob": 0-100,\n'
        '  "critical_evidence_gaps": ["..."],\n'
        '  "precedent_refs": ["doctrinal reference 1", "..."],\n'
        '  "ruling_en": "reasoned ruling, 2-4 paragraphs",\n'
        '  "ruling_ar": "نص الحكم المسبب",\n'
        '  "override_applied": true|false,\n'
        '  "override_reason": "explanation if override_applied"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            prior=ctx.prior_arguments or "(no arguments yet)",
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("ruling_en"),
            content_ar=data.get("ruling_ar"),
            raw=data,
            llm_used=resp.model,
        )
