import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";

import { useCaseEvents } from "@/api/useCaseEvents";

interface FakeEvent {
  data: string;
}

class FakeEventSource {
  static instances: FakeEventSource[] = [];
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;

  url: string;
  withCredentials: boolean;
  readyState = FakeEventSource.OPEN;
  onmessage: ((ev: FakeEvent) => void) | null = null;
  onerror: ((ev: unknown) => void) | null = null;
  closed = false;

  constructor(url: string, init?: { withCredentials?: boolean }) {
    this.url = url;
    this.withCredentials = init?.withCredentials ?? false;
    FakeEventSource.instances.push(this);
  }
  close(): void {
    this.closed = true;
    this.readyState = FakeEventSource.CLOSED;
  }
  emit(payload: object): void {
    this.onmessage?.({ data: JSON.stringify(payload) });
  }
}

function wrapper({ children }: { children: React.ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe("useCaseEvents", () => {
  beforeEach(() => {
    FakeEventSource.instances = [];
    vi.stubGlobal("EventSource", FakeEventSource);
  });
  afterEach(() => vi.unstubAllGlobals());

  it("opens the case-scoped SSE URL", () => {
    renderHook(() => useCaseEvents("abc-123"), { wrapper });
    expect(FakeEventSource.instances).toHaveLength(1);
    expect(FakeEventSource.instances[0].url).toBe("/api/v1/cases/abc-123/events");
  });

  it("yields the last parsed event and closes on a terminal status", () => {
    const { result } = renderHook(() => useCaseEvents("c1"), { wrapper });
    const es = FakeEventSource.instances[0];

    act(() => es.emit({ status: "running", stage: "evidence" }));
    expect(result.current?.status).toBe("running");

    act(() => es.emit({ status: "complete" }));
    expect(result.current?.status).toBe("complete");
    expect(es.closed).toBe(true);
  });

  it("is a no-op when no caseId is provided", () => {
    renderHook(() => useCaseEvents(undefined), { wrapper });
    expect(FakeEventSource.instances).toHaveLength(0);
  });

  it("cleans up the EventSource on unmount", () => {
    const { unmount } = renderHook(() => useCaseEvents("c2"), { wrapper });
    const es = FakeEventSource.instances[0];
    unmount();
    expect(es.closed).toBe(true);
  });

  it("survives malformed payloads", () => {
    const { result } = renderHook(() => useCaseEvents("c3"), { wrapper });
    const es = FakeEventSource.instances[0];
    act(() => es.onmessage?.({ data: "not-json" }));
    expect(result.current).toBeNull();
  });
});
