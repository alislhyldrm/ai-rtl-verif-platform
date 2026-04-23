# AI-RTL Verification Platform — Architecture Spec

**Date:** 2026-04-23  
**Status:** Approved  
**Phase:** 2 (AI layer on top of completed UART RTL)

---

## 1. Problem & Goal

Verification consumes ~70% of IC development effort. This platform automates the test generation and coverage closure loop using Claude AI, on top of an existing cocotb + Verilator stack.

**Goal:** A web dashboard where an engineer uploads an RTL module, fills a structured verification plan (no free text), and watches the AI generate, simulate, and refine cocotb tests until a coverage target is hit — all live in the browser.

---

## 2. Core Concept

A closed feedback loop:

```
RTL (.sv) + YAML plan
    → RTL Parser (pyslang) → interface JSON
    → Prompt Builder → deterministic structured prompt
    → Claude API → cocotb testbench
    → Verilator (--coverage) → simulation + coverage.dat
    → Coverage Parser → gap list JSON
    → back to Prompt Builder (next iteration)
    → repeat until coverage % ≥ target or max_iterations reached
```

All live output streamed to React dashboard via WebSocket.

---

## 3. Key Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| AI capability | Coverage-guided test generation | Solves the 70% verification bottleneck; most industry-active area |
| Input to Claude | RTL parser JSON + structured YAML (no free text) | Engineering control — minimizes hallucination risk |
| Coverage metric (MVP) | Verilator line + branch (`--coverage`) | Native, zero extra tooling, parseable .dat output |
| Backend | FastAPI (Python) | Shares language with cocotb layer; native async + WebSocket |
| Frontend | React + TypeScript + Vite | Best dashboard ecosystem (Recharts, shadcn/ui); clean separation |
| Realtime | WebSocket (one connection per run) | Streams log lines + coverage updates live |
| Scope | General platform, UART as reference demo | Forces clean abstractions without getting lost in generality |

---

## 4. Architecture

### 4.1 System Layers

```
┌─────────────────────────────────────────────────┐
│  React Dashboard (TypeScript + Vite)            │
│  Setup View → Live Dashboard View               │
└────────────┬──────────────┬─────────────────────┘
             │ REST         │ WebSocket /ws/{run_id}
┌────────────▼──────────────▼──────────┐  ┌───────────────────────────────────┐
│  FastAPI Backend (Python)            │  │  Claude API (claude-sonnet-4-6)   │
│  ┌──────────┐ ┌───────────┐          │  │  Prompt caching on RTL context    │
│  │RTL Parser│ │Orchestrat.│          │  │  (saves tokens on iterations 2+)  │
│  │(pyslang) │ │(loop.py)  │          │  └───────────────────────────────────┘
│  └──────────┘ └─────┬─────┘          │           ▲
│  ┌──────────┐ ┌─────▼─────┐          │  Anthropic │ SDK (async HTTP)
│  │Plan      │ │Sim Runner │          │           │
│  │Validator │ │(async sub)│          │  ┌────────┴──────────────────────────┐
│  │(Pydantic)│ └─────┬─────┘          │  │  LLM Client + Prompt Builder      │
│  └──────────┘       │  ┌────────────┐│  │  (inside FastAPI backend)         │
│  ┌──────────────┐   │  │Coverage    ││  └───────────────────────────────────┘
│  │WebSocket Hub │   │  │Parser      ││
│  │(typed msgs)  │   │  │(.dat→JSON) ││
│  └──────────────┘   │  └────────────┘│
└─────────────────────┼────────────────┘
                      │ subprocess + file I/O
           ┌──────────▼──────────────────────┐
           │  Verilator + cocotb (existing)  │
           │  rtl/*.sv  │ tests/ │ Makefile  │
           └─────────────────────────────────┘
```

### 4.2 Backend Modules

**`backend/parser/rtl_parser.py`**  
Input: path to `.sv` file  
Output: `RtlInterface` Pydantic model — module name, ports (name/dir/width), FSM states, parameters, detected clock/reset  
Tool: pyslang (Microsoft open-source SV parser). Heuristic fallback for clock/reset detection by naming convention.

**`backend/llm/prompt_builder.py`**  
Input: `RtlInterface` + validated `VerificationPlan` + coverage gap list (empty on iteration 1)  
Output: structured prompt string  
Structure:
```
[SYSTEM]   role + cocotb format rules + output constraints
[CACHED]   RTL interface JSON + protocol context (cached across iterations)
[DYNAMIC]  coverage gaps from current iteration
[TASK]     generate cocotb test targeting these specific uncovered branches
```
RTL context uses Anthropic prompt caching — paid once on iteration 1, free on 2–5.

**`backend/orchestrator/loop.py`**  
Owns the iteration state machine. Runs as FastAPI background task.
```python
while coverage_pct < target and iteration < max_iterations:
    prompt = build_prompt(rtl_json, plan, gaps)
    test_code = await claude.generate(prompt)
    save_test(test_code, run_id, iteration)
    coverage_pct, gaps = await sim_runner.run(test_code)
    await ws_hub.broadcast(run_id, coverage_pct, gaps)
    iteration += 1
return build_report(run_id)
```

**`backend/sim_runner/runner.py`**  
Async subprocess wrapper. Calls Verilator directly (not via Makefile) for generated tests: `verilator --coverage --binary -o sim_build/Vsim rtl/*.sv && python generated/{run_id}/test_iter_{n}.py` via `asyncio.subprocess`. The existing Makefile targets remain unchanged for hand-written tests. Streams each stdout line to WebSocket hub in real-time. Returns path to `coverage.dat` on completion.

