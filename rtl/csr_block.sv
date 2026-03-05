module csr_block (
    input  logic        clk,
    input  logic        rst_n,
    input  logic [7:0]  addr,
    input  logic [31:0] wdata,
    input  logic        we,
    input  logic        re,
    output logic [31:0] rdata,
    output logic [2:0]  ctrl_reg,
    output logic [31:0] baud_div_reg,
    input  logic [3:0]  status_in
);
    // Kaydedilen veriler (Internal Registers)
    logic [2:0]  ctrl_q; // sistemin açık/kapalı olması, veri okunması veya veri yazılması
    logic [31:0] baud_div_q; // hız ayarı

    assign ctrl_reg     = ctrl_q;
    assign baud_div_reg = baud_div_q;

    // Yazma Mantığı
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            ctrl_q     <= 3'b0; // UART, TX ve RX devre dışı
            baud_div_q <= 32'hD8; // haberleşme hızı varsayılan değer
        end else if (we) begin // write enable
            case (addr)
                8'h04: ctrl_q     <= wdata[2:0]; //eğer adres 0x04 ise cpu dan gelen verinin son üç bitini al ve ctrl içine koy
                8'h08: baud_div_q <= wdata; // Eğer adres 0x08 ise, 32 bitin tamamını al ve hız ayarı içine koy
                default: ; // Diğerleri Read-Only
            endcase
        end
    end

    // Okuma Mantığı
    always_comb begin //combinational, saat sinyali beklenmiyor
        rdata = 32'h0;  // veri yolunda gürültü kalmasın diye çıkışı her zaman sıfıra çekiyoruz
        if (re) begin  // read enable
            case (addr)
                8'h00: rdata = 32'hA1C0_0001; // ID
                8'h04: rdata = {29'b0, ctrl_q}; // ctrl_q içinde 3 bit var, sol tarafına 29 tane sıfır ekledik "Zero Padding"
                8'h08: rdata = baud_div_q; 
                8'h0C: rdata = {28'b0, status_in};  // state registerı 4 bit olduğu için 28 tane sıfır koyduk
                default: rdata = 32'hDEAD_BEEF; // cpu saçma bir adres okumaya kalkarsa DEAD_BEEF görür
            endcase
        end
    end
endmodule