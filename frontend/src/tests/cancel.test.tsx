import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import React from "react";

import { CaseDetailPage } from "@/pages/CaseDetailPage";
import { api } from "@/api/client";

function wrap(children: React.ReactNode) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return (
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/cases/abc"]}>
        <Routes>
          <Route path="/cases/:id" element={children} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}

const runningCase = {
  id: "abc", title_en: "Running case", title_ar: null,
  status: "RUNNING", source: "AI_GENERATED", difficulty: 2,
  area_of_law: "IP", created_at: new Date().toISOString(),
  summary_en: null, summary_ar: null, language_primary: "en",
  parties: [], facts: [], evidence: [], cancel_requested: false,
};

beforeEach(() => {
  vi.spyOn(api, "get").mockImplementation(async (url: string) => {
    if (url.startsWith("/api/cases/abc/status")) {
      return { data: { case_id: "abc", status: "RUNNING", rounds_complete: 0,
                       rounds_total: 0, arguments: [], pending_checkpoint_id: null,
                       pending_checkpoint_stage: null } } as never;
    }
    return { data: runningCase } as never;
  });
  vi.stubGlobal("confirm", () => true);
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("Cancel button on CaseDetailPage", () => {
  it("appears for a RUNNING case and POSTs to the cancel endpoint when confirmed", async () => {
    const post = vi.spyOn(api, "post").mockResolvedValue({
      data: { case_id: "abc", status: "RUNNING", cancel_requested: true },
    } as never);

    render(wrap(<CaseDetailPage />));

    const btn = await screen.findByTestId("cancel-case");
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);

    await waitFor(() => {
      expect(post).toHaveBeenCalledWith("/api/v1/cases/abc/cancel", {});
    });
  });

  it("does not POST when the confirmation is denied", async () => {
    const post = vi.spyOn(api, "post").mockResolvedValue({ data: {} } as never);
    vi.stubGlobal("confirm", () => false);

    render(wrap(<CaseDetailPage />));
    fireEvent.click(await screen.findByTestId("cancel-case"));

    await new Promise((r) => setTimeout(r, 0));
    expect(post).not.toHaveBeenCalled();
  });

  it("is absent for a DRAFT case (the Run button shows instead)", async () => {
    vi.spyOn(api, "get").mockImplementation(async (url: string) => {
      if (url.startsWith("/api/cases/abc/status")) {
        return { data: { case_id: "abc", status: "DRAFT", rounds_complete: 0,
                         rounds_total: 0, arguments: [], pending_checkpoint_id: null,
                         pending_checkpoint_stage: null } } as never;
      }
      return { data: { ...runningCase, status: "DRAFT" } } as never;
    });

    render(wrap(<CaseDetailPage />));
    await screen.findByText(/Running case/);
    expect(screen.queryByTestId("cancel-case")).not.toBeInTheDocument();
  });
});
