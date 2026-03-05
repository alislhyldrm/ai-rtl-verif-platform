# Proje Ayarları
SIM ?= verilator
TOPLEVEL_LANG ?= verilog

# RTL Dosyaları
VERILOG_SOURCES += $(PWD)/rtl/csr_block.sv
VERILOG_SOURCES += $(PWD)/rtl/uart_top.sv
VERILOG_SOURCES += $(PWD)/rtl/fifo.sv

# Üst Seviye Modül Adı (RTL'deki module ismi)
TOPLEVEL = uart_top

# Test Dosyası (tests/test_csr.py -> test_csr)
MODULE = tests.test_fifo

# Cocotb'nin kendi kurallarını dahil et
include $(shell cocotb-config --makefiles)/Makefile.sim

# Temizlik komutu
clean_all:
	rm -rf sim_build/ __pycache__ tests/__pycache__
	rm -f results.xml