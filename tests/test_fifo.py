import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_fifo_fill(dut):
    """FIFO'yu doldurma ve FULL bayrağını test etme"""
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    dut.rst_n.value = 0
    await Timer(10, units="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # FIFO 16 derinlikte olduğu için 16 kez veri yazalım
    for i in range(16):
        dut.addr.value = 0x10 # Veri register adresi
        dut.wdata.value = i
        dut.we.value = 1
        await RisingEdge(dut.clk)
    
    dut.we.value = 0
    await RisingEdge(dut.clk)

    # Status register'ı oku (0x0C) ve FULL bitini (bit 1) kontrol et
    dut.addr.value = 0x0C
    dut.re.value = 1
    await RisingEdge(dut.clk)
    
    status_val = dut.rdata.value
    dut._log.info(f"Status Register: {bin(status_val)}")
    
    # 0x0C adresinde bit 1 'tx_fifo_full' olarak tanımlanmıştı
    assert (status_val & 0x2), "Hata: FIFO dolu olmasına rağmen FULL bayrağı yanmadı!"