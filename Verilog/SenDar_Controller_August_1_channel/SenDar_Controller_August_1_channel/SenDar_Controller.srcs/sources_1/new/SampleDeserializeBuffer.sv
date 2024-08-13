/*
    1024 sample buffer for incoming data stream for the FFT
    First draft: Feb 28 2024
*/
module SampleDeserializeBuffer 
#(
    parameter int ARRAY_LENGTH = 1000,
    parameter int DATA_WIDTH = 16
)(
    input wire clk,          // Clock input
    input wire reset,        // Reset input
    input wire enable,       // Enable input
    input wire data_in_valid, // Valid input
    input wire [DATA_WIDTH-1:0] data_in,  // 16-bit data input
    output wire [DATA_WIDTH-1:0] data_out [0:ARRAY_LENGTH-1],  // 1024 parallel data outputs
    output wire data_out_valid // one cycle pulse showing the output is ready to be loaded
);
    reg [DATA_WIDTH-1:0] buffer [0:ARRAY_LENGTH-1];  // Internal buffer to store samples
    reg [9:0] count;

    always_ff @(posedge clk) begin
        if (reset) begin
            // Reset the buffer
            count <= 0;
            for (int i = 0; i < ARRAY_LENGTH; i = i + 1)
                buffer[i] <= 0;
        end else begin
            // Shift data into the buffer
            // When enable rises, next edge should shift in mem[0]
            if(enable)begin
                if(data_in_valid)begin
                    count <= (count < ARRAY_LENGTH)? count + 1 : 0;
                    for (int i = 0; i <ARRAY_LENGTH-1; i = i + 1)
                        buffer[i] <= buffer[i + 1];
                    buffer[ARRAY_LENGTH-1] <= data_in;
                end
            end else begin
                count <= 0; // count should stay 0 when not shifting
            end
        end
    end

    // Assign parallel outputs
    assign data_out = buffer;
    assign data_out_valid = (~enable & count == ARRAY_LENGTH); // so it only stays high for one cycle


endmodule
