import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";

import { api } from "@/api/client";
import { useStatutes } from "@/api/hooks";

export function StatutesPage() {
  const { t, i18n } = useTranslation();
  const [q, setQ] = useState("");
  const { data: statutes } = useStatutes();
  const search = useQuery({
    queryKey: ["statute-search", q],
    queryFn: async () =>
      (await api.get(`/api/statutes/search`, { params: { q } })).data as Array<{
        id: string;
        short_code: string;
        article_number: string;
        text_en: string | null;
        text_ar: string | null;
        title_en: string | null;
        title_ar: string | null;
      }>,
    enabled: q.length >= 2,
  });

  return (
    <div>
      <h1 className="text-2xl font-semibold text-brand mb-4">{t("statutes.title")}</h1>

      <input
        type="text"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder={t("statutes.search")}
        className="block w-full rounded-md border px-3 py-2 text-sm mb-4"
      />

      {q.length >= 2 ? (
        <div className="space-y-3">
          {(search.data || []).map((row) => (
            <div key={row.id} className="bg-white rounded-md border p-3 text-sm">
              <div className="text-xs text-slate-500">
                {row.short_code} art. {row.article_number} ·{" "}
                {(i18n.language === "ar" ? row.title_ar : row.title_en) || row.title_en}
              </div>
              <p className="mt-1 whitespace-pre-wrap">
                {(i18n.language === "ar" ? row.text_ar : row.text_en) || row.text_en || row.text_ar}
              </p>
            </div>
          ))}
          {search.data?.length === 0 && (
            <p className="text-sm text-slate-500">{t("statutes.no_results")}</p>
          )}
        </div>
      ) : (
        <ul className="bg-white rounded-md border divide-y">
          {(statutes || []).map((s: any) => (
            <li key={s.id} className="px-4 py-3 text-sm">
              <span className="font-medium">{s.short_code}</span> —{" "}
              {(i18n.language === "ar" ? s.title_ar : s.title_en) || s.title_en || s.title_ar}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
