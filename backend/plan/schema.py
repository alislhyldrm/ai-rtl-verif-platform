from enum import Enum
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field, field_validator


class Protocol(str, Enum):
    UART_8N1 = "UART_8N1"
    SPI = "SPI"
    I2C = "I2C"
    AXI4L = "AXI4L"
    CUSTOM = "CUSTOM"


class ErrorInjection(str, Enum):
    FRAME_ERROR = "frame_error"
    PARITY_ERROR = "parity_error"
    NOISE = "noise"
    NONE = "none"


class VerificationPlan(BaseModel):
    module: str
    rtl_file: str
    protocol: Protocol
    baud_divs: list[int] = Field(min_length=1)
    test_data: list[int] = Field(min_length=1)
    error_injection: list[ErrorInjection] = Field(default_factory=list)
    coverage_target_pct: int = Field(ge=1, le=100, default=90)
    max_iterations: int = Field(ge=1, le=10, default=5)
    golden_model: Optional[str] = None

    @field_validator("test_data")
    @classmethod
    def validate_bytes(cls, v: list[int]) -> list[int]:
        for b in v:
            if not 0 <= b <= 255:
                raise ValueError(f"{b} is not a valid byte (0-255)")
        return v

    @field_validator("baud_divs")
    @classmethod
    def validate_baud_divs(cls, v: list[int]) -> list[int]:
        for d in v:
            if d < 4:
                raise ValueError(f"baud_div {d} too small (min 4)")
        return v

    @classmethod
    def from_yaml(cls, path: Path) -> "VerificationPlan":
        data = yaml.safe_load(Path(path).read_text())
        return cls(**data)
