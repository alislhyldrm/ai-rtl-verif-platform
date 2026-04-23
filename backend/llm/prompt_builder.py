from backend.parser.schema import RtlInterface
from backend.plan.schema import VerificationPlan


def build_rtl_context(iface: RtlInterface, plan: VerificationPlan) -> str:
    ports_table = "\n".join(
        f"  - {p.name}: {p.direction}, {p.width}-bit"
        for p in iface.ports
    )
    fsm = ", ".join(iface.fsm_states) if iface.fsm_states else "none detected"
    clock_info = (
        f"Clock: {iface.clock}" if iface.clock else "Clock: not detected"
    )
    reset_info = (
        f"Reset: {iface.reset['signal']} (active {iface.reset['active']})"
        if iface.reset
        else "Reset: not detected"
    )
    baud_divs = ", ".join(str(d) for d in plan.baud_divs)
    test_data = ", ".join(hex(b) for b in plan.test_data)
    error_inj = ", ".join(e.value for e in plan.error_injection) or "none"

    return f"""\
MODULE: {iface.module}
PROTOCOL: {plan.protocol.value}
{clock_info}
{reset_info}

PORTS:
{ports_table}

FSM STATES: {fsm}

VERIFICATION PARAMETERS:
  Baud dividers to test: {baud_divs}
  Test data bytes: {test_data}
  Error injection: {error_inj}
  Coverage target: {plan.coverage_target_pct}%
"""


def build_task_prompt(iteration: int, gaps: list[dict]) -> str:
    if not gaps:
        return (
            f"Iteration {iteration}: This is the initial test generation. "
            "Write a comprehensive cocotb test that covers the main functionality: "
            "basic data reception, correct framing, and the rx_valid signal. "
            "Use the baud_divs and test_data from the context above. "
            "There are no coverage gaps yet — aim for broad coverage."
        )

    gap_lines = "\n".join(
        f"  - {g['file']}:{g['line']} [{g['type']}] {g['description']}"
        for g in gaps
    )
    return (
        f"Iteration {iteration}: The previous test achieved partial coverage. "
        f"The following branches/lines were NOT executed:\n{gap_lines}\n\n"
        "Write a NEW cocotb test that specifically targets these uncovered paths. "
        "Focus on the conditions that would trigger each missing branch."
    )
