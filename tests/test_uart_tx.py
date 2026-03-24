import cocotb
from cocotb.triggers import RisingEdge, Timer, FallingEdge
from cocotb.clock import Clock

async def uart_rx_golden_model(dut, baud_div, expected_data):
    # Baslangic durumu tx pini 1 olmali
    if dut.tx.value != 1:
        await RisingEdge(dut.tx)

    # START bitini yakala tx pininin 0 olmasi
    await FallingEdge(dut.tx)
    dut._log.info("START biti yakalandi.")

    # 1. ADIM: START bitinin tam ortasina (merkezine) git
    for _ in range(baud_div // 2):
        await RisingEdge(dut.clk)

    # 2. ADIM: Ilk data bitinin (Bit 0) ortasina ulasmak icin tam 1 baud bekle
    for _ in range(baud_div):
        await RisingEdge(dut.clk)

    # 8 adet Data bitini oku LSB first (Artik hep bitlerin ortasindayiz)
    received_val = 0
    for i in range(8):
        bit_val = int(dut.tx.value)
        received_val |= (bit_val << i)
        dut._log.info(f"Bit {i} okundu: {bit_val}")
        
        # Bir sonraki bitin ortasina git
        for _ in range(baud_div):
            await RisingEdge(dut.clk)

    # STOP bitini kontrol et
    stop_bit = int(dut.tx.value)
    dut._log.info(f"STOP biti okundu: {stop_bit}")
    assert stop_bit == 1, "HATA: STOP biti 1 degil"

    # Alinan veriyi beklenen ile karsilastir
    assert received_val == expected_data, f"HATA: Beklenen {hex(expected_data)} Alinan {hex(received_val)}"
    dut._log.info(f"TEBRIKLER: Veri basariyla iletildi: {hex(received_val)}")

@cocotb.test()
async def test_uart_tx_transfer(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    dut.rst_n.value = 0
    await Timer(50, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    sim_baud = 10

    # BAUD_DIV ayarla
    dut.addr.value = 0x08
    dut.wdata.value = sim_baud
    dut.we.value = 1
    await RisingEdge(dut.clk)

    # UART aktif et CTRL register
    dut.addr.value = 0x04
    dut.wdata.value = 0x1
    dut.we.value = 1
    await RisingEdge(dut.clk)

    # TX FIFO icine veri yaz Adres 0x10
    test_byte = 0xA5
    dut.addr.value = 0x10
    dut.wdata.value = test_byte
    dut.we.value = 1
    await RisingEdge(dut.clk)
    
    dut.we.value = 0

    # Golden modelin veriyi okuyup test etmesi
    await uart_rx_golden_model(dut, sim_baud, test_byte)