import { useTranslation } from "react-i18next";
import { cn } from "@/lib/cn";
import type { CaseStatusPayload } from "@/api/types";

const STAGE_KEYS = [
  "case.evidence_migration",
  "case.prosecution",
  "case.defense",
  "case.scoring",
  "case.judicial",
  "case.ruling",
  "case.outcome",
];

export function PipelineTimeline({ status }: { status: CaseStatusPayload | undefined }) {
  const { t } = useTranslation();
  const completedIdx = computeStage(status);
  return (
    <ol className="flex flex-col gap-1 text-xs md:flex-row md:flex-wrap md:gap-2">
      {STAGE_KEYS.map((k, i) => {
        const state = i < completedIdx ? "done" : i === completedIdx ? "active" : "pending";
        return (
          <li
            key={k}
            className={cn(
              "flex items-center gap-2 rounded-md border px-3 py-2",
              state === "done" && "bg-emerald-50 border-emerald-300 text-emerald-900",
              state === "active" && "bg-amber-50 border-amber-300 text-amber-900 md:font-semibold",
              state === "pending" && "bg-slate-50 border-slate-200 text-slate-500"
            )}
          >
            <span className="font-mono opacity-60 md:hidden">{i + 1}.</span>
            <span>{t(k)}</span>
          </li>
        );
      })}
    </ol>
  );
}

function computeStage(status: CaseStatusPayload | undefined): number {
  if (!status) return 0;
  if (status.status === "COMPLETE") return STAGE_KEYS.length;
  if (status.arguments.length === 0) return 0;
  const hasJudicial = status.arguments.some((a) => a.agent === "JUDICIAL");
  if (hasJudicial) return 5;
  const hasDefense = status.arguments.some((a) => a.agent === "DEFENSE");
  if (hasDefense) return 3;
  const hasProsecution = status.arguments.some((a) => a.agent === "PROSECUTION");
  if (hasProsecution) return 2;
  return 1;
}
