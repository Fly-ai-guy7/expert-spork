import { useState } from "react";
import { useTranslation } from "react-i18next";

import { useSubmitTrainee } from "@/api/hooks";

export function TraineeSeatDialog({
  checkpointId,
  onSubmitted,
}: {
  checkpointId: string;
  onSubmitted: () => void;
}) {
  const { t } = useTranslation();
  const [content, setContent] = useState("");
  const [citations, setCitations] = useState("");
  const submit = useSubmitTrainee();

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="trainee-seat-title"
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-6"
      >
        <h2 id="trainee-seat-title" className="text-lg font-semibold text-brand mb-2">
          {t("case.your_turn")}
        </h2>
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
          placeholder={t("case.citations_placeholder")}
          className="mt-2 w-full rounded-md border p-2 text-sm"
        />
        <div className="mt-4 flex justify-end gap-2">
          <button
            disabled={submit.isPending || !content.trim()}
            onClick={async () => {
              await submit.mutateAsync({
                checkpoint_id: checkpointId,
                content_en: content,
                citations: citations
                  .split(",")
                  .map((c) => c.trim())
                  .filter(Boolean),
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
