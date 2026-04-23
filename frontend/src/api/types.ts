export interface Port {
  name: string;
  direction: "input" | "output" | "inout";
  width: number;
}

export interface RtlInterface {
  module: string;
  ports: Port[];
  fsm_states: string[];
  parameters: { name: string; default: number }[];
  clock: string | null;
  reset: { signal: string; active: "low" | "high" } | null;
}

export type Protocol = "UART_8N1" | "SPI" | "I2C" | "AXI4L" | "CUSTOM";
export type ErrorInjection = "frame_error" | "parity_error" | "noise" | "none";

export interface VerificationPlan {
  module: string;
  rtl_file: string;
  protocol: Protocol;
  baud_divs: number[];
  test_data: number[];
  error_injection?: ErrorInjection[];
  coverage_target_pct?: number;
  max_iterations?: number;
}

export interface RunResponse {
  run_id: string;
}

export interface RunReport {
  final_pct: number;
  iterations: number;
  target_reached: boolean;
}

export interface TestCodeResponse {
  code: string;
}

export interface CoverageGap {
  file: string;
  line: number;
  type: "line" | "branch";
  description: string;
}

export type WsEvent =
  | { type: "iteration"; n: number; of: number; phase: "generating" | "simulating" | "analyzing" }
  | { type: "log"; text: string; source: string }
  | { type: "coverage"; pct: number; gaps: CoverageGap[] }
  | { type: "test_ready"; iteration: number; url: string }
  | { type: "done"; final_pct: number; iterations: number; target_reached: boolean }
  | { type: "error"; detail: string };
