`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/15/2024 01:32:43 PM
// Design Name: 
// Module Name: ArrayAverager
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
    Takes a 1000-sample arrays (one chirp) every time the "data valid" input is raised, 
    this code accumulates 10 chirps and produce the averaged chirp 
    First draft: Feb 28 2024
*/
module ArrayAverager #(
    parameter int ARRAY_LENGTH = 1000,
    parameter int NUM_AVG = 2,
    parameter int DATA_WIDTH = 16
)(
    input wire clk,          // Clock signal
    input wire reset,        // Asynchronous reset (active high)
    input wire data_in_valid,   // Data valid signal
//    input wire [3:0] num_avg, // Number of chirps to average
    input wire [DATA_WIDTH-1:0] input_array [0:ARRAY_LENGTH-1], // Input array (1024 samples)
    output reg [DATA_WIDTH-1:0] output_array [0:ARRAY_LENGTH-1],// Averaged array (1024 samples)
    output wire data_out_valid
);

    reg [20:0] sum_array [0:ARRAY_LENGTH-1]; // Accumulator for sum of arrays, add 5 more bits to prevent overflow
    reg [3:0] count; // Counter for number of arrays received
    
//    initial begin
//        for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
//           sum_array[i] <= 0; // Reset the sum array
//    end

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
                sum_array[i] <= 0; // Reset the sum array
            count <= 0; // Reset the counter
        end else begin
            if (data_in_valid && count < NUM_AVG) begin
                for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
                    sum_array[i] <= sum_array[i] + input_array[i]; // Accumulate the samples
                count <= count + 1; // Increment the counter
            end else if (count == NUM_AVG) begin
                for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
                    sum_array[i] <= 0; // Reset the accumulator. This can happen during the "dead time" of num_avg-th chirp.
                count <= 0;
            end
        end
    end

    // Calculate the average 
    always @(*) begin
        for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
                output_array[i] = sum_array[i] / NUM_AVG;
    end

    assign data_out_valid = (count == NUM_AVG);

endmodule
