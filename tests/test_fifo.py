import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_fifo_fill(dut):
    """FIFO'yu doldurma ve FULL bayrağını test etme"""
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    # Reset (Daha uzun ve garanti reset)
    dut.rst_n.value = 0
    await Timer(50, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut._log.info("--- FIFO Yazma Islemi Basliyor ---")
    for i in range(16):
        dut.addr.value = 0x10
        dut.wdata.value = i
        dut.we.value = 1
        await RisingEdge(dut.clk)
        # Her yazmada FIFO'nun içindeki sayacı kontrol edelim (Debug)
        cnt = int(dut.i_tx_fifo.count.value)
        dut._log.info(f"Yazildi: {i}, FIFO Sayaci: {cnt}")
    
    dut.we.value = 0
    await RisingEdge(dut.clk)

    # Durum oku (0x0C)
    dut.addr.value = 0x0C
    dut.re.value = 1
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")
    
    status_val = int(dut.rdata.value)
    # CSR içindeki status_in sinyalini de doğrudan kontrol edelim
    stat_in = int(dut.i_csr.status_in.value)
    
    dut._log.info(f"DEBUG: CSR status_in sinyali: {bin(stat_in)}")
    dut._log.info(f"OKUNAN: Status Register (rdata): {bin(status_val)}")
    
    assert (status_val & 0x2), f"HATA: Full biti yanmadi! Okunan: {bin(status_val)}"
    dut._log.info("TEBRIKLER: FIFO Full testi basariyla gecti!")