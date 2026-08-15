module lab_counter (
    input clk,
    input rst,
    input [3:0] sw,
    output [3:0] led,
    output [6:0] seg0,
    output lcd_en
);

reg [3:0] counter;
reg [6:0] seg_pattern;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        counter <= 4'b0000;
    end else if (sw[0]) begin
        counter <= counter + 1;
    end else begin
        counter <= counter;
    end
end

always @(*) begin
    case (counter)
        4'd0: seg_pattern = 7'b1000000;
        4'd1: seg_pattern = 7'b1111001;
        default: seg_pattern = 7'b0000110;
    endcase
end

assign led = counter;
assign seg0 = seg_pattern;
assign lcd_en = sw[3];

endmodule