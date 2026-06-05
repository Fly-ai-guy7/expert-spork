import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useCounsel, useSubmitTrainee } from "@/api/hooks";
import type { CounselAdvice } from "@/api/types";

export function TraineeSeatDialog({
  checkpointId,
  onSubmitted,
}: {
  checkpointId: string;
  onSubmitted: () => void;
}) {
  const { t, i18n } = useTranslation();
  const [content, setContent] = useState("");
  const [citations, setCitations] = useState("");
  const [advice, setAdvice] = useState<CounselAdvice | null>(null);
  const submit = useSubmitTrainee();
  const counsel = useCounsel();

  const parseCitations = () =>
    citations
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean);

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        <h2 className="text-lg font-semibold text-brand mb-2">{t("case.your_turn")}</h2>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={t("case.argument_placeholder")}
          rows={10}
          className="w-full rounded-md border p-2 text-sm font-mono"
        />
        <input
          type="text"
          value={citations}
          onChange={(e) => setCitations(e.target.value)}
          placeholder="Citations (comma-separated, e.g. 82/2002:113, 131/1948:163)"
          className="mt-2 w-full rounded-md border p-2 text-sm"
        />

        {advice && (
          <section className="mt-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm">
            <h3 className="font-semibold text-amber-900 mb-1">{t("counsel.title")}</h3>
            <p className="mb-2">
              {(i18n.language === "ar" ? advice.strategy_ar : advice.strategy_en) ||
                advice.strategy_en ||
                advice.strategy_ar}
            </p>
            <AdviceList label={t("counsel.suggested_citations")} items={advice.suggested_citations} />
            <AdviceList label={t("counsel.strengths")} items={advice.strengths} />
            <AdviceList label={t("counsel.risks")} items={advice.risks} />
            <AdviceList label={t("counsel.missing")} items={advice.missing_arguments} />
          </section>
        )}

        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <button
            type="button"
            disabled={counsel.isPending}
            onClick={async () => {
              const res = await counsel.mutateAsync({
                checkpoint_id: checkpointId,
                content_en: content,
                citations: parseCitations(),
              });
              setAdvice(res.advice);
            }}
            className="rounded-md border border-amber-500 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-50 disabled:opacity-50"
          >
            {counsel.isPending ? t("actions.loading") : t("counsel.get_advice")}
          </button>
          <button
            disabled={submit.isPending || !content.trim()}
            onClick={async () => {
              await submit.mutateAsync({
                checkpoint_id: checkpointId,
                content_en: content,
                citations: parseCitations(),
              });
              onSubmitted();
            }}
            className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            {submit.isPending ? t("actions.loading") : t("case.submit_argument")}
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
