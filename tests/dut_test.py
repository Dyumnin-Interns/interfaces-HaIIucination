import os
from random import randint
import cocotb
from cocotb.triggers import NextTimeStep, Timer, RisingEdge, ReadOnly
from cocotb_bus.drivers import BusDriver, Driver
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db


class writeValue:
    def __init__(self, address, data, en=1):
        self.address = address
        self.data = data
        self.en = en


class readValue:
    def __init__(self, address, en):
        self.address = address
        self.en = en


def sb_fn(actual_value):
    global expected_value
    e = expected_value.pop()
    print("expected = ", e, "\n actual = ", actual_value)
    assert actual_value == e, f"Sb Matching FAILED"


@CoverPoint("top.add", xf=lambda x, y: x, bins=[4, 5])
@CoverPoint("top.data", xf=lambda x, y: y, bins=[0, 1])
@CoverCross("top.cross.ab", items=["top.add", "top.data"])
def covert(write_add, write_data):
    pass

@CoverPoint("top.read_address", xf = lambda x:x, bins=[0, 1, 2, 3])
def ra_cover(read_address):
    pass

class writeDriver(BusDriver):
    _signals = ["write_rdy", "write_en", "write_data", "write_address"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.write_en.value = 0
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        if self.bus.write_rdy.value != 1:
            await RisingEdge(self.bus.write_rdy)
        self.bus.write_en = 1
        self.bus.write_address.value = value.address
        self.bus.write_data.value = value.data
        await ReadOnly()
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.write_en = 0


class readDriver(BusDriver):
    _signals = ["read_rdy", "read_en", "read_data", "read_address"]

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.read_en.value = 0
        self.clk = clk

    async def _driver_send(self, value, sync=True):
        if self.bus.read_rdy.value != 1:
            await RisingEdge(self.bus.read_rdy)
        self.bus.read_en = 1
        self.bus.read_address.value = value.address
        await ReadOnly()
        await RisingEdge(self.clk)
        await NextTimeStep()
        self.bus.read_en = 0


class outputDriver(BusDriver):
    _signals = ["read_rdy", "read_en", "read_data", "read_address"]

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.clk = clk
        self.callback = sb_callback

    async def _driver_send(self, value, sync=True):
        while 1:
            if self.bus.read_rdy.value != 1:
                await RisingEdge(self.bus.read_rdy)
            self.bus.read_en.value = 1
            await ReadOnly()
            self.callback(int(self.bus.read_data.value))
            await RisingEdge(self.clk)
            await NextTimeStep()
            self.bus.read_en.value = 0


@cocotb.test
async def dut_test(dut):
    global expected_value
    # Reset
    dut.RST_N.value = 1
    await Timer(20, "ns")
    dut.RST_N.value = 0
    await Timer(20, "ns")
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1

    expected_value = []
    idriver = writeDriver(dut, "", dut.CLK)
    rdriver = readDriver(dut, "", dut.CLK)
    outputDriver(dut, "", dut.CLK, sb_fn)

    for i in range(200):
        data = randint(0, 1)
        add = randint(4, 5)
        value = writeValue(address=add, data=data)

        idriver.append(value)

        expected_value.append(data)
        ra = randint(0, 3)
        rvalue = readValue(address=ra, en=1)
        rdriver.append(rvalue)

        covert(add, data)
        ra_cover(ra)


    await Timer(len(expected_value) * 5, "ns")

    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(os.getenv("RESULT_PATH", "./"), "coverage.xml")
    coverage_db.export_to_xml(filename=coverage_file)
