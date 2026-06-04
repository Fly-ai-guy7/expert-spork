import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCases } from "@/api/hooks";

export function CaseListPage() {
  const { t, i18n } = useTranslation();
  const { data, isLoading } = useCases();
  if (isLoading) return <p>{t("actions.loading")}</p>;
  return (
    <div>
      <h1 className="text-3xl md:text-4xl font-bold text-slate-900 mb-6">{t("cases.title")}</h1>
      <div className="bg-white rounded-lg border divide-y">
        {(data || []).map((c) => (
          <Link
            key={c.id}
            to={`/cases/${c.id}`}
            className="block px-4 py-3 hover:bg-slate-50 text-sm"
          >
            <div className="font-medium">
              {(i18n.language === "ar" ? c.title_ar : c.title_en) ||
                c.title_en ||
                c.title_ar ||
                t("case.untitled")}
            </div>
            <div className="mt-1 flex flex-wrap gap-1.5 text-xs">
              <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                {c.status}
              </span>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                {c.source}
              </span>
              {c.area_of_law && (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                  {c.area_of_law}
                </span>
              )}
              {c.difficulty != null && (
                <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-700">
                  {t("training.difficulty")} {c.difficulty}
                </span>
              )}
            </div>
          </Link>
        ))}
        {(!data || data.length === 0) && (
          <div className="px-4 py-8 text-center">
            <p className="text-sm font-medium text-slate-700">{t("cases.no_cases")}</p>
            <Link
              to="/cases/new"
              className="mt-2 inline-block text-sm font-medium text-brand hover:underline"
            >
              {t("cases.create_first")}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
