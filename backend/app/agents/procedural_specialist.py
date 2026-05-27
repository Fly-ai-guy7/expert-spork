from app.agents.base import AgentContext, AgentOutput, LegalAgent


class ProceduralSpecialistAgent(LegalAgent):
    """Analyzes procedural defenses upfront — jurisdiction, standing, limitation,
    competent court, mandatory pre-litigation steps. Runs after Evidence Migration
    so downstream agents can incorporate these issues."""

    name = "procedural_specialist"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Procedural Specialist agent for an Egyptian legal simulation. "
        "Identify all procedural issues that could affect this case under the Code "
        "of Civil and Commercial Procedures (13/1968) and area-specific procedural "
        "rules. Cover: jurisdiction, standing, limitation periods, mandatory "
        "pre-litigation steps (e.g. labour office filings, consumer agency mediation), "
        "competent court selection. Be concise; surface only material issues."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Return JSON: {{\n"
        '  "jurisdiction_issues": ["..."],\n'
        '  "standing_issues": ["..."],\n'
        '  "limitation_concerns": ["e.g. claim may be time-barred under 374 Civil Code"],\n'
        '  "mandatory_pre_litigation": ["e.g. labour office mediation under 12/2003 art. 82"],\n'
        '  "competent_court": "civil court | labour court | commercial court | ...",\n'
        '  "summary_en": "1-paragraph procedural posture",\n'
        '  "summary_ar": "ملخص الموقف الإجرائي"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(snapshot=ctx.case_snapshot)
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("summary_en"),
            content_ar=data.get("summary_ar"),
            raw=data,
            llm_used=resp.model,
        )
