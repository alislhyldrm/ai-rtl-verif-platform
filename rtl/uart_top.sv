module uart_top (
  input  logic        clk,
  input  logic        rst_n,

  // Simple MMIO bus
  input  logic [7:0]  addr,
  input  logic [31:0] wdata,
  input  logic        we,
  input  logic        re,
  output logic [31:0] rdata,
  output logic        ready
);

  localparam logic [31:0] ID_VALUE = 32'hA1C0_0001;

  always_comb begin
    ready = (we | re);
    rdata = 32'h0;

    if (re) begin
      unique case (addr)
        8'h00: rdata = ID_VALUE;
        default: rdata = 32'h0;
      endcase
    end
  end

endmodule