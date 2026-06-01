import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCreateCase, useGenerateCase } from "@/api/hooks";

export function NewCasePage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [mode, setMode] = useState<"manual" | "generate">("generate");
  const [title, setTitle] = useState("");
  const [area, setArea] = useState("IP");
  const [difficulty, setDifficulty] = useState(2);

  const create = useCreateCase();
  const generate = useGenerateCase();

  async function handle() {
    if (mode === "generate") {
      const c = await generate.mutateAsync({
        area_of_law: area,
        difficulty,
        language: i18n.language === "ar" ? "ar" : "en",
      });
      navigate(`/cases/${c.id}`);
    } else {
      const c = await create.mutateAsync({
        title_en: i18n.language === "en" ? title : null,
        title_ar: i18n.language === "ar" ? title : null,
        language_primary: i18n.language === "ar" ? "ar" : "en",
        area_of_law: area,
      } as never);
      navigate(`/cases/${c.id}`);
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">{t("new_case.title")}</h1>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setMode("generate")}
          className={`flex-1 rounded-md border px-3 py-2 text-sm ${
            mode === "generate" ? "bg-brand text-white" : "bg-white"
          }`}
        >
          {t("new_case.generate")}
        </button>
        <button
          onClick={() => setMode("manual")}
          className={`flex-1 rounded-md border px-3 py-2 text-sm ${
            mode === "manual" ? "bg-brand text-white" : "bg-white"
          }`}
        >
          {t("new_case.manual")}
        </button>
      </div>

      <div className="bg-white rounded-lg border p-6 space-y-4">
        {mode === "manual" && (
          <div>
            <label className="text-sm font-medium">
              {i18n.language === "ar" ? t("new_case.title_ar_label") : t("new_case.title_label")}
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 block w-full rounded-md border px-3 py-2 text-sm"
            />
          </div>
        )}
        <div>
          <label className="text-sm font-medium">{t("new_case.area")}</label>
          <select
            value={area}
            onChange={(e) => setArea(e.target.value)}
            className="mt-1 block w-full rounded-md border px-3 py-2 text-sm"
          >
            {["IP", "LABOUR", "COMMERCIAL", "CONSUMER", "PRIVACY", "CORPORATE", "CIVIL"].map((a) => (
              <option key={a} value={a}>
                {a}
              </option>
            ))}
          </select>
        </div>
        {mode === "generate" && (
          <div>
            <label className="text-sm font-medium">{t("training.difficulty")}</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border px-3 py-2 text-sm"
            >
              {[1, 2, 3, 4, 5].map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>
        )}
        <button
          onClick={handle}
          disabled={create.isPending || generate.isPending}
          className="w-full rounded-md bg-brand px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {mode === "generate" ? t("new_case.submit_generate") : t("new_case.submit")}
        </button>
      </div>
    </div>
  );
}
