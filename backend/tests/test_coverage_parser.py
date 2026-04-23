import pytest
from pathlib import Path
from backend.coverage.parser import parse_coverage_info, CoverageResult, CoverageGap

SAMPLE_INFO = """\
TN:
SF:rtl/uart_rx.sv
DA:25,1
DA:57,0
DA:75,0
BRDA:57,0,0,1
BRDA:57,0,1,0
BRDA:75,0,0,0
BRDA:75,0,1,1
LH:1
LF:3
BRH:2
BRF:4
end_of_record
"""


def test_parse_coverage_pct(tmp_path):
    info = tmp_path / "coverage.info"
    info.write_text(SAMPLE_INFO)
    result = parse_coverage_info(info)
    # (LH+BRH)/(LF+BRF) = (1+2)/(3+4) ≈ 42.9
    assert 42.0 < result.pct < 44.0


def test_parse_line_gaps(tmp_path):
    info = tmp_path / "coverage.info"
    info.write_text(SAMPLE_INFO)
    result = parse_coverage_info(info)
    gap_lines = [g.line for g in result.gaps if g.type == "line"]
    assert 57 in gap_lines
    assert 75 in gap_lines
    assert 25 not in gap_lines  # line 25 is covered (count=1)


def test_parse_branch_gaps(tmp_path):
    info = tmp_path / "coverage.info"
    info.write_text(SAMPLE_INFO)
    result = parse_coverage_info(info)
    branch_gaps = [g for g in result.gaps if g.type == "branch"]
    assert len(branch_gaps) >= 1


def test_no_gaps_when_fully_covered(tmp_path):
    full_info = """\
TN:
SF:rtl/uart_rx.sv
DA:10,5
LH:1
LF:1
BRH:2
BRF:2
end_of_record
"""
    info = tmp_path / "coverage.info"
    info.write_text(full_info)
    result = parse_coverage_info(info)
    assert result.pct == 100.0
    assert result.gaps == []
