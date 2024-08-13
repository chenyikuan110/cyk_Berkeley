`timescale 1ns / 1ps
/*
    Unity gain buffer with zero padding
    First draft: March 5 2024
*/
module SamplePlaybackSerializeBuffer 
#(
    parameter int INPUT_ARRAY_LENGTH = 1000,
    parameter int OUTPUT_ARRAY_LENGTH = 1024,
    parameter int DATA_WIDTH = 16
)(
    input wire clk,     // 10-bit gain coefficient
    input wire reset,        // Asynchronous reset (active high)
    input wire [DATA_WIDTH-1:0] data_in [0:INPUT_ARRAY_LENGTH-1], // 16-bit input data
    input wire data_in_valid,   // Data valid signal, this is a single-cycle pulse
    output wire data_out_valid, // Asserted in the same cycle as new_data_out_begin, and never de-asserts unless reset
    
    input wire fft_core_tready, // FFT core wait halt for N (N>=1) cycles at the very begining. Data cannot flow at this time.
    output wire new_data_out_begin, // Tells the data sink (next stage) to start consuming samples
    output wire data_out_last,  // Tells the data sink the current sample is the last sample of the
    output wire [DATA_WIDTH-1:0] data_out // 16-bit output data
);
    wire data_load;
    
    reg [DATA_WIDTH-1:0] data_out_reg [0:OUTPUT_ARRAY_LENGTH-1];
    reg [10:0] count;
    reg data_load_delayed;
    reg data_out_valid_reg;
    
    assign data_load = data_in_valid;
    always_ff @(posedge clk) begin
        if (reset) begin
            // Reset the data register
            count <= 0;
            for (int i = 0; i < OUTPUT_ARRAY_LENGTH; i = i + 1)
                data_out_reg[i] <= 16'h0;
        end else begin
            if (data_load) begin
                count <= 0;
                for (int i = 0; i < INPUT_ARRAY_LENGTH; i = i + 1)
                    data_out_reg[i] <= data_in[i];
            end else if(data_out_valid & fft_core_tready) begin // do not start shifting if the data out isn't even begining to shift
                count <= (count < OUTPUT_ARRAY_LENGTH-1)? count + 1 : 0; // count shifted-out samples
                for (int i = 0; i < OUTPUT_ARRAY_LENGTH-1; i = i + 1)
                    data_out_reg[i] <= data_out_reg[i+1];
                data_out_reg[OUTPUT_ARRAY_LENGTH-1] <= data_out_reg[0]; // playback
            end
        end
    end
    
    always_ff @(posedge clk)begin
        data_load_delayed <= data_load;
    end
    
    always_ff @(posedge clk)begin       
        if(reset)begin
            data_out_valid_reg <= 1'b0;
        end else begin
            if(data_load)
                data_out_valid_reg <= 1'b1;
            else if (data_out_last)
                data_out_valid_reg <= 1'b0;
        end
    end

    assign data_out = data_out_reg[0];
    assign data_out_valid = data_out_valid_reg;
    // assign data_out_valid = data_load_delayed; // again, only asserts for one cycle so 2nd frame doesn't start by itself
    assign data_out_last = (count == OUTPUT_ARRAY_LENGTH-1);
    assign new_data_out_begin = data_load_delayed;

endmodule

