import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useCaseCounsel } from "@/api/hooks";
import type { CounselAdvice } from "@/api/types";

export function PrepCounselDialog({
  caseId,
  defaultRole,
  onClose,
}: {
  caseId: string;
  defaultRole?: "PROSECUTION" | "DEFENSE";
  onClose: () => void;
}) {
  const { t, i18n } = useTranslation();
  const [content, setContent] = useState("");
  const [role, setRole] = useState<"PROSECUTION" | "DEFENSE">(defaultRole ?? "DEFENSE");
  const [advice, setAdvice] = useState<CounselAdvice | null>(null);
  const counsel = useCaseCounsel();
  const isAr = i18n.language === "ar";

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-brand">{t("counsel.prep_title")}</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-slate-500 hover:text-slate-800"
          >
            {t("actions.cancel")}
          </button>
        </div>

        {!defaultRole && (
          <div className="mb-2 flex items-center gap-2 text-sm">
            <span className="text-slate-600">{t("training.your_role")}:</span>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as "PROSECUTION" | "DEFENSE")}
              className="rounded-md border px-2 py-1 text-sm"
            >
              <option value="PROSECUTION">{t("training.prosecution")}</option>
              <option value="DEFENSE">{t("training.defense")}</option>
            </select>
          </div>
        )}

        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={t("counsel.prep_placeholder")}
          rows={6}
          className="w-full rounded-md border p-2 text-sm font-mono"
        />

        {advice && (
          <section className="mt-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm">
            <h3 className="font-semibold text-amber-900 mb-1">{t("counsel.title")}</h3>
            <p className="mb-2">
              {(isAr ? advice.strategy_ar : advice.strategy_en) ||
                advice.strategy_en ||
                advice.strategy_ar}
            </p>
            <AdviceList label={t("counsel.suggested_citations")} items={advice.suggested_citations} />
            <AdviceList label={t("counsel.strengths")} items={advice.strengths} />
            <AdviceList label={t("counsel.risks")} items={advice.risks} />
            <AdviceList label={t("counsel.missing")} items={advice.missing_arguments} />
          </section>
        )}

        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            disabled={counsel.isPending}
            onClick={async () => {
              const res = await counsel.mutateAsync({
                case_id: caseId,
                content_en: content,
                trainee_role: role,
              });
              setAdvice(res.advice);
            }}
            className="rounded-md bg-amber-500 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {counsel.isPending ? t("actions.loading") : t("counsel.get_advice")}
          </button>
        </div>
      </div>
    </div>
  );
}

function AdviceList({ label, items }: { label: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="mt-1">
      <span className="font-medium">{label}: </span>
      <ul className="list-disc ms-5">
        {items.map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    </div>
  );
}
