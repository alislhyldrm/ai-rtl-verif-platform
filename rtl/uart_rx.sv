module uart_rx (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [31:0] baud_div,
    input  logic        rx,
    output logic [7:0]  rx_data,
    output logic        rx_valid,
    output logic        frame_err
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
    logic [7:0]  rx_data_q;

    // RX sinyali icin cift flip flop senkronizasyonu
    logic rx_sync_1, rx_sync_2;
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_sync_1 <= 1'b1;
            rx_sync_2 <= 1'b1;
        end else begin
            rx_sync_1 <= rx;
            rx_sync_2 <= rx_sync_1;
        end
    end

    // Sirali Mantik (Sequential Logic)
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state_q     <= IDLE;
            baud_cnt_q  <= 0;
            bit_cnt_q   <= 0;
            rx_data_q   <= 8'b0;
            rx_valid    <= 1'b0;
            frame_err   <= 1'b0;
        end else begin
            state_q <= state_d;
            
            // Varsayilan olarak valid ve error sinyalleri 1 saat vurusunda kalir
            rx_valid  <= 1'b0;
            frame_err <= 1'b0;

            case (state_q)
                IDLE: begin
                    baud_cnt_q <= 0;
                    bit_cnt_q  <= 0;
                end
                START: begin
                    if (baud_cnt_q == (baud_div >> 1)) begin
                        baud_cnt_q <= 0;
                    end else begin
                        baud_cnt_q <= baud_cnt_q + 1;
                    end
                end
                DATA: begin
                    if (baud_cnt_q == (baud_div - 1)) begin
                        baud_cnt_q <= 0;
                        rx_data_q[bit_cnt_q] <= rx_sync_2;
                        bit_cnt_q <= bit_cnt_q + 1;
                    end else begin
                        baud_cnt_q <= baud_cnt_q + 1;
                    end
                end
                STOP: begin
                    if (baud_cnt_q == (baud_div - 1)) begin
                        baud_cnt_q <= 0;
                        if (rx_sync_2 == 1'b1) begin
                            rx_valid <= 1'b1;
                        end else begin
                            frame_err <= 1'b1;
                        end
                    end else begin
                        baud_cnt_q <= baud_cnt_q + 1;
                    end
                end
            endcase
        end
    end

    // Birlesik Mantik (Combinational FSM Logic)
    always_comb begin
        state_d = state_q;

        case (state_q)
            IDLE: begin
                // Hat 0 degerine duserse START durumuna gec
                if (rx_sync_2 == 1'b0) begin
                    state_d = START;
                end
            end
            START: begin
                // Baud periyodunun yarisinda hatta tekrar bak
                if (baud_cnt_q == (baud_div >> 1)) begin
                    if (rx_sync_2 == 1'b0) begin
                        state_d = DATA; 
                    end else begin
                        state_d = IDLE; 
                    end
                end
            end
            DATA: begin
                // Sekiz biti tamamlayinca STOP durumuna gec
                if (baud_cnt_q == (baud_div - 1) && bit_cnt_q == 3'd7) begin
                    state_d = STOP;
                end
            end
            STOP: begin
                // Stop bitinin sonunda IDLE durumuna don
                if (baud_cnt_q == (baud_div - 1)) begin
                    state_d = IDLE;
                end
            end
            default: state_d = IDLE;
        endcase
    end

    assign rx_data = rx_data_q;

endmodule