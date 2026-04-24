import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CoverageGap:
    file: str
    line: int
    type: str  # "line" | "branch"
    description: str


@dataclass
class CoverageResult:
    pct: float
    gaps: list[CoverageGap] = field(default_factory=list)


def _dat_to_info(dat_path: Path, info_path: Path) -> None:
    subprocess.run(
        ["verilator_coverage", "--write-info", str(info_path), str(dat_path)],
        check=True,
        capture_output=True,
    )


def parse_coverage_info(info_path: Path) -> CoverageResult:
    text = info_path.read_text()
    lh = lf = brh = brf = 0
    gaps: list[CoverageGap] = []
    current_file = ""

    for line in text.splitlines():
        if line.startswith("SF:"):
            current_file = line[3:].strip()
        elif line.startswith("DA:"):
            parts = line[3:].split(",")
            lineno, count = int(parts[0]), int(parts[1])
            if count == 0:
                gaps.append(CoverageGap(
                    file=current_file, line=lineno,
                    type="line", description=f"line {lineno} never executed",
                ))
        elif line.startswith("BRDA:"):
            parts = line[5:].split(",")
            lineno, count = int(parts[0]), int(parts[3])
            if count == 0:
                branch_id = f"block {parts[1]} branch {parts[2]}"
                gaps.append(CoverageGap(
                    file=current_file, line=lineno,
                    type="branch",
                    description=f"branch at line {lineno} ({branch_id}) never taken",
                ))
        elif line.startswith("LH:"):
            lh = int(line[3:])
        elif line.startswith("LF:"):
            lf = int(line[3:])
        elif line.startswith("BRH:"):
            brh = int(line[4:])
        elif line.startswith("BRF:"):
            brf = int(line[4:])

    total = lf + brf
    hit = lh + brh
    pct = (hit / total * 100.0) if total > 0 else 100.0
    return CoverageResult(pct=round(pct, 1), gaps=gaps)


def parse_coverage_dat(dat_path: Path) -> CoverageResult:
    """Converts .dat → .info then parses."""
    info_path = dat_path.with_suffix(".info")
    _dat_to_info(dat_path, info_path)
    return parse_coverage_info(info_path)


def parse_coverage_dats(dat_paths: list[Path]) -> CoverageResult:
    """Merges multiple .dat files into one .info and parses cumulative coverage."""
    if not dat_paths:
        return CoverageResult(pct=0.0)
    info_path = dat_paths[0].parent / "coverage_merged.info"
    cmd = ["verilator_coverage", "--write-info", str(info_path)]
    cmd.extend(str(p) for p in dat_paths)
    subprocess.run(cmd, check=True, capture_output=True)
    return parse_coverage_info(info_path)
