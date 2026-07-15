import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useCase, useCaseReport, useCaseStatus, useRunCase } from "@/api/hooks";
import { api } from "@/api/client";
import type { RulingPayload } from "@/api/types";
import { PipelineTimeline } from "@/components/PipelineTimeline";
import { DebateRoundCard } from "@/components/DebateRoundCard";
import { PrepCounselDialog } from "@/components/PrepCounselDialog";
import { TraineeSeatDialog } from "@/components/TraineeSeatDialog";

export function CaseDetailPage() {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { data: caseData } = useCase(id);
  const { data: status, refetch } = useCaseStatus(id);
  const { data: report } = useCaseReport(id);
  const runCase = useRunCase();
  const [prepOpen, setPrepOpen] = useState(false);

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

      {caseData.status !== "COMPLETE" && !traineeTurn && (
        <div className="flex gap-2">
          <button
            type="button"
            className="rounded-md border border-amber-500 px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-50"
            onClick={() => setPrepOpen(true)}
          >
            {t("counsel.prep_button")}
          </button>
        </div>
      )}

      {prepOpen && (
        <PrepCounselDialog caseId={id} onClose={() => setPrepOpen(false)} />
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

      {report?.ruling && <CouncilRulingSection ruling={report.ruling} />}

      {status?.status === "COMPLETE" && (
        <div className="flex gap-2 flex-wrap">
          <a
            href={`${api.defaults.baseURL}/api/cases/${id}/report.pdf`}
            className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white"
          >
            {t("case.download_pdf")}
          </a>
          {status.training_session_id && (
            <Link
              to={`/training/${status.training_session_id}`}
              className="rounded-md border border-brand px-4 py-2 text-sm font-medium text-brand hover:bg-brand/5"
            >
              {t("case.view_coaching")}
            </Link>
          )}
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

function CouncilRulingSection({ ruling }: { ruling: RulingPayload }) {
  const { t, i18n } = useTranslation();
  const isAr = i18n.language === "ar";
  const text = (isAr ? ruling.text_ar : ruling.text_en) || ruling.text_en || ruling.text_ar;
  const dissent = (isAr ? ruling.dissent_ar : ruling.dissent_en) || ruling.dissent_en;
  const vote = ruling.council_vote;

  return (
    <section className="rounded-md border border-slate-300 p-4">
      <h2 className="text-sm font-semibold mb-2">{t("case.judicial")}</h2>
      <div className="text-xs text-slate-600 mb-2">
        {t("case.plaintiff_prob")}: {Math.round(ruling.plaintiff_success_prob ?? 0)}%
        {ruling.override_applied && <> · {t("case.override")}</>}
        {ruling.council_size && ruling.council_size > 1 && vote && (
          <>
            {" "}
            · {t("council.panel_of", { n: ruling.council_size })} — {vote.for_plaintiff}–
            {vote.for_defendant} {t("council.vote_summary")}
          </>
        )}
      </div>
      {text && <p className="text-sm mb-3">{text}</p>}

      {ruling.council_verdicts?.length > 0 && (
        <div className="mt-3">
          <h3 className="text-xs font-semibold mb-1">{t("council.member_verdicts")}</h3>
          <ul className="text-xs space-y-1">
            {ruling.council_verdicts.map((v, i) => (
              <li key={i}>
                <span className="font-mono">{v.member_llm}</span> —{" "}
                {v.verdict === "FOR_PLAINTIFF" ? t("council.for_plaintiff") : t("council.for_defendant")} (
                {Math.round(v.plaintiff_success_prob)}%)
                {v.override_flagged && <> · {t("council.override_flagged")}</>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {dissent && (
        <div className="mt-3">
          <h3 className="text-xs font-semibold mb-1">{t("council.dissent")}</h3>
          <p className="text-xs text-slate-600">{dissent}</p>
        </div>
      )}
    </section>
  );
}
