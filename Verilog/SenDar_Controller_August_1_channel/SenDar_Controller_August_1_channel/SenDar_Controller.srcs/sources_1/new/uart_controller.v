`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/15/2024 02:55:30 PM
// Design Name: 
// Module Name: uart_controller
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

module uart_controller(
    input wire clk,
    input wire reset,
    input wire [31:0] fft_result_fifo_dout,
    input wire fifo_empty,
    input wire uart_tx_data_ready,
    output wire fifo_rd_en,
    output wire uart_tx_data_valid,
    output wire [7:0] uart_tx_data
);

reg [2:0] downcount;
reg [15:0] sent_sample_count;
assign fifo_rd_en = ~fifo_empty & (downcount == 0) & uart_tx_data_ready; 
assign uart_tx_data_valid = (downcount != 0) & uart_tx_data_ready;

always @(posedge clk) begin
    if(reset) begin
        downcount <= 0;
        sent_sample_count <= 0;
    end else begin      
        if(fifo_rd_en) begin
            downcount <= 3'd4;
            sent_sample_count <= sent_sample_count + 1;
        end 
        if(uart_tx_data_ready & uart_tx_data_valid) 
            downcount <= downcount - 1; // decrement after every handshake
    end
end

/*
    4:1 MUX - combinational logic
*/
reg [7:0] uart_tx_data_reg;
always @(*) begin
    uart_tx_data_reg = fft_result_fifo_dout[7:0];
    case(downcount)
        3'd1: uart_tx_data_reg = fft_result_fifo_dout[7:0];
        3'd2: uart_tx_data_reg = fft_result_fifo_dout[15:8];
        3'd3: uart_tx_data_reg = fft_result_fifo_dout[23:16];
        3'd4: uart_tx_data_reg = fft_result_fifo_dout[31:24];
    endcase
end
assign uart_tx_data = uart_tx_data_reg;

//WordToByteSerializer WordToByteSerializer_inst(
//    .clk(clk)          // Clock input
//   ,.reset(reset)        // Reset input
//   ,.enable(stream_out_en)
//   ,.data_in(fft_result_fifo_dout)
//   ,.data_out(uart_tx_data_out)
//);

endmodule
