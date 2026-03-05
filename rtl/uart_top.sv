module uart_top (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  addr,
    input  logic [31:0] wdata,
    input  logic        we,
    input  logic        re,
    output logic [31:0] rdata,
    output logic        ready
);

    logic [2:0]  ctrl_reg;
    logic [31:0] baud_div_reg;
    logic        tx_fifo_full, tx_fifo_empty;
    logic [7:0]  tx_data_out;

    assign ready = 1'b1;

    // Yazma sinyali sadece veri register'ına (örneğin 0x10) gelirse FIFO'ya gider
    logic tx_wr_en;
    assign tx_wr_en = (we && (addr == 8'h10)); 

    csr_block i_csr (
        .clk, .rst_n, .addr, .wdata, .we, .re, .rdata,
        .ctrl_reg,
        .baud_div_reg,
        .status_in({2'b0, tx_fifo_full, tx_fifo_empty})
    );

    fifo #(.DEPTH(16), .WIDTH(8)) i_tx_fifo (
        .clk,
        .rst_n,
        .wr_en(tx_wr_en),
        .din(wdata[7:0]),
        .rd_en(1'b0), // Milestone 3'te UART Engine bağlayacak
        .dout(tx_data_out),
        .full(tx_fifo_full),
        .empty(tx_fifo_empty)
    );

endmodule