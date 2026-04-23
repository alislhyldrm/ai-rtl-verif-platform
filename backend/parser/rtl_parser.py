import re
from pathlib import Path
from .schema import Port, RtlInterface

_MODULE_RE = re.compile(r'\bmodule\s+(\w+)', re.MULTILINE)
_PORT_RE = re.compile(
    r'^\s*(input|output|inout)\s+(?:logic\s+)?(?:\[(\d+):(\d+)\]\s+)?(\w+)\s*(?:[,;)]|$)',
    re.MULTILINE,
)
_PARAM_RE = re.compile(
    r'parameter\s+(?:int\s+)?(\w+)\s*=\s*(\d+)', re.MULTILINE
)
_ENUM_RE = re.compile(
    r'typedef\s+enum\s+\w+(?:\s*\[\d+:\d+\])?\s*\{([^}]+)\}', re.DOTALL
)

_CLOCK_NAMES = {"clk", "clk_i", "clock", "sys_clk", "pclk"}
_RESET_LOW = {"rst_n", "reset_n", "rstn", "areset_n", "nreset"}
_RESET_HIGH = {"rst", "reset", "sreset", "areset"}


def parse_rtl(path: Path) -> RtlInterface:
    src = Path(path).read_text()

    module_match = _MODULE_RE.search(src)
    if not module_match:
        raise ValueError(f"No module declaration found in {path}")
    module_name = module_match.group(1)

    ports: list[Port] = []
    for m in _PORT_RE.finditer(src):
        direction, high, low, name = m.group(1), m.group(2), m.group(3), m.group(4)
        width = (int(high) - int(low) + 1) if high is not None else 1
        ports.append(Port(name=name, direction=direction, width=width))

    fsm_states: list[str] = []
    for m in _ENUM_RE.finditer(src):
        raw = m.group(1)
        states = [s.strip().split("=")[0].strip() for s in raw.split(",") if s.strip()]
        fsm_states.extend(s for s in states if s)

    parameters: list[dict] = []
    for m in _PARAM_RE.finditer(src):
        parameters.append({"name": m.group(1), "default": int(m.group(2))})

    port_names = {p.name for p in ports}
    clock = next((n for n in _CLOCK_NAMES if n in port_names), None)

    reset = None
    for n in port_names:
        if n in _RESET_LOW:
            reset = {"signal": n, "active": "low"}
            break
        if n in _RESET_HIGH:
            reset = {"signal": n, "active": "high"}
            break

    return RtlInterface(
        module=module_name,
        ports=ports,
        fsm_states=fsm_states,
        parameters=parameters,
        clock=clock,
        reset=reset,
    )
