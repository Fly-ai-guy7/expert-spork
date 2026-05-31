import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useDashboard } from "@/api/hooks";
import type { ActivityEvent, RiskCell } from "@/api/types";
import { cn } from "@/lib/cn";

function title(lang: string, en: string | null, ar: string | null): string {
  return (lang === "ar" ? ar : en) || en || ar || "(untitled)";
}

/** Risk 0–100 → tailwind background. Higher risk is redder. */
function riskClass(risk: number): string {
  if (risk >= 80) return "bg-red-600 text-white";
  if (risk >= 60) return "bg-orange-500 text-white";
  if (risk >= 40) return "bg-amber-400 text-slate-900";
  if (risk >= 20) return "bg-lime-300 text-slate-900";
  return "bg-emerald-200 text-slate-900";
}

const ACTIVITY_ICON: Record<ActivityEvent["type"], string> = {
  case_created: "📁",
  ruling_issued: "⚖️",
  training_completed: "🎓",
  checkpoint_responded: "✅",
};

function StatCard({ label, value, tone }: { label: string; value: number; tone?: "alert" }) {
  return (
    <div className="bg-white rounded-lg border p-4">
      <div className={cn("text-3xl font-semibold", tone === "alert" && value > 0 ? "text-red-600" : "text-brand")}>
        {value}
      </div>
      <div className="text-xs text-slate-500 mt-1">{label}</div>
    </div>
  );
}

export function DashboardPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { data, isLoading } = useDashboard();

  if (isLoading) return <p>{t("actions.loading")}</p>;
  if (!data) return <p>{t("dashboard.empty")}</p>;

  const { open_issues, overdue, risk_heatmap, recent_activity } = data;
  const cellByKey = new Map<string, RiskCell>();
  for (const c of risk_heatmap.cells) cellByKey.set(`${c.area_of_law}|${c.difficulty}`, c);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-brand">{t("dashboard.title")}</h1>

      {/* open issue counts */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label={t("dashboard.open_cases")} value={open_issues.open_total} />
        <StatCard label={t("dashboard.pending_checkpoints")} value={open_issues.pending_checkpoints} />
        <StatCard label={t("dashboard.awaiting_trainee")} value={open_issues.awaiting_trainee} />
        <StatCard label={t("dashboard.overdue")} value={overdue.count} tone="alert" />
      </section>

      {/* risk heatmap */}
      <section className="bg-white rounded-lg border p-4">
        <h2 className="text-lg font-medium mb-3">{t("dashboard.risk_heatmap")}</h2>
        {risk_heatmap.areas.length === 0 ? (
          <p className="text-sm text-slate-500">{t("dashboard.no_risk")}</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="text-sm border-separate border-spacing-1">
              <thead>
                <tr>
                  <th className="text-start text-xs text-slate-500 font-normal px-2">
                    {t("dashboard.area")}
                  </th>
                  {risk_heatmap.difficulties.map((d) => (
                    <th key={d} className="text-xs text-slate-500 font-normal px-2">
                      {t("dashboard.difficulty_short")} {d}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {risk_heatmap.areas.map((area) => (
                  <tr key={area}>
                    <td className="text-xs font-medium px-2 whitespace-nowrap">{area}</td>
                    {risk_heatmap.difficulties.map((d) => {
                      const cell = cellByKey.get(`${area}|${d}`);
                      return (
                        <td key={d} className="p-0">
                          {cell ? (
                            <div
                              className={cn(
                                "rounded-md w-16 h-12 flex flex-col items-center justify-center",
                                riskClass(cell.avg_risk)
                              )}
                              title={`${t("dashboard.avg_risk")}: ${cell.avg_risk} · n=${cell.count}`}
                            >
                              <span className="font-semibold leading-none">{cell.avg_risk}</span>
                              <span className="text-[10px] opacity-80 leading-none mt-0.5">n={cell.count}</span>
                            </div>
                          ) : (
                            <div className="w-16 h-12 rounded-md bg-slate-50 border border-dashed border-slate-200" />
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <div className="grid md:grid-cols-2 gap-6">
        {/* overdue items */}
        <section className="bg-white rounded-lg border">
          <h2 className="text-lg font-medium px-4 py-3 border-b">
            {t("dashboard.overdue_items")}
            <span className="ms-2 text-xs text-slate-500">
              ({t("dashboard.over_hours", { hours: overdue.threshold_hours })})
            </span>
          </h2>
          <div className="divide-y">
            {overdue.items.map((it) => (
              <Link
                key={it.checkpoint_id}
                to={`/cases/${it.case_id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-50 text-sm"
              >
                <div>
                  <div className="font-medium">{title(lang, it.title_en, it.title_ar)}</div>
                  <div className="text-xs text-slate-500 mt-0.5">{it.stage}</div>
                </div>
                <span className="text-xs font-medium text-red-600 whitespace-nowrap">
                  {Math.round(it.age_hours)}h
                </span>
              </Link>
            ))}
            {overdue.items.length === 0 && (
              <div className="px-4 py-6 text-center text-slate-500 text-sm">
                {t("dashboard.no_overdue")}
              </div>
            )}
          </div>
        </section>

        {/* recent activity */}
        <section className="bg-white rounded-lg border">
          <h2 className="text-lg font-medium px-4 py-3 border-b">{t("dashboard.recent_activity")}</h2>
          <div className="divide-y">
            {recent_activity.map((e, i) => (
              <Link
                key={`${e.case_id}-${e.type}-${i}`}
                to={`/cases/${e.case_id}`}
                className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 text-sm"
              >
                <span aria-hidden>{ACTIVITY_ICON[e.type]}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{title(lang, e.title_en, e.title_ar)}</div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {t(`dashboard.activity.${e.type}`)} · {e.detail}
                  </div>
                </div>
                <span className="text-xs text-slate-400 whitespace-nowrap">
                  {new Date(e.at).toLocaleDateString(lang)}
                </span>
              </Link>
            ))}
            {recent_activity.length === 0 && (
              <div className="px-4 py-6 text-center text-slate-500 text-sm">
                {t("dashboard.no_activity")}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
