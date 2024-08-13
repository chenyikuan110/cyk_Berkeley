`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/14/2024 09:27:14 PM
// Design Name: 
// Module Name: fifo
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

module fifo #(
    parameter DATA_WIDTH = 32,
    parameter DEPTH = 1024, 
    parameter POINTER_WIDTH = 12
) (
    input clk, rst,

    // Write side
    input wr_en,
    input [DATA_WIDTH-1:0] din,
    output full,

    // Read side
    input rd_en,
    output reg [DATA_WIDTH-1:0] dout,
    output empty
);
    reg [DATA_WIDTH-1:0] data [DEPTH-1:0];
    reg [POINTER_WIDTH-1:0] rd_ptr, wr_ptr;
    // TODO: we can eliminate this entry_counter with one extra bit on rd_ptr and wr_ptr
    reg [POINTER_WIDTH:0] entry_counter;

    assign full = entry_counter == DEPTH;
    assign empty = entry_counter == 0;

    // Update entry_counter
    always @ (posedge clk) begin
        if (rst) begin
            entry_counter <= 0;
        end
        else if (wr_en && ~rd_en && !full) begin
            entry_counter <= entry_counter + 1;
        end
        else if (rd_en && ~wr_en && !empty) begin
            entry_counter <= entry_counter - 1;
        end
        else begin
            entry_counter <= entry_counter;
        end
    end

    // Update read pointer
    always @ (posedge clk) begin
        if (rst) begin
            rd_ptr <= 0;
        end
        else if (rd_en && ~empty) begin
            rd_ptr <= rd_ptr + 1;
        end
        else begin
            rd_ptr <= rd_ptr;
        end
    end

    // Update write pointer
    always @ (posedge clk) begin
        if (rst) begin
            wr_ptr <= 0;
        end
        else if (wr_en && ~full) begin
            wr_ptr <= wr_ptr + 1;
        end
        else begin
            wr_ptr <= wr_ptr;
        end
    end

    // Update internal data array
    always @ (posedge clk) begin
        if (wr_en && ~full) begin
            data[wr_ptr] <= din;
        end
        else begin
            data[wr_ptr] <= data[wr_ptr];
        end
    end

    // Update data out
    always @ (posedge clk) begin
        if (rst) begin
            dout <= 0;
        end
        else if (rd_en && ~empty) begin
            dout <= data[rd_ptr];
        end
        else begin
            dout <= dout;
        end
    end
endmodule
