module uart_tx (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [31:0] baud_div,
    input  logic        fifo_empty,
    input  logic [7:0]  fifo_data,
    output logic        fifo_rd_en,
    output logic        tx,
    output logic        tx_busy
);

    typedef enum logic [1:0] {
        IDLE  = 2'b00,
        START = 2'b01,
        DATA  = 2'b10,
        STOP  = 2'b11
    } state_e;

    state_e state_q, state_d;
    logic [31:0] baud_cnt_q;
    logic [2:0]  bit_cnt_q;
    logic [7:0]  tx_data_q;

    logic baud_tick;
    assign baud_tick = (baud_cnt_q == (baud_div - 1));

    // Sirali Mantik (Sequential Logic)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            baud_cnt_q <= 0;
            bit_cnt_q  <= 0;
            tx_data_q  <= 8'b0;
            state_q    <= IDLE;
        end else begin
            state_q <= state_d;

            // FIFO icinden veri okundugunda veriyi iceriye kaydet
            if (fifo_rd_en) begin
                tx_data_q <= fifo_data;
            end

            // Baud sayaci ve bit sayaci yonetimi
            if (state_q != IDLE) begin
                if (baud_tick) begin
                    baud_cnt_q <= 0;
                    if (state_q == DATA) begin
                        bit_cnt_q <= bit_cnt_q + 1;
                    end else if (state_q == STOP) begin
                        bit_cnt_q <= 0;
                    end
                end else begin
                    baud_cnt_q <= baud_cnt_q + 1;
                end
            end else begin
                baud_cnt_q <= 0;
                bit_cnt_q  <= 0;
            end
        end
    end

    // Birlesik Mantik (Combinational FSM Logic)
    always_comb begin
        state_d    = state_q;
        fifo_rd_en = 1'b0;
        tx         = 1'b1;
        tx_busy    = 1'b1;

        case (state_q)
            IDLE: begin
                tx_busy = 1'b0;
                if (!fifo_empty) begin
                    state_d = START;
                    fifo_rd_en = 1'b1; 
                end
            end
            START: begin
                tx = 1'b0; 
                if (baud_tick) begin
                    state_d = DATA;
                end
            end
            DATA: begin
                tx = tx_data_q[bit_cnt_q]; 
                if (baud_tick && bit_cnt_q == 3'd7) begin
                    state_d = STOP;
                end
            end
            STOP: begin
                tx = 1'b1; 
                if (baud_tick) begin
                    state_d = IDLE;
                end
            end
            default: state_d = IDLE;
        endcase
    end
endmodule