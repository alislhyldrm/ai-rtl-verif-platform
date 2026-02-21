import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_csr_registers_full(dut):
    """Bütün CSR register haritasını (RW/RO) test eder"""
    
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    # 1. Reset
    dut.rst_n.value = 0
    await Timer(10, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 2. BAUD_DIV Testi (Yaz ve Geri Oku)
    dut._log.info("BAUD_DIV test ediliyor...")
    dut.addr.value = 0x08
    dut.wdata.value = 0x1234
    dut.we.value = 1
    await RisingEdge(dut.clk)
    dut.we.value = 0
    
    dut.re.value = 1
    await RisingEdge(dut.clk)
    assert dut.rdata.value == 0x1234
    dut.re.value = 0

    # 3. CTRL Testi (Sadece alt 3 bit yazılabilir)
    dut._log.info("CTRL test ediliyor...")
    dut.addr.value = 0x04
    dut.wdata.value = 0x7  # UART_EN, TX_EN, RX_EN
    dut.we.value = 1
    await RisingEdge(dut.clk)
    dut.we.value = 0
    
    dut.re.value = 1
    await RisingEdge(dut.clk)
    assert dut.rdata.value == 0x7
    dut.re.value = 0

    # 4. STATUS Testi
    dut._log.info("STATUS gercek donanim kontrol ediliyor...")
    dut.addr.value = 0x0C
    dut.re.value = 1
    await RisingEdge(dut.clk)
    assert dut.rdata.value == 0x1
    
    dut._log.info("Tüm CSR testleri başarıyla tamamlandı!")