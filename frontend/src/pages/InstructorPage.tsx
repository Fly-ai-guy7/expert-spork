import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useInstructorOverview } from "@/api/hooks";

export function InstructorPage() {
  const { t } = useTranslation();
  const [userFilter, setUserFilter] = useState("");
  const { data, isLoading } = useInstructorOverview(userFilter || undefined);

  if (isLoading || !data) return <p>{t("actions.loading")}</p>;

  const grades = ["A", "B", "C", "D", "F"];

  return (
    <div className="space-y-6">
      <header className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-brand">{t("instructor.title")}</h1>
          <p className="text-xs text-slate-500 mt-1">{t("instructor.subtitle")}</p>
        </div>
        <input
          type="text"
          value={userFilter}
          onChange={(e) => setUserFilter(e.target.value)}
          placeholder={t("instructor.filter_user") || ""}
          className="rounded-md border px-3 py-2 text-sm"
        />
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Stat label={t("instructor.stat_sessions")} value={data.total_sessions} />
        <Stat label={t("instructor.stat_completed")} value={data.completed_sessions} />
        <Stat
          label={t("instructor.stat_avg")}
          value={`${Math.round(data.avg_score)}/100`}
        />
        <Stat
          label={t("instructor.stat_council_lost")}
          value={
            data.council_lost_rate == null
              ? "—"
              : `${Math.round(data.council_lost_rate * 100)}%`
          }
        />
      </section>

      <section className="bg-white border rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-2">{t("instructor.grade_dist")}</h2>
        <div className="flex gap-2 flex-wrap">
          {grades.map((g) => (
            <span
              key={g}
              className="rounded-md border px-3 py-1 text-sm bg-slate-50"
            >
              <span className="font-semibold">{g}</span> · {data.grade_distribution[g] || 0}
            </span>
          ))}
        </div>
      </section>

      {data.needs_attention.length > 0 && (
        <section className="bg-rose-50 border border-rose-200 rounded-lg p-4">
          <h2 className="text-sm font-semibold mb-2">{t("instructor.needs_attention")}</h2>
          <table className="w-full text-sm">
            <thead className="text-left text-xs text-slate-600">
              <tr>
                <th className="py-1">{t("instructor.col_user")}</th>
                <th>{t("instructor.col_role")}</th>
                <th>{t("instructor.col_grade")}</th>
                <th>{t("instructor.col_council")}</th>
                <th>{t("instructor.col_counsel")}</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {data.needs_attention.map((r) => (
                <tr key={r.session_id} className="border-t">
                  <td className="py-1 font-mono">{r.user_id}</td>
                  <td>{r.trainee_role}</td>
                  <td className="font-semibold">{r.grade || "—"}</td>
                  <td>{r.council_alignment || "—"}</td>
                  <td>{r.counsel_calls_count}</td>
                  <td>
                    <Link
                      to={`/training/${r.session_id}`}
                      className="text-brand underline"
                    >
                      {t("instructor.open")}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="bg-white border rounded-lg p-4">
          <h2 className="text-sm font-semibold mb-2">{t("instructor.top_users")}</h2>
          {data.per_user.length === 0 ? (
            <p className="text-xs text-slate-500">—</p>
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-slate-600">
                <tr>
                  <th>{t("instructor.col_user")}</th>
                  <th>{t("instructor.col_sessions")}</th>
                  <th>{t("instructor.col_avg")}</th>
                  <th>{t("instructor.col_latest")}</th>
                </tr>
              </thead>
              <tbody>
                {data.per_user.map((u) => (
                  <tr key={u.user_id} className="border-t">
                    <td className="py-1 font-mono">{u.user_id}</td>
                    <td>{u.sessions}</td>
                    <td>{Math.round(u.avg_score)}</td>
                    <td>{u.latest_grade || "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <div className="space-y-4">
          <ListCard
            title={t("instructor.top_missed")}
            items={data.top_missed_citations.map((c) => `${c.citation} (${c.count})`)}
          />
          <ListCard
            title={t("instructor.top_weak")}
            items={data.top_weak_patterns.map((p) => `${p.pattern} (${p.count})`)}
          />
        </div>
      </div>
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

function ListCard({ title, items }: { title: string; items: string[] }) {
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
