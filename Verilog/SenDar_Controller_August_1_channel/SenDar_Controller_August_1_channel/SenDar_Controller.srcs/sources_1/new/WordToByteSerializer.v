`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/15/2024 02:12:13 PM
// Design Name: 
// Module Name: WordToByteSerializer
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module WordToByteSerializer(
   input wire clk,
   input wire reset,
   input wire enable,
   input wire [31:0] data_in,
   output wire [7:0] data_out
);

// count: 0, 1, 2, 3, 0, ... (wraps automatically)
reg [1:0] count;
reg [7:0] data_out_reg;
always @(posedge clk) begin
    if(reset)
        count <= 0;
    else if(enable)
        count <= count + 1;
end

always @(posedge clk) begin
    if(reset)
        data_out_reg <= 0;
    else if(enable)begin
        case(count)
            2'd0: data_out_reg <= data_in[7:0];
            2'd1: data_out_reg <= data_in[15:8];
            2'd2: data_out_reg <= data_in[23:16];
            2'd3: data_out_reg <= data_in[31:24];
        endcase
    end
end

assign data_out = data_out_reg;

endmodule