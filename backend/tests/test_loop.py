import pytest
from unittest.mock import AsyncMock, patch
from backend.orchestrator.loop import VerificationLoop
from backend.plan.schema import VerificationPlan, Protocol
from backend.coverage.parser import CoverageResult, CoverageGap

MINIMAL_TEST = """\
import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_reset(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())
    dut.rx.value = 1
    dut.rst_n.value = 0
    dut.baud_div.value = 10
    await Timer(50, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    assert int(dut.rx_valid.value) == 0
"""


@pytest.fixture
def plan():
    return VerificationPlan(
        module="uart_rx",
        rtl_file="rtl/uart_rx.sv",
        protocol=Protocol.UART_8N1,
        baud_divs=[10],
        test_data=[0xA5],
        coverage_target_pct=50,
        max_iterations=2,
    )


@pytest.mark.asyncio
async def test_loop_emits_events(plan):
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = MINIMAL_TEST

    events = []

    async def capture(event):
        events.append(event)

    loop = VerificationLoop(plan=plan, llm=mock_llm)

    with patch("backend.orchestrator.loop.run_simulation") as mock_sim, \
         patch("backend.orchestrator.loop.parse_coverage_dat") as mock_cov:
        from backend.sim_runner.runner import SimResult
        from pathlib import Path
        mock_sim.return_value = SimResult(
            coverage_dat_path=Path("coverage.dat"), passed=True, returncode=0
        )
        mock_cov.return_value = CoverageResult(pct=75.0, gaps=[])

        report = await loop.run(run_id="test-run", on_event=capture)

    event_types = [e["type"] for e in events]
    assert "iteration" in event_types
    assert "coverage" in event_types
    assert "done" in event_types
    assert report.final_pct == 75.0
    assert report.target_reached  # 75 >= 50


@pytest.mark.asyncio
async def test_loop_stops_at_target(plan):
    mock_llm = AsyncMock()
    mock_llm.generate.return_value = MINIMAL_TEST

    loop = VerificationLoop(plan=plan, llm=mock_llm)

    with patch("backend.orchestrator.loop.run_simulation") as mock_sim, \
         patch("backend.orchestrator.loop.parse_coverage_dat") as mock_cov:
        from backend.sim_runner.runner import SimResult
        from pathlib import Path
        mock_sim.return_value = SimResult(
            coverage_dat_path=Path("coverage.dat"), passed=True, returncode=0
        )
        mock_cov.return_value = CoverageResult(pct=90.0, gaps=[])
        plan.coverage_target_pct = 80
        report = await loop.run(run_id="test-stop", on_event=None)

    assert len(report.iterations) == 1  # stopped after first iteration
