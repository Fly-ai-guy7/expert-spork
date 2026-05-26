from app.agents.base import AgentContext, AgentOutput, LegalAgent


class EvidenceMigrationAgent(LegalAgent):
    name = "evidence_migration"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Evidence Migration agent for an Egyptian legal simulation. "
        "Parse the raw case description into a structured chronology, separate "
        "disputed from undisputed facts, and identify missing evidence that would "
        "be critical for either side."
    )

    USER_TEMPLATE = (
        "Case input:\n{snapshot}\n\n"
        "Return a JSON object with this exact shape:\n"
        "{{\n"
        '  "facts": [{{"text_en": "...", "text_ar": "...", "disputed": true|false, "order_index": 0}}],\n'
        '  "evidence": [{{"kind": "DOCUMENT|WITNESS|PHYSICAL", "title_en": "...", "title_ar": "...", "description": "...", "missing": true|false}}],\n'
        '  "summary_en": "one-paragraph factual summary",\n'
        '  "summary_ar": "ملخص واقعي من فقرة واحدة"\n'
        "}}\n"
        "Be concise. Generate Arabic alongside English when possible."
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(snapshot=ctx.case_snapshot)
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("summary_en"),
            content_ar=data.get("summary_ar"),
            raw=data,
            llm_used=resp.model,
        )
