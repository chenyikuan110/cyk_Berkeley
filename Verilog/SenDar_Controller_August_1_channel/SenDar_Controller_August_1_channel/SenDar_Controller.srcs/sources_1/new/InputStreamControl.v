`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/14/2024 04:14:16 PM
// Design Name: 
// Module Name: InputStreamControl
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

module InputStreamControl 
#(
    parameter DOWNSAMPLING_FACTOR = 8,
    parameter MAX_COUNT = 1100,
    parameter ARRAY_LENGTH = 1000,
    parameter COUNTER_WIDTH = 11
) (
    input wire clk, // Clock signal
    input wire reset, // Synchronous reset
    input wire downsample_enable,
    input wire count_enable,
    output wire shift_enable // 11-bit counter output
);
    reg [COUNTER_WIDTH - 1:0] counter;
    wire [COUNTER_WIDTH - 1:0] max_count_val, array_length_val;
    assign max_count_val = downsample_enable? MAX_COUNT * DOWNSAMPLING_FACTOR : MAX_COUNT;
    assign array_length_val = downsample_enable? ARRAY_LENGTH * DOWNSAMPLING_FACTOR : ARRAY_LENGTH;
    
//    reg count_enable_delayed;
    always @(posedge clk) begin
        if (reset) // Synchronous reset
            counter <= 0;
        else 
            counter <= (count_enable && counter < max_count_val-1)? counter + 1 : 0;
    end
    
//    always @(posedge clk) begin
//        count_enable_delayed <= count_enable; // one cycle latency compared to the mem
//    end
    // Assert output when counter is less than ARRAY_LENGTH
    reg shift_enable_delayed;
    always @(posedge clk) begin
        shift_enable_delayed <=  (count_enable & counter < array_length_val);
    end
    assign shift_enable = downsample_enable? shift_enable_delayed : (count_enable & counter < array_length_val);
endmodule

