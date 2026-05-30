import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

export interface CaseEvent {
  status?: string;
  stage?: string;
  side?: string;
  round_no?: number;
  checkpoint_id?: string;
  reason?: string;
  ts?: number;
  [k: string]: unknown;
}

const TERMINAL = new Set(["complete", "failed", "paused"]);

/**
 * Subscribes to GET /api/v1/cases/{id}/events via SSE.
 *
 * On every event we invalidate the `case-status` query so the rest of the
 * page re-renders against the latest backend state — the SSE stream is the
 * trigger, the existing REST GET is the source of truth. This keeps the
 * payload tiny (just a status hint) and lets the UI keep using the
 * structured CaseStatusPayload it already knows.
 *
 * Falls back gracefully: if EventSource isn't available (older browsers,
 * test envs) the hook is a no-op and the caller's existing polling keeps
 * working.
 */
export function useCaseEvents(caseId: string | undefined): CaseEvent | null {
  const qc = useQueryClient();
  const [last, setLast] = useState<CaseEvent | null>(null);

  useEffect(() => {
    if (!caseId || typeof window === "undefined" || typeof EventSource === "undefined") {
      return;
    }
    // SSE doesn't carry Authorization headers from a regular EventSource,
    // so the deploy stack must accept cookie auth at the edge OR move the
    // token into a query param for /events. We keep the relative URL so
    // Caddy can decide.
    const url = `/api/v1/cases/${caseId}/events`;
    const es = new EventSource(url, { withCredentials: true });

    es.onmessage = (ev) => {
      try {
        const evt = JSON.parse(ev.data) as CaseEvent;
        setLast(evt);
        // Re-fetch the canonical status snapshot whenever the pipeline
        // moves; the SSE payload itself is just a nudge.
        qc.invalidateQueries({ queryKey: ["case-status", caseId] });
        qc.invalidateQueries({ queryKey: ["case", caseId] });
        if (evt.status && TERMINAL.has(evt.status)) {
          es.close();
        }
      } catch {
        /* ignore malformed event */
      }
    };
    es.onerror = () => {
      // Let EventSource auto-reconnect for transient errors; close on
      // terminal disconnect.
      if (es.readyState === EventSource.CLOSED) es.close();
    };

    return () => es.close();
  }, [caseId, qc]);

  return last;
}
