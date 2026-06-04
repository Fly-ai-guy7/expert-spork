import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useGenerateCase, useRunTraining, useTrainingSessions } from "@/api/hooks";

const AREAS = ["IP", "LABOUR", "COMMERCIAL", "CONSUMER", "PRIVACY", "CORPORATE", "CIVIL"];

export function TrainingDashboardPage() {
  const { t, i18n } = useTranslation();
  const [area, setArea] = useState("IP");
  const [difficulty, setDifficulty] = useState(2);
  const [role, setRole] = useState<"DEFENSE" | "PROSECUTION">("DEFENSE");
  const generate = useGenerateCase();
  const runTraining = useRunTraining();
  const sessions = useTrainingSessions();
  const navigate = useNavigate();

  async function start() {
    const c = await generate.mutateAsync({
      area_of_law: area,
      difficulty,
      language: i18n.language === "ar" ? "ar" : "en",
    });
    await runTraining.mutateAsync({
      case_id: c.id,
      trainee_role: role,
      user_id: "trainee",
      difficulty,
    });
    navigate(`/cases/${c.id}`);
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl md:text-4xl font-bold text-slate-900">
        {t("training.dashboard_title")}
      </h1>

      <section className="bg-white rounded-lg border p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-medium">{t("training.area")}</label>
            <select
              value={area}
              onChange={(e) => setArea(e.target.value)}
              className="mt-1 block w-full rounded-md border px-2 py-1.5 text-sm"
            >
              {AREAS.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">{t("training.difficulty")}</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border px-2 py-1.5 text-sm"
            >
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">{t("training.your_role")}</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as "DEFENSE" | "PROSECUTION")}
              className="mt-1 block w-full rounded-md border px-2 py-1.5 text-sm"
            >
              <option value="DEFENSE">{t("training.defense")}</option>
              <option value="PROSECUTION">{t("training.prosecution")}</option>
            </select>
          </div>
        </div>
        <div className="mt-6 pt-6 border-t flex justify-end">
          <button
            onClick={start}
            disabled={generate.isPending || runTraining.isPending}
            className="w-full md:w-auto rounded-md bg-brand px-6 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
          >
            {generate.isPending || runTraining.isPending
              ? t("actions.loading")
              : t("training.start_case")}
          </button>
        </div>
      </section>

      <section>
        <h2 className="text-lg font-medium mb-3">{t("training.recent_sessions")}</h2>
        {sessions.data && sessions.data.length > 0 ? (
          <ul className="bg-white rounded-lg border divide-y">
            {sessions.data.map((s) => (
              <li
                key={s.training_session_id}
                className="flex items-center justify-between px-4 py-3 text-sm"
              >
                <div>
                  <div className="font-medium">{s.trainee_role}</div>
                  <div className="text-xs text-slate-500">
                    {t("training.difficulty")} {s.difficulty} · {t("training.case_label")}{" "}
                    {s.case_id.slice(0, 8)}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {s.total_score != null && (
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold">
                      {Math.round(s.total_score)}/100
                    </span>
                  )}
                  <a
                    href={`/cases/${s.case_id}`}
                    className="text-brand hover:underline text-xs font-medium"
                  >
                    {t("training.open")}
                  </a>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="bg-white rounded-lg border px-6 py-8 text-center">
            <p className="text-sm font-medium text-slate-700">{t("training.no_sessions")}</p>
            <p className="mt-1 text-xs text-slate-500">{t("training.no_sessions_hint")}</p>
          </div>
        )}
      </section>
    </div>
  );
}
