// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2020.1.1 (lin64) Build 2960000 Wed Aug  5 22:57:21 MDT 2020
// Date        : Fri Aug  9 18:47:05 2024
// Host        : bwrcr740-10.eecs.berkeley.edu running 64-bit Red Hat Enterprise Linux Server release 7.9 (Maipo)
// Command     : write_verilog -force -mode synth_stub
//               /bwrcq/projects/ykchen/Vivado/SenDar_Controller/SenDar_Controller.srcs/sources_1/ip/vio_0/vio_0_stub.v
// Design      : vio_0
// Purpose     : Stub declaration of top-level module interface
// Device      : xcvu9p-flga2104-2L-e
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* X_CORE_INFO = "vio,Vivado 2020.1.1" *)
module vio_0(clk, probe_in0, probe_in1, probe_in2, probe_in3, 
  probe_in4, probe_in5, probe_in6, probe_in7, probe_in8, probe_in9, probe_in10, probe_in11, 
  probe_in12, probe_in13, probe_out0, probe_out1, probe_out2, probe_out3, probe_out4, probe_out5, 
  probe_out6)
/* synthesis syn_black_box black_box_pad_pin="clk,probe_in0[31:0],probe_in1[31:0],probe_in2[31:0],probe_in3[31:0],probe_in4[16:0],probe_in5[16:0],probe_in6[16:0],probe_in7[0:0],probe_in8[16:0],probe_in9[16:0],probe_in10[16:0],probe_in11[16:0],probe_in12[0:0],probe_in13[16:0],probe_out0[0:0],probe_out1[0:0],probe_out2[0:0],probe_out3[0:0],probe_out4[0:0],probe_out5[0:0],probe_out6[0:0]" */;
  input clk;
  input [31:0]probe_in0;
  input [31:0]probe_in1;
  input [31:0]probe_in2;
  input [31:0]probe_in3;
  input [16:0]probe_in4;
  input [16:0]probe_in5;
  input [16:0]probe_in6;
  input [0:0]probe_in7;
  input [16:0]probe_in8;
  input [16:0]probe_in9;
  input [16:0]probe_in10;
  input [16:0]probe_in11;
  input [0:0]probe_in12;
  input [16:0]probe_in13;
  output [0:0]probe_out0;
  output [0:0]probe_out1;
  output [0:0]probe_out2;
  output [0:0]probe_out3;
  output [0:0]probe_out4;
  output [0:0]probe_out5;
  output [0:0]probe_out6;
endmodule
