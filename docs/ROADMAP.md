# Platform Roadmap — Future Improvements

This file tracks planned upgrades beyond the MVP. Each item explains what it is, why it matters, how we'd implement it, and what the industry says about it.

---

## MVP Scope (Current)

- RTL parser → extracts ports, FSM states automatically
- Structured YAML verification plan (no free text)
- Claude API generates cocotb testbenches
- Verilator runs with `--coverage` (line + branch)
- Coverage report feeds back to Claude
- Loop repeats until coverage target % hit
- React dashboard with live streaming

---

## Roadmap Items

---

### 1. FSM Transition Coverage (High Priority)

**What:** Track which FSM state transitions were exercised, not just which lines ran.
For `uart_rx`: did we cover IDLE→START, START→IDLE (false start), DATA→STOP, STOP→IDLE?

**Why:** Line coverage says "this code ran." FSM transition coverage says "this protocol path was exercised." For communication protocols, the paths matter more than the lines. A bug often lives in a transition that line coverage says is "covered" but was never tested under the right conditions.

**Industry relevance:** Standard practice in any UVM-based verification plan. Cadence and Synopsys coverage tools report FSM arcs as a first-class metric. Hiring managers in verification roles will specifically ask about transition coverage.

**How we'd implement it:**
- Extend the RTL parser to detect `typedef enum` + FSM state registers
- Instrument the cocotb testbench to log `(prev_state, next_state)` transitions at runtime
- Post-process the log to build a transition coverage matrix
- Feed uncovered transitions to Claude: "IDLE→START under false-start condition never triggered — generate a test for it"

**Advantages:**
- Much more meaningful than line coverage for protocol IPs
- Directly maps to the verification plan (every arc in the FSM diagram)
- Claude can generate very targeted tests ("drive rx=0 for half a baud period then return high")

