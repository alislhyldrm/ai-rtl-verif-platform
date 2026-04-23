from backend.llm.prompt_builder import build_rtl_context, build_task_prompt
from backend.parser.schema import Port, RtlInterface
from backend.plan.schema import Protocol, VerificationPlan


def _make_iface():
    return RtlInterface(
        module="uart_rx",
        ports=[
            Port(name="clk", direction="input", width=1),
            Port(name="rst_n", direction="input", width=1),
            Port(name="rx", direction="input", width=1),
            Port(name="rx_data", direction="output", width=8),
            Port(name="rx_valid", direction="output", width=1),
        ],
        fsm_states=["IDLE", "START", "DATA", "STOP"],
        parameters=[{"name": "baud_div", "default": 216}],
        clock="clk",
        reset={"signal": "rst_n", "active": "low"},
    )


def _make_plan():
    return VerificationPlan(
        module="uart_rx",
        rtl_file="rtl/uart_rx.sv",
        protocol=Protocol.UART_8N1,
        baud_divs=[10],
        test_data=[0xA5],
        coverage_target_pct=90,
        max_iterations=5,
    )


def test_rtl_context_contains_module_name():
    ctx = build_rtl_context(_make_iface(), _make_plan())
    assert "uart_rx" in ctx


def test_rtl_context_contains_all_ports():
    ctx = build_rtl_context(_make_iface(), _make_plan())
    assert "rx_data" in ctx
    assert "rx_valid" in ctx
    assert "rst_n" in ctx


def test_rtl_context_contains_fsm_states():
    ctx = build_rtl_context(_make_iface(), _make_plan())
    assert "IDLE" in ctx
    assert "STOP" in ctx


def test_task_prompt_no_gaps():
    prompt = build_task_prompt(iteration=1, gaps=[])
    assert "iteration 1" in prompt.lower()
    assert "no gaps" in prompt.lower() or "initial" in prompt.lower()


def test_task_prompt_with_gaps():
    gaps = [
        {"file": "uart_rx.sv", "line": 57, "type": "branch", "description": "else branch never taken"},
        {"file": "uart_rx.sv", "line": 75, "type": "branch", "description": "frame_err never triggered"},
    ]
    prompt = build_task_prompt(iteration=2, gaps=gaps)
    assert "57" in prompt
    assert "frame_err" in prompt
    assert "else branch" in prompt
