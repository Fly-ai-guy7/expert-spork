import asyncio
from statistics import mean

from app.agents.base import AgentContext, AgentOutput, LegalAgent
from app.agents.judicial import JudicialAgent

FOR_PLAINTIFF = "FOR_PLAINTIFF"
FOR_DEFENDANT = "FOR_DEFENDANT"


def _dedup(items: list) -> list:
    seen: set = set()
    out: list = []
    for item in items:
        key = item if isinstance(item, str) else repr(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


class JudicialCouncilAgent(LegalAgent):
    """A panel of judges, each backed by a different LLM.

    Every member renders an independent verdict via the single-judge prompt; the
    council then aggregates them into a majority ruling, records dissents, and
    averages the plaintiff success probability. A tie resolves for the defendant —
    the plaintiff carries the burden of proof and has not met it.
    """

    name = "judicial_council"
    default_llm = "claude-opus"

    def __init__(self, members: list[str] | None = None):
        self.members = members or ["claude-opus", "claude-sonnet", "deepseek"]
        super().__init__(llm=self.members[0])

    async def run(self, ctx: AgentContext) -> AgentOutput:
        judges = [JudicialAgent(llm=member) for member in self.members]
        outs = await asyncio.gather(*(judge.run(ctx) for judge in judges))

        panel: list[dict] = []
        for member_llm, out in zip(self.members, outs):
            raw = out.raw
            prob = float(raw.get("plaintiff_success_prob", 50))
            panel.append({
                "member_llm": member_llm,
                "llm_used": out.llm_used,
                "plaintiff_success_prob": prob,
                "verdict": FOR_PLAINTIFF if prob >= 50 else FOR_DEFENDANT,
                "override_flagged": bool(raw.get("override_applied", False)),
                "override_reason": raw.get("override_reason") or None,
                "ruling_en": raw.get("ruling_en"),
                "ruling_ar": raw.get("ruling_ar"),
                "critical_evidence_gaps": raw.get("critical_evidence_gaps") or [],
                "precedent_refs": raw.get("precedent_refs") or [],
            })

        for_plaintiff = sum(1 for m in panel if m["verdict"] == FOR_PLAINTIFF)
        for_defendant = len(panel) - for_plaintiff
        majority = FOR_PLAINTIFF if for_plaintiff > for_defendant else FOR_DEFENDANT
        avg_prob = round(mean(m["plaintiff_success_prob"] for m in panel), 1)
        override_applied = sum(1 for m in panel if m["override_flagged"]) * 2 > len(panel)

        gaps = _dedup([g for m in panel for g in m["critical_evidence_gaps"]])
        precedents = _dedup([p for m in panel for p in m["precedent_refs"]])

        majority_members = [m for m in panel if m["verdict"] == majority]
        dissent_members = [m for m in panel if m["verdict"] != majority]
        lead = (majority_members or panel)[0]

        vote = f"{for_plaintiff}–{for_defendant}"
        side_en = "plaintiff" if majority == FOR_PLAINTIFF else "defendant"
        side_ar = "المدعي" if majority == FOR_PLAINTIFF else "المدعى عليه"
        header_en = f"Judicial Council of {len(panel)} — {vote} for the {side_en}. "
        header_ar = f"هيئة قضائية من {len(panel)} أعضاء — {vote} لصالح {side_ar}. "
        ruling_en = header_en + (lead.get("ruling_en") or lead.get("ruling_ar") or "")
        ruling_ar = header_ar + (lead.get("ruling_ar") or lead.get("ruling_en") or "")

        dissent_en = self._join_dissents(dissent_members, "ruling_en") or None
        dissent_ar = self._join_dissents(dissent_members, "ruling_ar") or None

        raw = {
            "plaintiff_success_prob": avg_prob,
            "critical_evidence_gaps": gaps,
            "precedent_refs": precedents,
            "ruling_en": ruling_en,
            "ruling_ar": ruling_ar,
            "override_applied": override_applied,
            "council_size": len(panel),
            "council_vote": {"for_plaintiff": for_plaintiff, "for_defendant": for_defendant},
            "majority_verdict": majority,
            "dissent_en": dissent_en,
            "dissent_ar": dissent_ar,
            "panel": panel,
        }
        llm_used = "+".join(m["llm_used"] for m in panel) or f"council:{len(panel)}"
        return AgentOutput(content_en=ruling_en, content_ar=ruling_ar, raw=raw, llm_used=llm_used)

    @staticmethod
    def _join_dissents(members: list[dict], key: str) -> str:
        parts = []
        for m in members:
            text = m.get(key) or m.get("ruling_en") or m.get("ruling_ar")
            if text:
                parts.append(f"[{m['member_llm']}] {text}")
        return " ".join(parts)