**Disadvantages:**
- Requires custom extraction logic (Verilator doesn't output this natively)
- FSM detection heuristics can miss complex state encodings

---

### 2. Functional Coverage with Covergroups (Medium Priority)

**What:** Define coverage bins in the structured YAML plan — combinations of inputs/outputs that must be observed. Example: "we must see baud_div=10 AND a valid frame AND a frame error in the same run."

**Why:** Code coverage tells you what ran. Functional coverage tells you what *scenarios* were tested. Two testbenches can have identical line coverage but test completely different corner cases. Functional coverage closes this gap.

**Industry relevance:** Functional coverage is the primary metric in industrial UVM environments. The IEEE 1800 standard includes covergroups as a first-class language feature. Most chip companies require >95% functional coverage before tape-out sign-off.

**How we'd implement it:**
- Add a `coverage_model` section to the YAML verification plan
- Schema defines bins: `{signal, values, cross_with}`
- Python runtime tracker samples signals at each clock edge and logs bin hits
- Feed uncovered bins to Claude as structured JSON

**Advantages:**
- The most meaningful coverage metric in industry
- Directly derived from the structured YAML — no free text, high control
- Shows "verification completeness" not just "code was executed"

**Disadvantages:**
- Requires defining the coverage model upfront (more human input, but structured)
- More complex runtime infrastructure
- Overkill for simple modules

---

### 3. SVA / Formal Property Input (Low Priority — Advanced)

**What:** Allow engineers to provide SystemVerilog Assertions (SVA) alongside the RTL. Claude reads the formal properties and generates tests that specifically exercise and validate them.

**Why:** SVA is the gold standard for expressing hardware correctness properties. It's unambiguous by definition — a formal language with no room for misinterpretation. This is what Synopsys VC Formal and Cadence Jasper use.

**Industry relevance:** Every serious chip company writes SVA for their IP blocks. Being able to ingest SVA and generate simulation-based tests from it bridges formal and simulation verification — a workflow that Mentor/Siemens EDA is actively productizing.

**How we'd implement it:**
- SVA parser (Verible supports this) extracts property definitions
- Claude receives SVA text + structured interface JSON
- Claude generates cocotb tests that deliberately trigger the condition and check the consequent

**Advantages:**
- Zero ambiguity — SVA is a formal language
- Engineers who write SVA already know what they want to test
- Bridges formal verification and simulation worlds

**Disadvantages:**
- SVA is hard to write correctly — steep learning curve
- Chicken-and-egg: if you can write perfect SVA, you mostly already know what to test
- Parser must handle the full SVA subset — complex engineering

---

### 4. Golden Model Integration as Equivalence Checker (Medium Priority)

**What:** The Python golden models already in the codebase (`uart_rx_golden_model`, `uart_tx_golden_model`) become first-class inputs. Claude generates tests that specifically probe the boundary between RTL and model behavior.

**Why:** You already have golden models. This is Option 4 from our brainstorm — and it's free engineering leverage. The gap between RTL and model is exactly where bugs hide.

**Industry relevance:** Synopsys HECTOR and Cadence Jasper C Apps do this commercially — formal equivalence checking between C/C++ reference models and RTL. We do the simulation-based version.

**How we'd implement it:**
- Structured YAML gains a `golden_model` field pointing to the Python file
- Claude generates tests that run both the model and the DUT, compare outputs signal-by-signal
- Any divergence is a bug, not just a coverage miss

**Advantages:**
- Catches functional bugs, not just coverage gaps
- Golden models already exist in this codebase — low extra cost
- Outputs are binary (match / mismatch) — easy to reason about

**Disadvantages:**
- Model bugs can mask RTL bugs — need to trust the model
- Model must be kept in sync with RTL changes

---

### 5. Multi-LLM Support / Provider Abstraction (Low Priority)

**What:** Abstract the Claude API calls behind a provider interface. Swap in GPT-4, Gemini, or a local model (Llama, Mistral) without changing the verification loop.

**Why:** In production environments, organizations may have LLM vendor contracts, on-premise requirements (no data leaves the network), or cost constraints. Provider lock-in is a real concern for enterprise adoption.

**Industry relevance:** Most enterprise AI tools in EDA are moving toward provider-agnostic architectures. Synopsys.ai supports multiple model backends.

**How we'd implement it:**
- Define a `LLMProvider` abstract class with `generate(prompt) -> str`
- Implement `ClaudeProvider`, `OpenAIProvider`, `LocalProvider` (Ollama)
- YAML verification plan gains a `llm_provider` field

**Advantages:**
- Future-proof against vendor changes
- Allows cost/quality trade-off per use case
- On-premise option removes data security concerns

**Disadvantages:**
- Different models have different strengths at code generation — results will vary
- Extra abstraction layer to maintain

---

### 6. CI/CD Integration (Medium Priority)

**What:** A GitHub Actions / GitLab CI mode — run the verification loop automatically on every RTL commit. Report coverage delta in the PR.

**Why:** Manual verification is how bugs slip through. Continuous verification catches regressions before merge. This is where the "platform" becomes infrastructure, not just a tool.

**Industry relevance:** Every mature chip design team runs regression suites in CI. Cadence and Synopsys both offer cloud-native CI integration. This feature turns the project from "demo" into "used in production."

**How we'd implement it:**
- CLI entry point: `python verify.py --rtl rtl/uart_rx.sv --plan plans/uart_rx.yaml --ci`
- Outputs JUnit XML (coverage report as test results) — parseable by any CI system
- FastAPI backend gains a `/webhook` endpoint for GitHub push events

**Advantages:**
- Transforms the tool into infrastructure
- Forces clean API design (the CLI must be stable)
- Huge portfolio signal — shows you understand DevOps

**Disadvantages:**
- Costs money per CI run (Claude API + Verilator compute)
- Coverage regressions need a baseline to compare against

---

### 7. Waveform Viewer Integration (Low Priority — UX)

**What:** When a test fails or an interesting signal pattern is found, embed a lightweight waveform viewer in the dashboard (GTKWave-compatible VCD viewer in the browser).

**Why:** RTL engineers live in waveform viewers. Being able to click on a failing test and immediately see the signal trace is a massive productivity win. It's the difference between "AI suggested something" and "AI showed me the bug."

**Industry relevance:** Every EDA vendor has a waveform viewer. Cadence SimVision, Synopsys DVE, open-source GTKWave. Browser-based VCD viewers exist (vcd-viewer, WaveDrom).

**How we'd implement it:**
- Verilator outputs `.vcd` when run with `--trace`
- FastAPI serves the VCD file
- React embeds a VCD viewer library (wavedrom or a custom canvas renderer)

**Advantages:**
- Enormous UX improvement for engineers who review AI-generated tests
- Directly shows what the AI found, not just text descriptions
- Makes the dashboard look professional and complete

**Disadvantages:**
- VCD files get large fast — need size limits
- Browser-based VCD rendering is non-trivial to implement well

---

## Priority Summary

| Item | Priority | Effort | Industry Signal |
|------|----------|--------|-----------------|
| FSM Transition Coverage | High | Medium | High |
| Functional Covergroups | Medium | High | Very High |
| Golden Model Integration | Medium | Low | High |
| CI/CD Integration | Medium | Medium | Very High |
| SVA Input | Low | High | High |
| Multi-LLM Support | Low | Low | Medium |
| Waveform Viewer | Low | High | Medium |
