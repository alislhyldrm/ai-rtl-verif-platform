import pytest
from backend.parser.schema import Port, RtlInterface


def test_port_model():
    p = Port(name="clk", direction="input", width=1)
    assert p.name == "clk"
    assert p.direction == "input"
    assert p.width == 1


def test_rtl_interface_model():
    iface = RtlInterface(
        module="uart_rx",
        ports=[Port(name="clk", direction="input", width=1)],
        fsm_states=["IDLE", "START", "DATA", "STOP"],
        parameters=[{"name": "baud_div", "width": 32, "default": 216}],
        clock="clk",
        reset={"signal": "rst_n", "active": "low"},
    )
    assert iface.module == "uart_rx"
    assert len(iface.ports) == 1
    assert iface.clock == "clk"
