import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PlanForm } from "@/components/plan/PlanForm";
import type { RtlInterface } from "@/api/types";

const IFACE: RtlInterface = {
  module: "uart_rx",
  ports: [{ name: "clk", direction: "input", width: 1 }],
  fsm_states: [],
  parameters: [],
  clock: "clk",
  reset: null,
};

test("renders with module name pre-filled", () => {
  render(<PlanForm iface={IFACE} rtlFilename="rtl/uart_rx.sv" onSubmit={() => {}} />);
  expect(screen.getByDisplayValue("uart_rx")).toBeInTheDocument();
});

test("calls onSubmit with a valid plan", async () => {
  const onSubmit = vi.fn();
  render(<PlanForm iface={IFACE} rtlFilename="rtl/uart_rx.sv" onSubmit={onSubmit} />);
  await userEvent.click(screen.getByRole("button", { name: /start/i }));
  expect(onSubmit).toHaveBeenCalledWith(
    expect.objectContaining({ module: "uart_rx", protocol: "UART_8N1" })
  );
});
