import cocotb
from cocotb.triggers import Timer

@cocotb.test()
async def test_placeholder(dut):
    """Basit bir smoke test, sistemin derlenebildiğini doğrular."""
    await Timer(10, units="ns")
    assert True