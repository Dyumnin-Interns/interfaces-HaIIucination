// Generated by Bluespec Compiler (build d05342e3)
//
// On Tue Oct 11 09:42:23 IST 2022
//
//
// Ports:
// Name                         I/O  size props
// write_rdy                      O     1 const
// read_data                      O     1
// read_rdy                       O     1 const
// CLK                            I     1 clock
// RST_N                          I     1 reset
// write_address                  I     3
// write_data                     I     1 reg
// read_address                   I     3
// write_en                       I     1
// read_en                        I     1
//
// Combinational paths from inputs to outputs:
//   read_address -> read_data
//
//
module test (
    CLK,
    RST_N,

    write_address,
    write_data,
    write_en,
    write_rdy,

    read_address,
    read_en,
    read_data,
    read_rdy
);
  output reg CLK;
  input RST_N;

  // action method write
  input [2 : 0] write_address;
  input write_data;
  input write_en;
  output write_rdy;

  // actionvalue method read
  input [2 : 0] read_address;
  input read_en;
  output read_data;
  output read_rdy;

  dut dut_test(
      .CLK  (CLK),
      .RST_N(RST_N),

      .write_address(write_address),
      .write_data(write_data),
      .write_en(write_en),
      .write_rdy(write_rdy),

      .read_address(read_address),
      .read_en(read_en),
      .read_data(read_data),
      .read_rdy(read_rdy)
  );

  initial begin
    $dumpfile("wave.vcd");
    $dumpvars;
    CLK = 0;
    forever begin
      #5 CLK = ~CLK;
    end
  end
endmodule
