from anthropic import AsyncAnthropic

_SYSTEM_PROMPT = """\
You are an expert hardware verification engineer. Your task is to write \
a cocotb testbench in Python for the given SystemVerilog RTL module.

Rules:
- Output ONLY valid Python code. No markdown fences, no explanation.
- Import only: cocotb, cocotb.triggers, cocotb.clock
- The test function must be decorated with @cocotb.test()
- Drive signals by setting dut.<signal>.value = <int>
- Use RisingEdge(dut.clk) for clock synchronization
- Use Timer(N, unit="ns") only for reset sequences
- Always initialize and deassert reset before testing
"""


class LLMClient:
    def __init__(self) -> None:
        self._client = AsyncAnthropic()

    async def generate(self, rtl_context: str, task_prompt: str) -> str:
        response = await self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": rtl_context,
                            "cache_control": {"type": "ephemeral"},
                        },
                        {
                            "type": "text",
                            "text": task_prompt,
                        },
                    ],
                }
            ],
        )
        return response.content[0].text.strip()
