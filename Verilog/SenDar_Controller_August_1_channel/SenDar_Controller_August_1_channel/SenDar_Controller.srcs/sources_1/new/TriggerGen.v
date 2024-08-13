`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/27/2024 02:31:16 PM
// Design Name: 
// Module Name: TriggerGen
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

module TriggerGen 
#(
    parameter ARRAY_LENGTH = 8_800,
    parameter HIGH_SAMPLES = 8_000,
    parameter CLK_FREQ = 80_000_000,
    parameter COUNTER_WIDTH = 32
) (
    input wire clk, // Clock signal
    input wire reset, // Synchronous reset
    input wire count_enable,
    output wire trigger // 11-bit counter output
);
    reg [COUNTER_WIDTH - 1:0] counter;
    //reg count_enable_delayed;
    always @(posedge clk) begin
        if (reset) // Synchronous reset
            counter <= 0;
        else 
            counter <= (count_enable && counter < ARRAY_LENGTH - 1)? counter + 1 : 0;
    end
    
    assign trigger = count_enable & (counter < HIGH_SAMPLES);
    
endmodule
