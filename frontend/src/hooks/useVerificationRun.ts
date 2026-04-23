import { useEffect, useReducer, useRef } from "react";
import type { WsEvent, CoverageGap } from "@/api/types";

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

type Action = { type: "ws_event"; event: WsEvent } | { type: "connected" };

function reduce(state: RunState, action: Action): RunState {
  if (action.type === "connected") return { ...state, status: "running" };
  const ev = action.event;
  switch (ev.type) {
    case "iteration":
      return { ...state, currentIteration: ev.n, currentPhase: ev.phase };
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

  const [state, dispatch] = useReducer(reduce, undefined, () => {
    const initial: RunState = {
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
    };
    return initial;
  });

  dispatchRef.current = (event: WsEvent) => dispatch({ type: "ws_event", event });

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/${runId}`);
    wsRef.current = ws;

    ws.onopen = () => dispatch({ type: "connected" });
    ws.onmessage = (e) => {
      try {
        const event: WsEvent = JSON.parse(e.data as string);
        dispatch({ type: "ws_event", event });
      } catch {
        /* ignore malformed messages */
      }
    };

    return () => ws.close();
  }, [runId]);

  return state;
}
