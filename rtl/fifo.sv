module fifo #(
    parameter int DEPTH = 16,
    parameter int WIDTH = 8
) (
    input  logic             clk,
    input  logic             rst_n,
    input  logic             wr_en,
    input  logic [WIDTH-1:0] din,
    input  logic             rd_en,
    output logic [WIDTH-1:0] dout,
    output logic             full,
    output logic             empty
);

    logic [WIDTH-1:0] mem [DEPTH];
    logic [$clog2(DEPTH)-1:0] wr_ptr, rd_ptr;
    logic [$clog2(DEPTH):0]   count;

    assign full = (count == ($bits(count))'(DEPTH));
    assign empty = (count == 0);
    assign dout  = mem[rd_ptr];

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            count  <= 0;
        end else begin
            case ({wr_en && !full, rd_en && !empty})
                2'b10: begin // Sadece Yazma
                    mem[wr_ptr] <= din;
                    wr_ptr      <= wr_ptr + 1;
                    count       <= count + 1;
                end
                2'b01: begin // Sadece Okuma
                    rd_ptr <= rd_ptr + 1;
                    count  <= count - 1;
                end
                2'b11: begin // Aynı Anda Okuma ve Yazma
                    mem[wr_ptr] <= din;
                    wr_ptr      <= wr_ptr + 1;
                    rd_ptr      <= rd_ptr + 1;
                    // Giriş ve çıkış olduğu için count değişmez
                end
                default: ; 
            endcase
        end
    end
endmodule