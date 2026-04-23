import { renderHook, act } from "@testing-library/react";
import { useVerificationRun } from "@/hooks/useVerificationRun";

// Silence WebSocket errors in tests
beforeEach(() => {
  vi.spyOn(console, "error").mockImplementation(() => {});
  (global as unknown as Record<string, unknown>).WebSocket = class {
    onopen: (() => void) | null = null;
    onmessage: ((e: { data: string }) => void) | null = null;
    close() {}
  };
});

afterEach(() => {
  vi.restoreAllMocks();
});

test("starts in connecting state", () => {
  const { result } = renderHook(() => useVerificationRun("test-123"));
  expect(result.current.status).toBe("connecting");
});

test("processes iteration event", () => {
  const { result } = renderHook(() => useVerificationRun("test-123"));
  act(() => {
    result.current._dispatchForTest({
      type: "iteration",
      n: 1,
      of: 3,
      phase: "generating",
    });
  });
  expect(result.current.currentIteration).toBe(1);
  expect(result.current.currentPhase).toBe("generating");
});

test("accumulates coverage history", () => {
  const { result } = renderHook(() => useVerificationRun("test-123"));
  act(() => {
    result.current._dispatchForTest({ type: "coverage", pct: 45.0, gaps: [] });
    result.current._dispatchForTest({ type: "coverage", pct: 72.0, gaps: [] });
  });
  expect(result.current.coverageHistory).toHaveLength(2);
  expect(result.current.coverageHistory[1]).toBe(72.0);
});

test("marks done when done event arrives", () => {
  const { result } = renderHook(() => useVerificationRun("test-123"));
  act(() => {
    result.current._dispatchForTest({
      type: "done",
      final_pct: 88.0,
      iterations: 3,
      target_reached: true,
    });
  });
  expect(result.current.status).toBe("done");
  expect(result.current.finalReport?.final_pct).toBe(88.0);
});
