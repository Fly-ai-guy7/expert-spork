import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCase, useCaseStatus, useRunCase } from "@/api/hooks";
import { useCaseEvents } from "@/api/useCaseEvents";
import { api } from "@/api/client";
import { PipelineTimeline } from "@/components/PipelineTimeline";
import { DebateRoundCard } from "@/components/DebateRoundCard";
import { TraineeSeatDialog } from "@/components/TraineeSeatDialog";

export function CaseDetailPage() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { data: caseData } = useCase(id);
  // SSE drives freshness; the long-interval poll is a safety net if the
  // EventSource connection dies and the browser doesn't reconnect.
  const { data: status, refetch } = useCaseStatus(id, 10_000);
  useCaseEvents(id);
  const runCase = useRunCase();

  if (!caseData || !id) return <p>{t("actions.loading")}</p>;

  const title =
    (i18n.language === "ar" ? caseData.title_ar : caseData.title_en) ||
    caseData.title_en ||
    caseData.title_ar ||
    "(untitled)";

  const traineeTurn =
    status?.pending_checkpoint_id && status.pending_checkpoint_stage === "TRAINEE_TURN";

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-brand">{title}</h1>
        <div className="text-xs text-slate-500 mt-1">
          {caseData.status} · {caseData.source} · {caseData.area_of_law || "—"}
        </div>
      </header>

      <PipelineTimeline status={status} />

      {caseData.status === "DRAFT" && (
        <div className="flex gap-2">
          <button
            className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white"
            onClick={() => runCase.mutate(id)}
          >
            {t("case.run")}
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section>
          <h2 className="text-sm font-semibold mb-2">{t("case.prosecution")}</h2>
          {(status?.arguments || [])
            .filter((a) => a.agent === "PROSECUTION")
            .map((a) => (
              <DebateRoundCard key={a.id} argument={a} />
            ))}
        </section>
        <section>
          <h2 className="text-sm font-semibold mb-2">{t("case.defense")}</h2>
          {(status?.arguments || [])
            .filter((a) => a.agent === "DEFENSE")
            .map((a) => (
              <DebateRoundCard key={a.id} argument={a} />
            ))}
        </section>
      </div>

      {(status?.arguments || []).some((a) => a.agent === "TRAINEE") && (
        <section>
          <h2 className="text-sm font-semibold mb-2">Trainee</h2>
          {(status?.arguments || [])
            .filter((a) => a.agent === "TRAINEE")
            .map((a) => (
              <DebateRoundCard key={a.id} argument={a} />
            ))}
        </section>
      )}

      {(status?.arguments || []).some((a) => a.agent === "JUDICIAL") && (
        <section>
          <h2 className="text-sm font-semibold mb-2">{t("case.judicial")}</h2>
          {(status?.arguments || [])
            .filter((a) => a.agent === "JUDICIAL")
            .map((a) => (
              <DebateRoundCard key={a.id} argument={a} />
            ))}
        </section>
      )}

      {status?.status === "COMPLETE" && (
        <div className="flex gap-2">
          <a
            href={`${api.defaults.baseURL}/api/cases/${id}/report.pdf`}
            className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white"
          >
            {t("case.download_pdf")}
          </a>
        </div>
      )}

      {traineeTurn && (
        <TraineeSeatDialog
          checkpointId={status!.pending_checkpoint_id!}
          onSubmitted={() => refetch()}
        />
      )}
    </div>
  );
}
