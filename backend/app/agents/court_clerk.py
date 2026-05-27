from app.agents.base import AgentContext, AgentOutput, LegalAgent


class CourtClerkAgent(LegalAgent):
    """Generates the docket record for the case — case number, competent court
    designation, list of required filings, and a check of whether all mandatory
    documents are on file. Runs first, before any other agent."""

    name = "court_clerk"
    default_llm = "claude-sonnet"

    SYSTEM = (
        "You are the Court Clerk agent for an Egyptian legal simulation. "
        "Generate the formal docket record: an internal case number (year/seq), "
        "the competent court designation, the list of mandatory filings required "
        "for this area of law under the Code of Civil and Commercial Procedures "
        "(13/1968), and flag any that appear to be missing from the case file."
    )

    USER_TEMPLATE = (
        "Case snapshot:\n{snapshot}\n\n"
        "Area of law: {area_of_law}\n\n"
        "Return JSON: {{\n"
        '  "docket_number": "e.g. 2025/00123",\n'
        '  "competent_court": "Cairo Court of First Instance - Civil Circuit | Labour Court | ...",\n'
        '  "required_filings": ["statement of claim", "list of evidence", "..."],\n'
        '  "missing_filings": ["..."],\n'
        '  "filing_date": "ISO date estimated from facts",\n'
        '  "summary_en": "1-line procedural posture",\n'
        '  "summary_ar": "ملخص الموقف الإجرائي"\n'
        "}}"
    )

    async def run(self, ctx: AgentContext) -> AgentOutput:
        prompt = self.USER_TEMPLATE.format(
            snapshot=ctx.case_snapshot,
            area_of_law=ctx.extra.get("area_of_law", "GENERAL"),
        )
        resp = await self.llm.complete(
            system=self._system(self.SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        return AgentOutput(
            content_en=data.get("summary_en"),
            content_ar=data.get("summary_ar"),
            raw=data,
            llm_used=resp.model,
        )