**`backend/coverage/parser.py`**  
Reads Verilator `coverage.dat` text format. Outputs `CoverageResult(pct: float, gaps: list[CoverageGap])`. Each gap: `{file, line, type: "branch"|"line", description}`. Gap list is appended to next iteration's prompt.

**`backend/llm/client.py`**  
Anthropic SDK async client. Single `generate(prompt) -> str` method. Prompt caching configured on the RTL context block. Model: `claude-sonnet-4-6`.

**`backend/plan/schema.py` + `backend/parser/schema.py`**  
All Pydantic models. Plan validated before any Claude call. Parser output typed before entering prompt builder.

### 4.3 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-rtl` | Upload `.sv` file → returns parser JSON (engineering review gate) |
| POST | `/api/validate-plan` | Validate YAML plan → errors or `{"valid": true}` |
| POST | `/api/run` | Start verification loop → returns `run_id` |
| GET | `/api/runs/{run_id}/report` | Download final report JSON |
| GET | `/api/runs/{run_id}/tests/{n}` | Fetch generated test file for iteration n |
| DELETE | `/api/runs/{run_id}` | Cancel running loop |
| WS | `/ws/{run_id}` | WebSocket — streams all events for a run |

### 4.4 WebSocket Message Types

```jsonc
{"type": "log",        "text": "...", "source": "verilator"}
{"type": "iteration",  "n": 2, "of": 5, "phase": "generating"}
{"type": "coverage",   "pct": 67.3, "gaps": [{line, type, desc}]}
{"type": "test_ready", "iteration": 2, "url": "/api/runs/abc/tests/2"}
{"type": "done",       "final_pct": 91.2, "iterations": 3, "report_url": "..."}
{"type": "error",      "code": "SIM_FAIL", "message": "..."}
```

### 4.5 YAML Verification Plan Schema

```yaml
module: uart_rx
rtl_file: rtl/uart_rx.sv
protocol: UART_8N1            # enum: UART_8N1 | SPI | I2C | AXI4L | CUSTOM
baud_divs: [10, 20, 50]       # list[int] — validated
test_data: [0x00, 0xFF, 0xA5] # list[int 0–255]
error_injection:
  - frame_error               # enum: frame_error | parity_error | noise | none
coverage_target_pct: 90       # int 1–100
max_iterations: 5             # int 1–10
golden_model: tests/test_uart_rx.py  # optional
```

All fields Pydantic-validated. Run rejected before Claude call if any field fails.

### 4.6 Frontend Components

**View 1 — Setup**
- `RtlDropZone` — file upload, calls `POST /api/upload-rtl`, passes result to ParserPreviewCard
- `ParserPreviewCard` — shows extracted ports/FSM states — **engineering review gate #1**
- `VerificationPlanForm` — form-based builder, all dropdowns/sliders/checkboxes (no free text), calls `POST /api/validate-plan` on change

**View 2 — Live Dashboard**
- `CoverageChart` — Recharts LineChart, updates on `coverage` WS messages, shows target line
- `IterationStatusBar` — phase indicator: Parsing → Generating → Simulating → Analyzing → Done
- `SimLogTerminal` — scrolling terminal, color-coded by log level
- `TestFileViewer` — tabbed code viewer (Prism.js), one tab per iteration
- `useVerificationSocket` — custom hook, owns WS connection, dispatches messages to component state

**Tech:** React 18 + TypeScript, Vite, Recharts, Tailwind CSS, shadcn/ui, Prism.js

---

## 5. Directory Structure

```
ai-rtl-verif-platform/
├── rtl/                          # ✅ existing — untouched
├── tests/                        # ✅ existing — golden models reused
├── plans/
│   └── uart_rx.yaml              # reference verification plan
├── generated/                    # gitignored — AI-generated tests
│   └── {run_id}/test_iter_N.py
├── backend/
│   ├── main.py                   # FastAPI app, routes
│   ├── parser/                   # rtl_parser.py, schema.py
│   ├── orchestrator/             # loop.py
│   ├── sim_runner/               # runner.py
│   ├── coverage/                 # parser.py
│   ├── llm/                      # client.py, prompt_builder.py
│   └── plan/                     # schema.py
├── frontend/
│   └── src/
│       ├── components/           # 7 components listed above
│       ├── hooks/                # useVerificationSocket.ts
│       └── api/                  # client.ts
├── docs/
│   ├── TODO.md
│   └── superpowers/specs/        # this file
├── Makefile                      # extended with backend/frontend targets
└── CLAUDE.md
```

---

## 6. Implementation Milestones

| Milestone | Deliverable | Done When |
|-----------|-------------|-----------|
| M5 | RTL Parser + YAML plan + Pydantic validation | `parse uart_rx.sv` → correct JSON |
| M6 | Claude integration + first test generation | Claude writes a valid cocotb test that runs |
| M7 | Verilator coverage + loop orchestrator | Loop runs 3 iterations, coverage climbs each time |
| M8 | FastAPI backend + WebSocket streaming | `POST /api/run` streams live output to wscat |
| M9 | React dashboard (full UI) | End-to-end demo: upload → watch coverage hit 90% |

Estimated: ~6–7 weeks total.

---

## 7. What Existing Code Is Reused

- All `rtl/*.sv` files — untouched
- `tests/test_uart_rx.py` → `uart_tx_golden_model()` referenced in YAML plan
- `tests/test_uart_tx.py` → `uart_rx_golden_model()` referenced in YAML plan
- Makefile sim targets — called by Sim Runner
- cocotb + Verilator environment (`.venv/`)

---

## 8. Future Improvements

See `docs/TODO.md` for detailed breakdown of:
- FSM transition coverage (next after MVP)
- Functional covergroups
- SVA formal property input
- Golden model equivalence checking
- CI/CD integration
- Multi-LLM provider abstraction
- Waveform viewer
