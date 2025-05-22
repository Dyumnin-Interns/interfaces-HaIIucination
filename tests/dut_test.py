import os
from random import randint
import cocotb
from cocotb.triggers import NextTimeStep, Timer, RisingEdge, ReadOnly
from cocotb_bus.drivers import BusDriver, Driver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db


class writeValue:
    def __init__(self, address, data, en):
        self.address = address
        self.data = data
        self.en = en

class readValue:
    def __init__(self, address, en):
        self.address = address
        self.en = en

def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value.pop(0), "Sb Matching FAILED"

'''
@CoverPoint("top.write_en",
            xf = lambda x, y: x,
            bins = [0, 1]
            )
@CoverPoint("top.write_data",
            xf = lambda x, y: x,
            bins = [0, 1]
            )
@CoverPoint("top.write_address",
            xf = lambda x, y: x,
            bins = list(range(0,8))
            )

@CoverPoint("top.read_en",
            xf = lambda x, y: x,
            bins = [0, 1]
            )
@CoverPoint("top.read_address",
            xf = lambda x, y: x,
            bins = list(range(0,8))
            )
'''

class readDriver(BusDriver):
    _signals = ["read_rdy", "read_en", "read_data", "read_address"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.read_en.value = 0
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        if self.bus.read_rdy.value != 1:
            await RisingEdge(self.bus.read_rdy)
        self.bus.read_en.value = value.en
        self.bus.read_address.value = value.address
        await ReadOnly()
        await RisingEdge(self.clk)
        await NextTimeStep()
        #self.bus.write_en = 0

class writeDriver(BusDriver):
    _signals = ["write_rdy", "write_en", "write_data", "write_address"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.write_en.value = 0
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        if self.bus.write_rdy.value != 1:
            await RisingEdge(self.bus.write_rdy)
        self.bus.write_en.value = value.en
        self.bus.write_data.value = value.data
        self.bus.write_address.value = value.address
        await ReadOnly()
        await RisingEdge(self.clk)
        await NextTimeStep()
        #self.bus.write_en = 0

class outputDriver(BusDriver):
    _signals = ["read_rdy", "read_en", "read_data", "read_address"]
    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.clk = clk
        self.callback = sb_callback

    async def _driver_send(self, value, sync=True):
        while True:
            if self.bus.read_rdy.value != 1:
                await RisingEdge(self.bus.read_rdy)
            self.bus.read_en.value = 1
            await ReadOnly()
            self.callback(self.bus.read_data.value)
            await RisingEdge(self.clk)
            await NextTimeStep()
            self.bus.read_en.value = 0
    


@cocotb.test
async def dut_test(dut):
    global expected_value
    # Reset
    dut.RST_N.value = 1
    await Timer(20, 'ns')
    dut.RST_N.value = 0
    await Timer(20, 'ns')
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1

    expected_value = []
    wdriver = writeDriver(dut, "", dut.CLK)
    rdriver = readDriver(dut, "", dut.CLK)
    rvalue = readValue(address=None, en=None)
    odriver = outputDriver(dut, "read_data", dut.CLK, sb_fn)
    odriver.append(rvalue)


    for i in range(20):
        add = randint(0, 8)
        data = randint(0, 1)
        en = randint(0, 1)
        expected_value.append(data)
        wvalue = writeValue(address=add, data=data, en=en)
        rvalue = readValue(address=add, en=en)

        wdriver.append(wvalue)
        rdriver.append(rvalue)

    #coverage_db.report_coverage(cocotb.log.info, bins=True)
    #coverage_file = os.path.join(
            #os.getenv('RESULT_PATH', "./"), 'coverage.xml')
    #coverage_db.export_to_xml(filename=coverage_file)
