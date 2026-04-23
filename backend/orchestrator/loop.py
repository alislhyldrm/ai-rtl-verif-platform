from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Awaitable

from backend.coverage.parser import CoverageGap, CoverageResult, parse_coverage_dat
from backend.llm.client import LLMClient
from backend.llm.prompt_builder import build_rtl_context, build_task_prompt
from backend.parser.rtl_parser import parse_rtl
from backend.plan.schema import VerificationPlan
from backend.sim_runner.runner import SimResult, run_simulation


@dataclass
class IterationResult:
    iteration: int
    coverage: CoverageResult
    test_file: Path
    sim_passed: bool


@dataclass
class LoopReport:
    run_id: str
    final_pct: float
    iterations: list[IterationResult] = field(default_factory=list)
    target_reached: bool = False


OnEvent = Callable[[dict], Awaitable[None]]


class VerificationLoop:
    def __init__(self, plan: VerificationPlan, llm: LLMClient | None = None):
        self.plan = plan
        self.llm = llm or LLMClient()

    async def run(
        self,
        run_id: str,
        on_event: OnEvent | None = None,
    ) -> LoopReport:
        async def emit(event: dict) -> None:
            if on_event:
                await on_event(event)

        iface = parse_rtl(Path(self.plan.rtl_file))
        rtl_context = build_rtl_context(iface, self.plan)
        report = LoopReport(run_id=run_id, final_pct=0.0)
        gaps: list[CoverageGap] = []

        for i in range(1, self.plan.max_iterations + 1):
            await emit({"type": "iteration", "n": i,
                        "of": self.plan.max_iterations, "phase": "generating"})

            task_prompt = build_task_prompt(iteration=i, gaps=[g.__dict__ for g in gaps])
            test_code = await self.llm.generate(rtl_context, task_prompt)

            await emit({"type": "iteration", "n": i,
                        "of": self.plan.max_iterations, "phase": "simulating"})

            async def _on_line(line: str) -> None:
                await emit({"type": "log", "text": line, "source": "verilator"})

            sim_result: SimResult = await run_simulation(
                test_code=test_code,
                run_id=run_id,
                iteration=i,
                toplevel=self.plan.module,
                on_line=_on_line,
            )

            await emit({"type": "iteration", "n": i,
                        "of": self.plan.max_iterations, "phase": "analyzing"})

            coverage = CoverageResult(pct=0.0)
            if sim_result.coverage_dat_path.exists():
                coverage = parse_coverage_dat(sim_result.coverage_dat_path)

            gaps = coverage.gaps
            report.iterations.append(IterationResult(
                iteration=i,
                coverage=coverage,
                test_file=Path("generated") / run_id / f"test_iter_{i}.py",
                sim_passed=sim_result.passed,
            ))
            report.final_pct = coverage.pct

            await emit({"type": "coverage", "pct": coverage.pct,
                        "gaps": [g.__dict__ for g in gaps]})
            await emit({"type": "test_ready", "iteration": i,
                        "url": f"/api/runs/{run_id}/tests/{i}"})

            if coverage.pct >= self.plan.coverage_target_pct:
                report.target_reached = True
                break

        await emit({"type": "done", "final_pct": report.final_pct,
                    "iterations": len(report.iterations),
                    "target_reached": report.target_reached})
        return report
