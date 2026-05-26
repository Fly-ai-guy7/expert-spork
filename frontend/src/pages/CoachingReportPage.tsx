import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCoachingReport } from "@/api/hooks";

export function CoachingReportPage() {
  const { sessionId } = useParams();
  const { t, i18n } = useTranslation();
  const { data, isLoading } = useCoachingReport(sessionId);
  if (isLoading || !data) return <p>{t("actions.loading")}</p>;
  const report = data.coaching_report as Record<string, unknown> as {
    grade?: string;
    total_score?: number;
    per_round?: Array<{ round_no: number; overall: number; rationale_en: string | null; rationale_ar: string | null }>;
    missed_citations?: string[];
    evidence_gaps_to_address?: string[];
    weak_patterns?: string[];
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-brand">{t("coaching.title")}</h1>

      <div className="bg-white border rounded-lg p-6 flex items-center gap-6">
        <div className="text-5xl font-bold text-brand">{report.grade || "—"}</div>
        <div>
          <div className="text-sm text-slate-500">{t("coaching.total")}</div>
          <div className="text-2xl font-semibold">
            {report.total_score != null ? Math.round(report.total_score) : 0}/100
          </div>
        </div>
      </div>

      <section className="bg-white border rounded-lg p-6">
        <h2 className="text-sm font-semibold mb-3">{t("coaching.per_round")}</h2>
        <ul className="space-y-3 text-sm">
          {(report.per_round || []).map((r) => (
            <li key={r.round_no} className="border-l-4 border-brand pl-3">
              <div className="font-medium">Round {r.round_no} · {Math.round(r.overall)}/100</div>
              <div className="text-xs text-slate-500 mt-1">
                {(i18n.language === "ar" ? r.rationale_ar : r.rationale_en) || r.rationale_en}
              </div>
            </li>
          ))}
        </ul>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ListBlock title={t("coaching.missed_citations")} items={report.missed_citations || []} />
        <ListBlock title={t("coaching.evidence_gaps")} items={report.evidence_gaps_to_address || []} />
        <ListBlock title={t("coaching.weak_patterns")} items={report.weak_patterns || []} />
      </div>
    </div>
  );
}

function ListBlock({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <h3 className="text-sm font-semibold mb-2">{title}</h3>
      {items.length === 0 ? (
        <p className="text-xs text-slate-500">—</p>
      ) : (
        <ul className="list-disc ml-5 text-sm space-y-1">
          {items.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
