# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`ai-rtl-verif-platform` is a learning project building an AI-powered RTL verification platform. Phase 1 (complete) delivers a fully verified UART peripheral in SystemVerilog. Phase 2 (in design) adds an AI layer on top of the cocotb/Verilator infrastructure.

## Test Commands

```bash
# Activate venv first (always required)
source .venv/bin/activate

# Run individual test suites
make csr        # CSR block tests
make fifo       # FIFO unit tests
make tx         # UART TX tests (default TOPLEVEL=uart_top)
make rx         # UART RX tests (TOPLEVEL=uart_rx)
make smoke      # Smoke test

# Run a specific test module directly
make sim MODULE=tests.test_fifo
```

All tests use cocotb + Verilator. Outputs go to `sim_build/`. Waveforms as `.vcd` if enabled.

## Architecture

### RTL (Phase 1 — Complete)

```
uart_top (top)
├── csr_block       — addr-mapped registers: ID(0x00), CTRL(0x04), BAUD_DIV(0x08), STATUS(0x0C)
├── fifo #(16,8)    — TX FIFO; write via addr 0x10; parameterizable DEPTH/WIDTH
├── uart_tx         — reads from FIFO, shifts out start+8data+stop at baud_div rate
└── uart_rx         — standalone module (not wired into uart_top yet)
                      FSM: IDLE→START→DATA→STOP; center-sampling; dual-FF sync on rx pin
```

Key signal: `ctrl_reg[0]` = UART enable. TX FIFO read is gated by this bit. `baud_div` is a clock-cycle counter — baud period = `baud_div` cycles.

### Testbench Pattern

Each test file follows a **golden-model** style: one side drives the DUT, a Python golden model drives/reads the other side at the pin level. No UVM, no scoreboard — just direct cocotb coroutines + asserts.

- `test_uart_tx.py` — `uart_rx_golden_model()` reads the TX pin and validates LSB-first framing
- `test_uart_rx.py` — `uart_tx_golden_model()` drives the RX pin; test awaits `rx_valid`

### Phase 2 — AI Layer (In Design)

Architecture brainstorm in progress. Spec will land in `docs/superpowers/specs/`. The AI layer will sit above the cocotb/Verilator stack. No code written yet.

## Milestones

| # | Status | Description |
|---|--------|-------------|
| 1 | ✅ Done | CSR block design + unit tests |
| 2 | ✅ Done | FIFO design + unit tests |
| 3 | ✅ Done | UART TX engine + golden model tests |
| 4 | ✅ Done | UART RX engine + center-sampling validation |
| 5 | 🔄 In Design | AI layer architecture (brainstorm session active) |
| 6 | ⬜ Pending | AI layer implementation |

## Key Constraints

- Python env is `.venv/` — always activate before running make targets
- `uart_rx` is tested standalone (`TOPLEVEL=uart_rx`); it is **not** yet integrated into `uart_top`
- `sim_build/` contains Verilator-compiled artifacts — safe to delete, rebuilt on next `make`
