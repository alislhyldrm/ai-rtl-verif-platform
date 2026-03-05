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

    assign full  = (count == $bits(count)'(DEPTH)); // DEPTH'i count'un bit genişliğine zorla
    assign empty = (count == $bits(count)'(0));     // 0'ı count'un bit genişliğine zorla

    // Yazma ve Okuma İşaretçileri (Geliştirilmiş Mantık)
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
                    dout        <= mem[rd_ptr];
                    rd_ptr      <= rd_ptr + 1;
                    count       <= count - 1;
                end
                2'b11: begin // Aynı Anda Yazma ve Okuma
                    mem[wr_ptr] <= din;
                    dout        <= mem[rd_ptr];
                    wr_ptr      <= wr_ptr + 1;
                    rd_ptr      <= rd_ptr + 1;
                    // count değişmez, çünkü 1 eklendi ve 1 çıkarıldı
                end
                default: ; // İşlem yok
            endcase
        end
    end
    
endmodule