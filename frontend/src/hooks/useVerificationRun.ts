import { useEffect, useReducer, useRef } from "react";
import type { WsEvent, CoverageGap } from "@/api/types";
import { getReport } from "@/api/client";

export interface RunReport {
  final_pct: number;
  iterations: number;
  target_reached: boolean;
}

export interface RunState {
  status: "connecting" | "running" | "done" | "error";
  currentIteration: number;
  currentPhase: string;
  coverageHistory: number[];
  gaps: CoverageGap[];
  logs: string[];
  testUrls: Map<number, string>;
  finalReport: RunReport | null;
  error: string | null;
  _dispatchForTest: (event: WsEvent) => void;
}

type Action =
  | { type: "ws_event"; event: WsEvent }
  | { type: "connected" }
  | { type: "report_polled"; report: RunReport };

function reduce(state: RunState, action: Action): RunState {
  if (action.type === "connected") {
    return state.status === "connecting" ? { ...state, status: "running" } : state;
  }
  if (action.type === "report_polled") {
    return { ...state, status: "done", finalReport: action.report };
  }
  const ev = action.event;
  switch (ev.type) {
    case "iteration":
      return { ...state, status: "running", currentIteration: ev.n, currentPhase: ev.phase };
    case "log":
      return { ...state, logs: [...state.logs, ev.text] };
    case "coverage":
      return { ...state, coverageHistory: [...state.coverageHistory, ev.pct], gaps: ev.gaps };
    case "test_ready": {
      const next = new Map(state.testUrls);
      next.set(ev.iteration, ev.url);
      return { ...state, testUrls: next };
    }
    case "done":
      return {
        ...state,
        status: "done",
        finalReport: {
          final_pct: ev.final_pct,
          iterations: ev.iterations,
          target_reached: ev.target_reached,
        },
      };
    case "error":
      return { ...state, status: "error", error: ev.detail };
    default:
      return state;
  }
}

export function useVerificationRun(runId: string): RunState {
  const dispatchRef = useRef<((event: WsEvent) => void) | null>(null);

  const [state, dispatch] = useReducer(reduce, undefined, () => ({
    status: "connecting",
    currentIteration: 0,
    currentPhase: "",
    coverageHistory: [],
    gaps: [],
    logs: [],
    testUrls: new Map(),
    finalReport: null,
    error: null,
    _dispatchForTest: (event: WsEvent) => {
      if (dispatchRef.current) dispatchRef.current(event);
    },
  } as RunState));

  dispatchRef.current = (event: WsEvent) => dispatch({ type: "ws_event", event });

  useEffect(() => {
    let cancelled = false;
    let pollTimer: ReturnType<typeof setTimeout> | null = null;

    // Try the WebSocket for live updates (best-effort)
    const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`);
    ws.onopen = () => {
      if (!cancelled) dispatch({ type: "connected" });
    };
    ws.onmessage = (e) => {
      if (cancelled) return;
      try {
        const event: WsEvent = JSON.parse(e.data as string);
        dispatch({ type: "ws_event", event });
      } catch {
        /* ignore */
      }
    };

    // ALWAYS poll the HTTP report endpoint as the source of truth.
    // Runs regardless of WebSocket state. Stops when cancelled or report found.
    const poll = async () => {
      if (cancelled) return;
      try {
        const report = await getReport(runId);
        if (!cancelled) dispatch({ type: "report_polled", report });
      } catch {
        if (!cancelled) pollTimer = setTimeout(poll, 2000);
      }
    };
    pollTimer = setTimeout(poll, 1500);

    return () => {
      cancelled = true;
      if (pollTimer) clearTimeout(pollTimer);
      ws.close();
    };
  }, [runId]);

  return state;
}
