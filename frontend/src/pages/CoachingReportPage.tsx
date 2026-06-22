import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { api } from "@/api/client";
import { useCoachingReport, useCounselLog } from "@/api/hooks";
import type { CounselLogEntry } from "@/api/types";

export function CoachingReportPage() {
  const { sessionId } = useParams();
  const { t, i18n } = useTranslation();
  const { data, isLoading } = useCoachingReport(sessionId);
  const { data: counselLog } = useCounselLog(sessionId);
  if (isLoading || !data) return <p>{t("actions.loading")}</p>;
  const report = data.coaching_report as Record<string, unknown> as {
    grade?: string;
    total_score?: number;
    per_round?: Array<{ round_no: number; overall: number; rationale_en: string | null; rationale_ar: string | null }>;
    missed_citations?: string[];
    evidence_gaps_to_address?: string[];
    weak_patterns?: string[];
    counsel_calls_count?: number;
    council_alignment?: "WON" | "LOST";
    council_for_trainee?: number;
    council_against_trainee?: number;
    council_supporters?: string[];
    council_dissenters?: string[];
  };

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-semibold text-brand">{t("coaching.title")}</h1>
        <a
          href={`${api.defaults.baseURL}/api/training/${sessionId}/coaching.pdf`}
          className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white"
        >
          {t("coaching.download_pdf")}
        </a>
      </header>

      <div className="bg-white border rounded-lg p-6 flex items-center gap-6">
        <div className="text-5xl font-bold text-brand">{report.grade || "—"}</div>
        <div className="flex-1">
          <div className="text-sm text-slate-500">{t("coaching.total")}</div>
          <div className="text-2xl font-semibold">
            {report.total_score != null ? Math.round(report.total_score) : 0}/100
          </div>
        </div>
        {report.counsel_calls_count != null && (
          <div className="text-right">
            <div className="text-sm text-slate-500">{t("coaching.counsel_calls")}</div>
            <div className="text-2xl font-semibold">{report.counsel_calls_count}</div>
          </div>
        )}
      </div>

      {report.council_alignment && (
        <section
          className={
            "border rounded-lg p-4 " +
            (report.council_alignment === "WON"
              ? "border-emerald-300 bg-emerald-50"
              : "border-rose-300 bg-rose-50")
          }
        >
          <h2 className="text-sm font-semibold mb-1">{t("coaching.council_title")}</h2>
          <p className="text-sm">
            {t(
              report.council_alignment === "WON"
                ? "coaching.council_won"
                : "coaching.council_lost",
              {
                for: report.council_for_trainee ?? 0,
                against: report.council_against_trainee ?? 0,
              },
            )}
          </p>
          {(report.council_supporters?.length || 0) > 0 && (
            <p className="text-xs mt-1">
              <span className="font-medium">{t("coaching.council_supporters")}:</span>{" "}
              {(report.council_supporters || []).join(", ")}
            </p>
          )}
          {(report.council_dissenters?.length || 0) > 0 && (
            <p className="text-xs mt-1">
              <span className="font-medium">{t("coaching.council_dissenters")}:</span>{" "}
              {(report.council_dissenters || []).join(", ")}
            </p>
          )}
        </section>
      )}

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

      {(counselLog?.length || 0) > 0 && (
        <CounselLogSection entries={counselLog || []} lang={i18n.language} />
      )}
    </div>
  );
}

function CounselLogSection({ entries, lang }: { entries: CounselLogEntry[]; lang: string }) {
  const { t } = useTranslation();
  const isAr = lang === "ar";
  return (
    <section className="bg-white border rounded-lg p-6">
      <h2 className="text-sm font-semibold mb-3">{t("coaching.counsel_log_title")}</h2>
      <ul className="space-y-4 text-sm">
        {entries.map((e) => {
          const draft = (isAr ? e.draft_ar : e.draft_en) || e.draft_en || e.draft_ar;
          const strategy =
            (isAr ? e.advice.strategy_ar : e.advice.strategy_en) ||
            e.advice.strategy_en ||
            e.advice.strategy_ar;
          return (
            <li key={e.id} className="border-l-4 border-amber-400 pl-3">
              <div className="text-xs text-slate-500 mb-1">
                {new Date(e.created_at).toLocaleString()} · {e.trainee_role}
              </div>
              {draft && (
                <details className="text-xs mb-1">
                  <summary className="cursor-pointer">{t("coaching.counsel_draft")}</summary>
                  <p className="font-mono whitespace-pre-wrap mt-1">{draft}</p>
                </details>
              )}
              {strategy && <p className="mb-1">{strategy}</p>}
              <MiniList label={t("counsel.suggested_citations")} items={e.advice.suggested_citations} />
              <MiniList label={t("counsel.missing")} items={e.advice.missing_arguments} />
            </li>
          );
        })}
      </ul>
    </section>
  );
}

function MiniList({ label, items }: { label: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="text-xs mt-1">
      <span className="font-medium">{label}:</span> {items.join(", ")}
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
