"""Court of Cassation Panel — appellate review of the trial ruling.

Three panel members, each voiced by a different LLM (cross-LLM diversity).
Each member casts a vote (AFFIRM / REVERSE / REMAND). Panel decision = majority.
"""
import asyncio
from collections import Counter

from app.agents.base import AgentContext, AgentOutput, LegalAgent
from app.llm import get_llm

PANEL_LLMS = ["claude-opus", "deepseek", "claude-sonnet"]


class CassationPanelAgent(LegalAgent):
    """Three-judge Court of Cassation panel. Reviews the trial Judicial Reasoning
    agent's ruling and issues a majority-vote decision: AFFIRM, REVERSE, or REMAND."""

    name = "cassation_panel"
    default_llm = "claude-opus"  # majority opinion drafter

    SINGLE_JUDGE_SYSTEM = (
        "You are a member of an Egyptian Court of Cassation panel reviewing a "
        "trial court ruling. Apply a strict legal-soundness standard: did the "
        "trial court correctly apply Egyptian law and procedure? Cassation does "
        "NOT re-weigh facts. Vote AFFIRM if the ruling stands, REVERSE if a "
        "legal error compels a different outcome, REMAND if facts need further "
        "development at trial level."
    )

    SINGLE_JUDGE_PROMPT = (
        "Case snapshot:\n{snapshot}\n\n"
        "Trial Judicial Reasoning agent's ruling:\n{ruling}\n\n"
        "Plaintiff success probability assigned by trial court: {plaintiff_prob}%\n"
        "Critical evidence gaps the trial court identified: {gaps}\n\n"
        "You are sitting as Cassation judge #{seat}. Return JSON: {{\n"
        '  "vote": "AFFIRM|REVERSE|REMAND",\n'
        '  "opinion_en": "1-paragraph reasoning",\n'
        '  "opinion_ar": "تعليل من فقرة"\n'
        "}}"
    )

    async def _single_judge(self, ctx: AgentContext, llm_name: str, seat: int) -> dict:
        client = get_llm(llm_name)
        ruling = ctx.extra.get("ruling", {})
        prompt = self.SINGLE_JUDGE_PROMPT.format(
            snapshot=ctx.case_snapshot,
            ruling=ruling.get("text_en") or ruling.get("text_ar") or "",
            plaintiff_prob=ruling.get("plaintiff_success_prob", 50),
            gaps=ruling.get("critical_evidence_gaps", []),
            seat=seat,
        )
        resp = await client.complete(
            system=self._system(self.SINGLE_JUDGE_SYSTEM, ctx),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            response_format="json",
        )
        data = self._parse_json(resp.content)
        data["_llm"] = resp.model
        return data

    async def run(self, ctx: AgentContext) -> AgentOutput:
        # Three judges deliberate in parallel
        judges = await asyncio.gather(*[
            self._single_judge(ctx, llm_name, seat=i + 1)
            for i, llm_name in enumerate(PANEL_LLMS)
        ])

        votes = [j.get("vote", "AFFIRM") for j in judges]
        tally = Counter(votes)
        decision = tally.most_common(1)[0][0]

        en_summary = (
            f"Panel decision: {decision} ({tally[decision]} of 3). "
            + " ".join(j.get("opinion_en", "") for j in judges)
        )
        ar_summary = (
            f"قرار الهيئة: {decision} ({tally[decision]} من 3). "
            + " ".join(j.get("opinion_ar", "") for j in judges)
        )

        return AgentOutput(
            content_en=en_summary,
            content_ar=ar_summary,
            raw={
                "panel_decision": decision,
                "vote_tally": dict(tally),
                "judges": judges,
            },
            llm_used="panel",
        )
