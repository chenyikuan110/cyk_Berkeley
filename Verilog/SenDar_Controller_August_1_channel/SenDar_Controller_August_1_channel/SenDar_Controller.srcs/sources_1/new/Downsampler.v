`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/19/2024 02:00:51 PM
// Design Name: 
// Module Name: Downsampler
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
module Downsampler #(
    parameter DOWNSAMPLING_FACTOR = 8
)(
    input wire clk,       // Clock input
    input wire reset,     // Asynchronous reset (active low)
    input wire enable,    // if disabled, will just keep data flowing
    input wire [15:0] in, // Input data (16-bit wide)
    output wire output_valid,
    output wire [15:0] out // Output data (16-bit wide)
);
    reg [15:0] counter = 0; // Counter to keep track of downsampling
    reg [15:0] dout;
    always @(posedge clk) begin
        if (reset) begin
            counter <= 0; // Reset the counter
            dout <= 0;
        end else begin
            if(enable)begin
                dout <= (counter == 0)? in : dout; // Output the input data every 10th clock cycle
                counter <= (counter == DOWNSAMPLING_FACTOR - 1)?  0 : counter + 1; // Increment the counter
            end else begin
                counter <= 0;
            end
        end
    end

    assign output_valid = (enable)? (counter == 1) : 1'b1; // latency is 1 cycle when on
    assign out = (enable)? dout : in; // latency is 1 cycle when on, 0 when off

endmodule
