import { render, screen } from "@testing-library/react";
import { InterfacePreview } from "@/components/upload/InterfacePreview";
import type { RtlInterface } from "@/api/types";

const MOCK_IFACE: RtlInterface = {
  module: "uart_rx",
  ports: [
    { name: "clk", direction: "input", width: 1 },
    { name: "rx_data", direction: "output", width: 8 },
  ],
  fsm_states: ["IDLE", "START", "DATA", "STOP"],
  parameters: [],
  clock: "clk",
  reset: { signal: "rst_n", active: "low" },
};

test("renders module name", () => {
  render(<InterfacePreview iface={MOCK_IFACE} />);
  expect(screen.getByText("uart_rx")).toBeInTheDocument();
});

test("renders all port names", () => {
  render(<InterfacePreview iface={MOCK_IFACE} />);
  expect(screen.getByText("clk")).toBeInTheDocument();
  expect(screen.getByText("rx_data")).toBeInTheDocument();
});

test("renders FSM states", () => {
  render(<InterfacePreview iface={MOCK_IFACE} />);
  expect(screen.getByText("IDLE")).toBeInTheDocument();
  expect(screen.getByText("STOP")).toBeInTheDocument();
});
