# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`ai-rtl-verif-platform` is a learning project building an AI-powered RTL verification platform.

- **Phase 1 (complete):** UART peripheral in SystemVerilog, verified with cocotb + Verilator
- **Phase 2 (implementation ready):** AI layer — coverage-guided test generation loop with a React web dashboard

## Current State (as of 2026-04-24)

**Architecture spec:** `docs/superpowers/specs/2026-04-23-architecture-design.md` — fully approved, read this first.

**Backend:** COMPLETE. FastAPI REST + WebSocket, RTL parser, LLM client, sim runner, coverage parser, loop orchestrator. 25/25 tests green.

**Frontend:** COMPLETE (M9). React + Vite + TypeScript + shadcn. All 8 tasks in `docs/superpowers/plans/2026-04-23-frontend.md` shipped.

**Coverage merging (added 2026-04-24):** Previously the loop only reported the last iteration's coverage — each iteration wiped `coverage.dat`. Now per-iteration dats are stored at `generated/{run_id}/coverage_iter_N.dat` and merged cumulatively each iteration via `parse_coverage_dats()` (calls `verilator_coverage --write-info` with all dats). `max_iterations` in `plans/uart_rx.yaml` bumped 5 → 10.

**Known open issue:** Even with cumulative coverage and 10 iterations, the 90% target is not yet reliably reached on uart_rx. To investigate later — likely causes: AI generates similar tests across iterations (weak gap-driven diversification), prompt may need stronger few-shot examples of branch-specific stimulus, or target is simply too high for regex-parsed RTL context. Revisit prompt_builder.py gap-injection quality first.

**Future improvements:** `docs/TODO.md` — 8 items with industry context, pros/cons, priority table.

## What to Build Next

Frontend + backend are both shipped end-to-end. Remaining work:

1. **Push coverage closer to target** — diagnose why 90% isn't reached despite cumulative merging. See "Known open issue" above.
2. Items in `docs/TODO.md` (pyslang parser upgrade, cheaper model routing, dedicated verification agent, etc.).

## Key Architecture Decisions (do not revisit)

| Decision | Choice | Reason |
|----------|--------|--------|
| AI capability | Coverage-guided test generation loop | Solves 70% verification bottleneck |
| Input to Claude | RTL parser JSON + structured YAML (no free text) | Engineering control, minimize hallucination risk |
| Coverage metric | Verilator line+branch (`--coverage`) → lcov `.info` | Native, zero extra tooling |
| Backend | FastAPI (Python) + WebSocket | Shares language with cocotb; async-native |
| Frontend | React + TypeScript + Vite | Best dashboard ecosystem |
| RTL parser | Regex-based (MVP) | Practical for UART; pyslang upgrade in TODO |
| Prompt caching | Anthropic SDK ephemeral cache on RTL context block | Saves tokens on iterations 2+ |
| Scope | General platform, UART as reference demo | Forces clean abstractions |

## Phase 2 System Architecture

```
React Dashboard ←WebSocket→ FastAPI Backend ←subprocess→ Verilator + cocotb
                             FastAPI Backend ←Anthropic SDK→ Claude API
```

**Loop:** RTL(.sv) + YAML plan → parser JSON → prompt builder → Claude → cocotb test → Verilator `--coverage` → coverage.dat → lcov parser → gap list → back to prompt builder → repeat until coverage % ≥ target.

**WebSocket message types:** `log`, `iteration`, `coverage`, `test_ready`, `done`, `error`

**REST endpoints:** `POST /api/upload-rtl`, `POST /api/validate-plan`, `POST /api/run`, `GET /api/runs/{id}/report`, `GET /api/runs/{id}/tests/{n}`, `DELETE /api/runs/{id}`, `WS /ws/{run_id}`

## Directory Structure

```
ai-rtl-verif-platform/
├── rtl/                    # Phase 1 RTL — untouched
├── tests/                  # Phase 1 cocotb tests — golden models reused in Phase 2
├── plans/                  # YAML verification plans (uart_rx.yaml to be created in Task 4)
├── generated/              # gitignored — AI-generated cocotb tests go here
├── backend/                # FastAPI app (to be built per plan)
│   ├── parser/             # rtl_parser.py, schema.py
│   ├── plan/               # schema.py (VerificationPlan)
│   ├── llm/                # client.py, prompt_builder.py
│   ├── orchestrator/       # loop.py
│   ├── sim_runner/         # runner.py
│   ├── coverage/           # parser.py
│   └── main.py
├── frontend/               # React + Vite + TypeScript (Phase 2, after backend)
├── docs/
│   ├── TODO.md
│   └── superpowers/
│       ├── specs/          # 2026-04-23-architecture-design.md
│       └── plans/          # 2026-04-23-backend.md
├── requirements-backend.txt  # to be created in Task 1
├── Makefile                  # extend: add COMPILE_ARGS += --coverage in Task 7
└── CLAUDE.md
```

## Phase 1 Commands (existing)

```bash
source .venv/bin/activate   # always required

make csr                    # CSR block tests
make fifo                   # FIFO unit tests
make tx                     # UART TX tests
make rx                     # UART RX tests (TOPLEVEL=uart_rx)
make smoke                  # smoke test
make sim MODULE=tests.test_fifo   # run specific module
```

## Phase 2 Commands (after backend is built)

```bash
source .venv/bin/activate
pip install -r requirements-backend.txt

# Start backend
uvicorn backend.main:app --reload --port 8000

# Run backend tests
pytest backend/tests/ -v

# Required env var
export ANTHROPIC_API_KEY=your_key_here
```

## Phase 1 Architecture (RTL)

```
uart_top (top)
├── csr_block   — registers: ID(0x00), CTRL(0x04), BAUD_DIV(0x08), STATUS(0x0C)
├── fifo #(16,8) — TX FIFO; write via addr 0x10
├── uart_tx     — reads FIFO, shifts start+8data+stop at baud_div rate
└── uart_rx     — standalone; FSM: IDLE→START→DATA→STOP; center-sampling; dual-FF sync
```

- `ctrl_reg[0]` = UART enable — gates TX FIFO read
- `baud_div` = clock-cycle counter; baud period = `baud_div` cycles
- `uart_rx` not yet wired into `uart_top`

## Testbench Pattern (Phase 1)

Golden-model style — no UVM. One side drives DUT, Python model drives/reads the other side at pin level.

- `test_uart_tx.py` → `uart_rx_golden_model()` reads TX pin, validates LSB-first framing
- `test_uart_rx.py` → `uart_tx_golden_model()` drives RX pin; awaits `rx_valid`

## Milestones

| # | Status | Description |
|---|--------|-------------|
| 1 | ✅ Done | CSR block + unit tests |
| 2 | ✅ Done | FIFO + unit tests |
| 3 | ✅ Done | UART TX engine + golden model tests |
| 4 | ✅ Done | UART RX engine + center-sampling validation |
| 5 | ✅ Done | Architecture spec + backend plan written |
| 6 | ✅ Done | Backend implemented — 25/25 tests green |
| 7 | ✅ Done | Frontend (M9) — all 8 tasks shipped |
| 8 | ✅ Done | Cumulative coverage merging across iterations |
| 9 | 🔄 Next | Reach 90% coverage target reliably (prompt/gap diversification) |

## Key Constraints

- `.venv/` — always activate before any make or python command
- `uart_rx` tested standalone (`TOPLEVEL=uart_rx`); not integrated into `uart_top`
- `sim_build/` — Verilator artifacts, safe to delete
- `generated/` — gitignored, created at runtime by the backend
- No co-author lines in git commits
- `ANTHROPIC_API_KEY` must be set in environment before running backend
