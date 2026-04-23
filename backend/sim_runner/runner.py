import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Awaitable

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_GENERATED_DIR = _PROJECT_ROOT / "generated"


@dataclass
class SimResult:
    coverage_dat_path: Path
    passed: bool
    returncode: int


async def run_simulation(
    test_code: str,
    run_id: str,
    iteration: int,
    toplevel: str = "uart_rx",
    on_line: Callable[[str], Awaitable[None]] | None = None,
) -> SimResult:
    """
    Saves generated test, runs via cocotb Makefile, calls on_line for each
    stdout line (for live streaming), returns SimResult when done.
    """
    test_dir = _GENERATED_DIR / run_id
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "__init__.py").touch()

    module_name = f"test_iter_{iteration}"
    test_file = test_dir / f"{module_name}.py"
    test_file.write_text(test_code)

    coverage_dat = _PROJECT_ROOT / "coverage.dat"
    coverage_dat.unlink(missing_ok=True)

    cmd = [
        "make", "sim",
        f"MODULE=generated.{run_id}.{module_name}",
        f"TOPLEVEL={toplevel}",
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(_PROJECT_ROOT),
    )

    assert proc.stdout is not None
    async for raw in proc.stdout:
        line = raw.decode(errors="replace").rstrip()
        if on_line:
            await on_line(line)

    await proc.wait()
    return SimResult(
        coverage_dat_path=coverage_dat if coverage_dat.exists() else Path(""),
        passed=proc.returncode == 0,
        returncode=proc.returncode or 0,
    )
