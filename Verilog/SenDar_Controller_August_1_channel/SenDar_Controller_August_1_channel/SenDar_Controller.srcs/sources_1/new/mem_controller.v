`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 04/10/2024 01:41:42 PM
// Design Name: 
// Module Name: mem_controller
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
    This module replaces the VIO, making it possible to access the values from UART as opposed to vio_interface
*/
module mem_controller #(
  parameter FIFO_WIDTH = 8
) (
  input clk,
  input rst,
  input rx_fifo_empty,
  input [FIFO_WIDTH-1:0] din,
  
  output reg rx_fifo_rd_en, 
  
  output wire [16:0] TX_DAC_frequency_word,
  output wire [16:0] TX_DAC_initial_phase,
  output wire [16:0] TX_IQ_phase_diff,      
  output wire TX_Mult_enable,
  output wire [16:0]TX_Mult_gain,

  output wire [16:0] VM_DAC_frequency_word,
  output wire [16:0] VM_DAC_initial_phase,
  output wire [16:0] VM_IQ_phase_diff,      
  output wire VM_Mult_enable,
  output wire [16:0]VM_Mult_gain   
);

  localparam MEM_WIDTH = 8;
  localparam MEM_DEPTH = 256;
  localparam NUM_BYTES_PER_WORD = MEM_WIDTH/8;
  localparam 
    IDLE = 3'd0,
    READ_CMD_ADDR = 3'd1,
    READ_DATA = 3'd2,
    WRITE_MEM_VAL = 3'd3;

  reg [2:0] curr_state;
  reg [2:0] next_state;
  //reg [MEM_WIDTH-1:0] rx_data; 

  always @(posedge clk) begin
    if (rst)
      curr_state <= IDLE;
    else
      curr_state <= next_state;
  end

  wire [7:0] addr_sum; //temp value for the address
  wire [7:0] val_to_write;
  reg write_en;
  reg [2:0] pkt_rd_cnt;
  reg [7:0] addr_0; // use this to hold the addr
  reg [MEM_WIDTH-1:0] cmd;
  reg [6:0] addr;
  reg [7:0] data;
  
  assign addr_sum = addr_0;

  always @(*) begin
    /* initial values to avoid latch synthesis */
    next_state = curr_state;
    case (curr_state)
      
      IDLE: begin
        // Command to read
        if (~rx_fifo_empty) begin
          next_state = READ_CMD_ADDR;
        end
      end
      
            
      READ_CMD_ADDR: begin
        if (pkt_rd_cnt == 2) begin // so far typed cmd, addr1, addr0
          if (cmd == 8'd49) begin
            // WRITE = '1'
            next_state = READ_DATA;
          end else begin
            next_state = IDLE; 
          end
        end
      end

      READ_DATA: begin
        if (pkt_rd_cnt == 3) begin
          next_state = WRITE_MEM_VAL;
        end
      end

      WRITE_MEM_VAL: begin
        next_state = IDLE;
      end

      default: next_state = IDLE;
    endcase
  end

  always @(*) begin
    /* initial values to avoid latch synthesis */

    rx_fifo_rd_en = 0;
    write_en = 0;
    
    case (curr_state)
      IDLE: begin
        if (~rx_fifo_empty) begin
          rx_fifo_rd_en = 1;
        end
      end

      READ_CMD_ADDR: begin
        if (~rx_fifo_empty && pkt_rd_cnt < 2) begin 
            rx_fifo_rd_en = 1;
        end
        if (pkt_rd_cnt == 3'd2) begin
          if (cmd == 8'd49 && ~rx_fifo_empty) begin
            rx_fifo_rd_en = 1;
          end
        end
      end    

      READ_DATA:begin
        if (~rx_fifo_empty && pkt_rd_cnt < 3) begin
          rx_fifo_rd_en = 1;
        end
      end

      WRITE_MEM_VAL: begin
        write_en = 1'b1;
      end

      default: begin
      end
      
    endcase
  end


  reg rx_fifo_rd_en_delayed;
  reg rx_fifo_empty_delayed;

  always @(posedge clk) begin
    rx_fifo_rd_en_delayed <= rx_fifo_rd_en;
    rx_fifo_empty_delayed <= rx_fifo_empty;
  end

  reg handshake = 0;

  always @(posedge clk) begin

    if (next_state == IDLE) begin
      handshake <= 0;
      pkt_rd_cnt <= 0;

      addr_0 <= 8'd0;

      cmd <= 8'd255;
      data <= 1'b0;
    end else begin
      handshake <= ~rx_fifo_empty && rx_fifo_rd_en;
    end

    if (~rx_fifo_empty && rx_fifo_rd_en)
      pkt_rd_cnt <= pkt_rd_cnt + 1;

    if (handshake) begin
      case (pkt_rd_cnt)
        
        3'd1: begin
          cmd <= din;
        end

        3'd2: begin
          addr_0 <= din; //zeroth number
        end
        
        3'd3: begin
          data <= din;
        end
        // default: 
      endcase
    end
  end

  //assign state_leds = (1 << curr_state);
  assign val_to_write = data;
  
  reg [7:0] TX_DAC_frequency_word_reg_2,TX_DAC_frequency_word_reg_1,TX_DAC_frequency_word_reg_0;  
  reg [7:0] TX_DAC_initial_phase_reg_2,TX_DAC_initial_phase_reg_1,TX_DAC_initial_phase_reg_0;
  reg [7:0] TX_IQ_phase_diff_reg_2,TX_IQ_phase_diff_reg_1,TX_IQ_phase_diff_reg_0;      
  reg [7:0] TX_Mult_enable_reg;
  reg [7:0] TX_Mult_gain_reg_2,TX_Mult_gain_reg_1,TX_Mult_gain_reg_0;

  reg [7:0] VM_DAC_frequency_word_reg_2,VM_DAC_frequency_word_reg_1,VM_DAC_frequency_word_reg_0;  
  reg [7:0] VM_DAC_initial_phase_reg_2,VM_DAC_initial_phase_reg_1,VM_DAC_initial_phase_reg_0;
  reg [7:0] VM_IQ_phase_diff_reg_2,VM_IQ_phase_diff_reg_1,VM_IQ_phase_diff_reg_0;     
  reg [7:0] VM_Mult_enable_reg;
  reg [7:0] VM_Mult_gain_reg_2,VM_Mult_gain_reg_1,VM_Mult_gain_reg_0;
  
  assign TX_DAC_frequency_word = {TX_DAC_frequency_word_reg_2[0],TX_DAC_frequency_word_reg_1,TX_DAC_frequency_word_reg_0};
  assign TX_DAC_initial_phase = {TX_DAC_initial_phase_reg_2[0],TX_DAC_initial_phase_reg_1,TX_DAC_initial_phase_reg_0};
  assign TX_IQ_phase_diff = {TX_IQ_phase_diff_reg_2[0],TX_IQ_phase_diff_reg_1,TX_IQ_phase_diff_reg_0};      
  assign TX_Mult_enable = TX_Mult_enable_reg[0];
  assign TX_Mult_gain = {TX_Mult_gain_reg_2[0],TX_Mult_gain_reg_1,TX_Mult_gain_reg_0};
  
  assign VM_DAC_frequency_word = {VM_DAC_frequency_word_reg_2[0],VM_DAC_frequency_word_reg_1,VM_DAC_frequency_word_reg_0};
  assign VM_DAC_initial_phase = {VM_DAC_initial_phase_reg_2[0],VM_DAC_initial_phase_reg_1,VM_DAC_initial_phase_reg_0};
  assign VM_IQ_phase_diff = {VM_IQ_phase_diff_reg_2[0],VM_IQ_phase_diff_reg_1,VM_IQ_phase_diff_reg_0};      
  assign VM_Mult_enable = VM_Mult_enable_reg[0];
  assign VM_Mult_gain = {VM_Mult_gain_reg_2[0],VM_Mult_gain_reg_1,VM_Mult_gain_reg_0}; 
  
  
  always @ (posedge clk)begin
    if(rst)begin
        TX_DAC_frequency_word_reg_2 <= 8'h00;
        TX_DAC_frequency_word_reg_1 <= 8'h00;
        TX_DAC_frequency_word_reg_0 <= 8'hFF;
        TX_DAC_initial_phase_reg_2 <= 8'h00;
        TX_DAC_initial_phase_reg_1 <= 8'h00;
        TX_DAC_initial_phase_reg_0 <= 8'h00;
        TX_IQ_phase_diff_reg_2 <= 8'h00;
        TX_IQ_phase_diff_reg_1 <= 8'h7F;
        TX_IQ_phase_diff_reg_0 <= 8'hFF;     
        TX_Mult_enable_reg <= 1'b1;
        TX_Mult_gain_reg_2 <= 8'h00;
        TX_Mult_gain_reg_1 <= 8'h80;
        TX_Mult_gain_reg_0 <= 8'h00;
        
        VM_DAC_frequency_word_reg_2 <= 8'h00;
        VM_DAC_frequency_word_reg_1 <= 8'h00;
        VM_DAC_frequency_word_reg_0 <= 8'hFF;
        VM_DAC_initial_phase_reg_2 <= 8'h00;
        VM_DAC_initial_phase_reg_1 <= 8'h00;
        VM_DAC_initial_phase_reg_0 <= 8'h00;
        VM_IQ_phase_diff_reg_2 <= 8'h00;
        VM_IQ_phase_diff_reg_1 <= 8'h7F;
        VM_IQ_phase_diff_reg_0 <= 8'hFF;     
        VM_Mult_enable_reg <= 1'b1;
        VM_Mult_gain_reg_2 <= 8'h00;
        VM_Mult_gain_reg_1 <= 8'h80;
        VM_Mult_gain_reg_0 <= 8'h00;
        
    end else if(write_en) begin
        case(addr_sum)
           8'd0: begin  TX_DAC_frequency_word_reg_2 <= val_to_write; end
           8'd1: begin  TX_DAC_frequency_word_reg_1 <= val_to_write; end
           8'd2: begin  TX_DAC_frequency_word_reg_0 <= val_to_write; end
           
           8'd3: begin  TX_DAC_initial_phase_reg_2 <= val_to_write; end
           8'd4: begin  TX_DAC_initial_phase_reg_1 <= val_to_write; end
           8'd5: begin  TX_DAC_initial_phase_reg_0 <= val_to_write; end
           
           8'd6: begin  TX_IQ_phase_diff_reg_2 <= val_to_write; end
           8'd7: begin  TX_IQ_phase_diff_reg_1 <= val_to_write; end
           8'd8: begin  TX_IQ_phase_diff_reg_0 <= val_to_write; end
           
           8'd9: begin  TX_Mult_enable_reg <= val_to_write; end
           8'd10: begin  TX_Mult_gain_reg_2 <= val_to_write; end
           8'd11: begin  TX_Mult_gain_reg_1 <= val_to_write; end
           8'd12: begin  TX_Mult_gain_reg_0 <= val_to_write; end   
             
           8'd13: begin VM_DAC_frequency_word_reg_2 <= val_to_write; end       
           8'd14: begin VM_DAC_frequency_word_reg_1 <= val_to_write; end
           8'd15: begin VM_DAC_frequency_word_reg_0 <= val_to_write; end
           
           8'd16: begin VM_DAC_initial_phase_reg_2 <= val_to_write; end
           8'd17: begin VM_DAC_initial_phase_reg_1 <= val_to_write; end
           8'd18: begin VM_DAC_initial_phase_reg_0 <= val_to_write; end
           
           8'd19: begin VM_IQ_phase_diff_reg_2 <= val_to_write; end
           8'd20: begin VM_IQ_phase_diff_reg_1 <= val_to_write; end
           8'd21: begin VM_IQ_phase_diff_reg_0 <= val_to_write; end  
             
           8'd22: begin VM_Mult_enable_reg <= val_to_write; end
           8'd23: begin VM_Mult_gain_reg_2 <= val_to_write; end
           8'd24: begin VM_Mult_gain_reg_1 <= val_to_write; end
           8'd25: begin VM_Mult_gain_reg_0 <= val_to_write; end
        endcase
    end
  end
  
  
endmodule