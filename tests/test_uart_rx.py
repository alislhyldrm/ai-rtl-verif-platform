import cocotb
from cocotb.triggers import RisingEdge, Timer, with_timeout
from cocotb.clock import Clock

async def uart_tx_golden_model(dut, baud_div, data_byte):
    # 1 baud periyodu kadar bekleme fonksiyonu
    async def wait_baud():
        for _ in range(baud_div):
            await RisingEdge(dut.clk)

    dut._log.info(f"Golden Model veri gonderiyor: {hex(data_byte)}")
    
    # START biti (0)
    dut.rx.value = 0
    await wait_baud()

    # 8 adet DATA biti (En dusuk anlamli bitten baslayarak)
    for i in range(8):
        bit_val = (data_byte >> i) & 1
        dut.rx.value = bit_val
        await wait_baud()

    # STOP biti (1)
    dut.rx.value = 1
    await wait_baud()

@cocotb.test()
async def test_uart_rx_receive(dut):
    cocotb.start_soon(Clock(dut.clk, 20, unit="ns").start())

    # Baslangic durumlari
    dut.rx.value = 1
    dut.rst_n.value = 0
    dut.baud_div.value = 10
    await Timer(50, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    test_byte = 0xCA
    sim_baud = 10

    # Golden model ile veriyi pin uzerinden gonder
    # Bu islemi arka planda baslatiyoruz (start_soon)
    cocotb.start_soon(uart_tx_golden_model(dut, sim_baud, test_byte))

    # Veri alindiktan sonra rx_valid sinyalinin yukselen kenarini bekle
    # Zaman asimi (timeout) korumasi ekleyerek sonsuz donguyu engelliyoruz
    await with_timeout(RisingEdge(dut.rx_valid), 2000, 'ns')
    
    assert int(dut.rx_data.value) == test_byte, f"HATA: Beklenen {hex(test_byte)} Alinan {hex(int(dut.rx_data.value))}"
    dut._log.info("TEBRIKLER: Alinan veri dogru ve rx_valid basariyla tetiklendi!")