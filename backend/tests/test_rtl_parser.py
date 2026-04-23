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


from backend.parser.rtl_parser import parse_rtl
from pathlib import Path

RTL_PATH = Path("rtl/uart_rx.sv")


def test_parse_module_name():
    iface = parse_rtl(RTL_PATH)
    assert iface.module == "uart_rx"


def test_parse_ports():
    iface = parse_rtl(RTL_PATH)
    names = [p.name for p in iface.ports]
    assert "clk" in names
    assert "rst_n" in names
    assert "rx" in names
    assert "rx_data" in names
    assert "rx_valid" in names
    assert "frame_err" in names


def test_parse_port_directions():
    iface = parse_rtl(RTL_PATH)
    port_map = {p.name: p for p in iface.ports}
    assert port_map["clk"].direction == "input"
    assert port_map["rx_data"].direction == "output"
    assert port_map["rx_valid"].direction == "output"


def test_parse_port_widths():
    iface = parse_rtl(RTL_PATH)
    port_map = {p.name: p for p in iface.ports}
    assert port_map["rx_data"].width == 8
    assert port_map["baud_div"].width == 32
    assert port_map["clk"].width == 1


def test_parse_fsm_states():
    iface = parse_rtl(RTL_PATH)
    assert set(iface.fsm_states) == {"IDLE", "START", "DATA", "STOP"}


def test_detect_clock():
    iface = parse_rtl(RTL_PATH)
    assert iface.clock == "clk"


def test_detect_reset():
    iface = parse_rtl(RTL_PATH)
    assert iface.reset is not None
    assert iface.reset["signal"] == "rst_n"
    assert iface.reset["active"] == "low"
