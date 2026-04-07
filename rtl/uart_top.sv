module uart_top (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  addr,
    input  logic [31:0] wdata,
    input  logic        we,
    input  logic        re,
    output logic [31:0] rdata,
    output logic        ready,
    output logic        tx
);

    logic [2:0]  ctrl_reg;
    logic [31:0] baud_div_reg;
    logic        tx_fifo_full, tx_fifo_empty;
    logic [7:0]  tx_data_out;
    logic        tx_fifo_rd_en;
    logic        tx_busy;

    assign ready = 1'b1;

    // Adres 0x10'a yazılırsa TX FIFO'ya git
    logic tx_wr_en;
    assign tx_wr_en = (we && (addr == 8'h10));

    // UART Enable Kontrolü: ctrl_reg'in 0. biti 1 ise UART çalışır
    logic uart_en;
    assign uart_en = ctrl_reg[0];

    csr_block i_csr (
        .clk, .rst_n, .addr, .wdata, .we, .re, .rdata,
        .ctrl_reg,
        .baud_div_reg,
        .status_in({2'b0, tx_fifo_full, tx_fifo_empty})
    );

    fifo #(.DEPTH(16), .WIDTH(8)) i_tx_fifo (
        .clk,
        .rst_n,
        .wr_en  (tx_wr_en),
        .din    (wdata[7:0]),
        .rd_en  (tx_fifo_rd_en && uart_en), // UART kapalıysa FIFO'dan veri çekilemez!
        .dout   (tx_data_out),
        .full   (tx_fifo_full),
        .empty  (tx_fifo_empty)
    );

    uart_tx i_uart_tx (
        .clk,
        .rst_n,
        .baud_div   (baud_div_reg),
        .fifo_empty (tx_fifo_empty || !uart_en), // UART kapalıysa FIFO'yu hep boş görür (başlamaz)
        .fifo_data  (tx_data_out),
        .fifo_rd_en (tx_fifo_rd_en),
        .tx         (tx),
        .tx_busy    (tx_busy)
    );

endmodule