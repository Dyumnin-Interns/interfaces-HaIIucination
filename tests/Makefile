SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO1.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/wrappers/test.v
assin2:
	rm -rf sim_build
	$(MAKE) sim TOPLEVEL=test MODULE=dut_test

include $(shell cocotb-config --makefiles)/Makefile.sim
