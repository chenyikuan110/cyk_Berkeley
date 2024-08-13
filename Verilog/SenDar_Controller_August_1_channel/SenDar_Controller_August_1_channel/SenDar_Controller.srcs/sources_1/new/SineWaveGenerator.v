`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/19/2024 02:02:54 PM
// Design Name: 
// Module Name: SineWaveGenerator
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
    Single tone generator with tunable frequency (provided externally) and initial phase (provided externally) 
    Fireset draft: Feb 28 2024, not finalized
*/

module SineWaveGenerator #(
    parameter ADDR_WIDTH = 14, //15 if LUT_SIZE = 32768
    parameter LUT_SIZE = 16384
)(
    input wire clk, // Clock input, let's say it is 100MHz, and we at minimum support 1KHz, this is 100k points!
    input wire reset, // Reset input
    input wire enable, // Enable signal for the DAC, when is 0, the phase should reset to initial_phase
    input wire next_sample, // a one-cycle signal to update the output
    input wire [ADDR_WIDTH +1:0] frequency_word, // This is the number of index to advance every output cycle, range 0 - 32767 (2^15-1)
    input wire [ADDR_WIDTH +1:0] initial_phase, // Initial phase (in index), range 0 - 65535 (2^16-1)
    input wire [ADDR_WIDTH +1:0] IQ_phase_diff, // if 0, both IQ will output the same number, else cosine_output will lead by the phase diff 
    output wire [15:0] cosine_output,
    output wire [15:0] sine_output // Sine wave output (16-bit resolution)
);

    // Phase accumulator
    wire [ADDR_WIDTH:0] LUT_SIZE_DOUBLE_MINUS_ONE;
    assign LUT_SIZE_DOUBLE_MINUS_ONE = (1 << (ADDR_WIDTH+1)) -1; // 32767 if addr_width is 14
    
    reg [ADDR_WIDTH+1:0] sine_phase_acc, cosine_phase_acc;
    
    always @(posedge clk) begin
        if (reset) begin
            sine_phase_acc <= initial_phase;
            cosine_phase_acc <= initial_phase + IQ_phase_diff;
        end else begin
            if(enable)begin
                if(next_sample)begin
                    sine_phase_acc <= sine_phase_acc + frequency_word;
                    cosine_phase_acc <= cosine_phase_acc + frequency_word;
                end
            end else begin
                sine_phase_acc <= initial_phase;
                cosine_phase_acc <= initial_phase + IQ_phase_diff;
            end
        end
    end

    // 16-bit Sine lookup table generation
    reg [15:0] sine_lut [0:LUT_SIZE-1];
    initial begin
       $readmemb("sine_0to90_32768_16b.mem", sine_lut);
    end

    // Output
    wire [1:0] sine_quadrant, cosine_quadrant;
    wire [ADDR_WIDTH-1:0] sine_index, cosine_index;
    wire [ADDR_WIDTH:0] sine_even_quadrant_index, sine_odd_quadrant_index;
    wire [ADDR_WIDTH:0] cosine_even_quadrant_index, cosine_odd_quadrant_index;
    
    assign sine_quadrant = sine_phase_acc[ADDR_WIDTH+1:ADDR_WIDTH];
    assign sine_even_quadrant_index = sine_phase_acc[ADDR_WIDTH:0];
    assign sine_odd_quadrant_index  = LUT_SIZE_DOUBLE_MINUS_ONE - sine_phase_acc[ADDR_WIDTH:0]; // couunt backward if phase is between 90-180 or 270-360 deg
    assign sine_index = (sine_quadrant[0] == 1'b0)? sine_even_quadrant_index[ADDR_WIDTH-1:0] : sine_odd_quadrant_index[ADDR_WIDTH-1:0] ;
    
    assign cosine_quadrant = cosine_phase_acc[ADDR_WIDTH+1:ADDR_WIDTH];
    assign cosine_even_quadrant_index = cosine_phase_acc[ADDR_WIDTH:0];
    assign cosine_odd_quadrant_index  = LUT_SIZE_DOUBLE_MINUS_ONE - cosine_phase_acc[ADDR_WIDTH:0]; // couunt backward if phase is between 90-180 or 270-360 deg
    assign cosine_index = (cosine_quadrant[0] == 1'b0)? cosine_even_quadrant_index[ADDR_WIDTH-1:0] : cosine_odd_quadrant_index[ADDR_WIDTH-1:0] ;    
    
    assign cosine_output = (cosine_quadrant[1] == 1'b0)? sine_lut[cosine_index] : (1 << 16) - sine_lut[cosine_index];
    assign sine_output = (sine_quadrant[1] == 1'b0)? sine_lut[sine_index] : (1 << 16) - sine_lut[sine_index];

endmodule

