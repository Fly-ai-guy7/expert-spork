import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCases } from "@/api/hooks";

export function CaseListPage() {
  const { i18n } = useTranslation();
  const { data, isLoading } = useCases();
  if (isLoading) return <p>Loading…</p>;
  return (
    <div>
      <h1 className="text-2xl font-semibold text-brand mb-4">Cases</h1>
      <div className="bg-white rounded-lg border divide-y">
        {(data || []).map((c) => (
          <Link
            key={c.id}
            to={`/cases/${c.id}`}
            className="block px-4 py-3 hover:bg-slate-50 text-sm"
          >
            <div className="font-medium">
              {(i18n.language === "ar" ? c.title_ar : c.title_en) || c.title_en || c.title_ar || "(untitled)"}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {c.status} · {c.source} · {c.area_of_law || "—"}
              {c.difficulty != null ? ` · diff ${c.difficulty}` : ""}
            </div>
          </Link>
        ))}
        {(!data || data.length === 0) && (
          <div className="px-4 py-6 text-center text-slate-500 text-sm">No cases yet.</div>
        )}
      </div>
    </div>
  );
}
