import { useTranslation } from "react-i18next";
import type { ArgumentRecord } from "@/api/types";
import { cn } from "@/lib/cn";

export function DebateRoundCard({ argument }: { argument: ArgumentRecord }) {
  const { t, i18n } = useTranslation();
  const content = i18n.language === "ar" ? argument.content_ar : argument.content_en;
  const fallback = i18n.language === "ar" ? argument.content_en : argument.content_ar;
  return (
    <div
      className={cn(
        "rounded-md border p-3 my-2 bg-white",
        argument.agent === "PROSECUTION" && "border-l-4 border-l-role-prosecution",
        argument.agent === "DEFENSE" && "border-l-4 border-l-role-defense",
        argument.agent === "JUDICIAL" && "border-l-4 border-l-role-judicial",
        argument.agent === "TRAINEE" && "border-l-4 border-l-role-trainee"
      )}
    >
      <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
        <span className="font-medium">
          {t(`case.${argument.agent.toLowerCase()}`, argument.agent)} · {t("coaching.round")}{" "}
          {argument.round_no}
        </span>
        <span className="flex gap-2">
          {argument.llm_used && <span className="text-slate-400">{argument.llm_used}</span>}
          {argument.score_overall != null && (
            <span className="rounded-full bg-slate-100 px-2 py-0.5 font-semibold text-slate-700">
              {argument.score_overall.toFixed(0)}/100
            </span>
          )}
        </span>
      </div>
      <p className="whitespace-pre-wrap text-sm leading-relaxed">{content || fallback}</p>
    </div>
  );
}
