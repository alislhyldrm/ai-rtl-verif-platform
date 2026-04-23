import pytest
from pydantic import ValidationError
from backend.plan.schema import VerificationPlan, Protocol, ErrorInjection


def test_valid_plan():
    plan = VerificationPlan(
        module="uart_rx",
        rtl_file="rtl/uart_rx.sv",
        protocol=Protocol.UART_8N1,
        baud_divs=[10, 20],
        test_data=[0x00, 0xFF, 0xA5],
        error_injection=[ErrorInjection.FRAME_ERROR],
        coverage_target_pct=90,
        max_iterations=5,
    )
    assert plan.module == "uart_rx"
    assert plan.coverage_target_pct == 90


def test_invalid_byte_rejected():
    with pytest.raises(ValidationError, match="valid byte"):
        VerificationPlan(
            module="x", rtl_file="x.sv", protocol=Protocol.UART_8N1,
            baud_divs=[10], test_data=[256],
        )


def test_coverage_target_bounds():
    with pytest.raises(ValidationError):
        VerificationPlan(
            module="x", rtl_file="x.sv", protocol=Protocol.UART_8N1,
            baud_divs=[10], test_data=[0], coverage_target_pct=101,
        )


def test_baud_div_too_small():
    with pytest.raises(ValidationError, match="too small"):
        VerificationPlan(
            module="x", rtl_file="x.sv", protocol=Protocol.UART_8N1,
            baud_divs=[2], test_data=[0],
        )


def test_from_yaml(tmp_path):
    import yaml
    data = {
        "module": "uart_rx",
        "rtl_file": "rtl/uart_rx.sv",
        "protocol": "UART_8N1",
        "baud_divs": [10, 20],
        "test_data": [0, 255, 165],
        "error_injection": ["frame_error"],
        "coverage_target_pct": 90,
        "max_iterations": 5,
    }
    f = tmp_path / "plan.yaml"
    f.write_text(yaml.dump(data))
    plan = VerificationPlan.from_yaml(f)
    assert plan.module == "uart_rx"
