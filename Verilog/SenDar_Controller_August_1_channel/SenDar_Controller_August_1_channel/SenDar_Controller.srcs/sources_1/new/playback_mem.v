`timescale 1ns / 1ps

module playback_mem #(
    parameter MAX_DATA_ADDR = 8800
)(
    input wire clk,
    input wire reset,
    input wire enable,
    output wire [31:0] samples,
    output wire [15:0] data,
    output wire last_data
    );
    
    // Load the memory file
    reg [15:0] sine_lut [0:MAX_DATA_ADDR-1];
    reg [31:0] sample_count;
    reg [15:0] addr;
    initial begin
       $readmemb("sine_8800.mem", sine_lut);
    end
    
    always @ (posedge clk) begin
        if(reset)begin
            addr <= 0;
            sample_count <= 0;
        end else begin
            if(enable)begin
                addr <= (addr < MAX_DATA_ADDR-1)? addr + 1 : 0;
                sample_count <= sample_count + 1;
            end else 
                addr <= 0; // if dataflow is paused, reset data addr
        end
    end
    
    assign data = sine_lut[addr];
    assign last_data = (sample_count % MAX_DATA_ADDR == MAX_DATA_ADDR-1);
    assign samples = sample_count;
endmodule
