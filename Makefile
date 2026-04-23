# --- Makefile ---
SIM ?= verilator
TOPLEVEL_LANG ?= verilog
COMPILE_ARGS += --coverage

# Projedeki tüm RTL dosyalarını buraya ekliyoruz
VERILOG_SOURCES += $(PWD)/rtl/fifo.sv
VERILOG_SOURCES += $(PWD)/rtl/csr_block.sv
VERILOG_SOURCES += $(PWD)/rtl/uart_tx.sv
VERILOG_SOURCES += $(PWD)/rtl/uart_top.sv
VERILOG_SOURCES += $(PWD)/rtl/uart_rx.sv

# Test edilecek en üst modül (Top Module)
TOPLEVEL = uart_top

# Varsayılan olarak çalışacak test dosyası
MODULE = tests.test_uart_tx

# Cocotb Makefile kütüphanesini dahil et
include $(shell cocotb-config --makefiles)/Makefile.sim

smoke:
	make sim MODULE=tests.test_smoke

csr:
	make sim MODULE=tests.test_csr

fifo:
	make sim MODULE=tests.test_fifo

tx: 
	make sim MODULE=tests.test_uart_tx

rx:
	make sim MODULE=tests.test_uart_rx TOPLEVEL=uart_rx