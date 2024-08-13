`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/25/2024 03:17:05 PM
// Design Name: 
// Module Name: VariableGainBuffer
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
/*
    Simple variable gain buffer with 10 bit gain control
    First draft: March 5 2024
*/
module VariableGainBuffer (
    input wire [15:0] data_in, // 16-bit input data
    //input wire clk,
    input wire enable,         // if enabled, lateny will be 1; if disabled, latency will be 0
    input wire [16:0] gain,     // 16-bit signed gain coefficient, normalized to 1 (i.e. output will left shift by 16 bits)
    output wire [15:0] data_out // 16-bit signed output data
);
    wire [31:0] out_buffer; // Internal buffer to store data
//    wire [16:0] data_in_sext, gain_sext;
//    assign data_in_sext = {data_in[15],data_in[15:0]};
//    assign gain_sext = {gain[15], gain[15:0]};
    mult_gen_0 mult_inst(
         .A(data_in)
        ,.B(gain)
        ,.P(out_buffer)
    );

    assign data_out = (enable)? out_buffer[30:15] : data_in;

endmodule
