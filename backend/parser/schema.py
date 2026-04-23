from typing import Literal, Optional
from pydantic import BaseModel


class Port(BaseModel):
    name: str
    direction: Literal["input", "output", "inout"]
    width: int


class RtlInterface(BaseModel):
    module: str
    ports: list[Port]
    fsm_states: list[str]
    parameters: list[dict]
    clock: Optional[str]
    reset: Optional[dict]  # {"signal": str, "active": "low"|"high"}
