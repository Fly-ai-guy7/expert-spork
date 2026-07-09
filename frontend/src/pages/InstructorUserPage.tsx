import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useInstructorOverview, useTrainingSessions } from "@/api/hooks";
import type { TrainingSessionSummary } from "@/api/types";

export function InstructorUserPage() {
  const { userId = "" } = useParams();
  const { t } = useTranslation();
  const { data: overview } = useInstructorOverview(userId);
  const { data: sessions } = useTrainingSessions(userId);

  if (!overview || !sessions) return <p>{t("actions.loading")}</p>;

  const summary = overview.per_user[0];
  const sorted = [...sessions].sort((a, b) => {
    const at = a.completed_at ? Date.parse(a.completed_at) : 0;
    const bt = b.completed_at ? Date.parse(b.completed_at) : 0;
    return bt - at;
  });

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between gap-4">
        <div>
          <div className="text-xs text-slate-500">
            <Link to="/instructor" className="underline">
              {t("instructor.title")}
            </Link>{" "}
            /
          </div>
          <h1 className="text-2xl font-semibold text-brand font-mono">{userId}</h1>
        </div>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label={t("instructor.stat_sessions")} value={summary?.sessions ?? sessions.length} />
        <Stat
          label={t("instructor.stat_avg")}
          value={summary ? `${Math.round(summary.avg_score)}/100` : "—"}
        />
        <Stat label={t("instructor.stat_latest")} value={summary?.latest_grade ?? "—"} />
        <Stat
          label={t("instructor.stat_council_lost")}
          value={_lostRateForUser(sessions)}
        />
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-2">{t("instructor.trajectory")}</h2>
        <GradeTrend sessions={sorted} />
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-2">{t("instructor.sessions_table")}</h2>
        {sorted.length === 0 ? (
          <p className="text-xs text-slate-500">—</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-slate-600">
              <tr>
                <th className="py-1">{t("instructor.col_completed")}</th>
                <th>{t("instructor.col_role")}</th>
                <th>{t("instructor.col_grade")}</th>
                <th>{t("instructor.col_score")}</th>
                <th>{t("instructor.col_council")}</th>
                <th>{t("instructor.col_counsel")}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {sorted.map((s) => (
                <tr key={s.id} className="border-t">
                  <td className="py-1 whitespace-nowrap">
                    {s.completed_at
                      ? new Date(s.completed_at).toLocaleDateString()
                      : "—"}
                  </td>
                  <td>{s.trainee_role}</td>
                  <td className="font-semibold">{s.grade ?? "—"}</td>
                  <td>{s.total_score != null ? Math.round(s.total_score) : "—"}</td>
                  <td>{s.council_alignment ?? "—"}</td>
                  <td>{s.counsel_calls_count}</td>
                  <td>
                    <Link
                      to={`/training/${s.id}`}
                      className="text-brand underline"
                    >
                      {t("instructor.open")}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

function _lostRateForUser(sessions: TrainingSessionSummary[]): string {
  const withAlignment = sessions.filter((s) => s.council_alignment);
  if (withAlignment.length === 0) return "—";
  const lost = withAlignment.filter((s) => s.council_alignment === "LOST").length;
  return `${Math.round((lost / withAlignment.length) * 100)}%`;
}

function GradeTrend({ sessions }: { sessions: TrainingSessionSummary[] }) {
  if (sessions.length === 0) return <p className="text-xs text-slate-500">—</p>;
  const chron = [...sessions].reverse();
  const gradeColor: Record<string, string> = {
    A: "bg-emerald-500 text-white",
    B: "bg-emerald-300 text-emerald-900",
    C: "bg-amber-300 text-amber-900",
    D: "bg-rose-300 text-rose-900",
    F: "bg-rose-500 text-white",
  };
  return (
    <div className="flex flex-wrap gap-1">
      {chron.map((s) => {
        const g = s.grade ?? "—";
        return (
          <span
            key={s.id}
            title={
              (s.completed_at ? new Date(s.completed_at).toLocaleString() : "") +
              (s.council_alignment ? ` · council ${s.council_alignment}` : "")
            }
            className={
              "inline-flex items-center justify-center w-7 h-7 rounded text-xs font-bold " +
              (gradeColor[g] || "bg-slate-200 text-slate-700")
            }
          >
            {g}
          </span>
        );
      })}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white border rounded-lg p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
    </div>
  );
}
