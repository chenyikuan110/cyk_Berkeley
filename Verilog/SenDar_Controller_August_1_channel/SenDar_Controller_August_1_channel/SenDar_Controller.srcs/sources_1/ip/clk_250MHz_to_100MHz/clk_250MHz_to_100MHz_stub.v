// Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2020.1.1 (lin64) Build 2960000 Wed Aug  5 22:57:21 MDT 2020
// Date        : Wed Aug  7 16:13:29 2024
// Host        : bwrcr740-10.eecs.berkeley.edu running 64-bit Red Hat Enterprise Linux Server release 7.9 (Maipo)
// Command     : write_verilog -force -mode synth_stub
//               /bwrcq/projects/ykchen/Vivado/SenDar_Controller/SenDar_Controller.srcs/sources_1/ip/clk_250MHz_to_100MHz/clk_250MHz_to_100MHz_stub.v
// Design      : clk_250MHz_to_100MHz
// Purpose     : Stub declaration of top-level module interface
// Device      : xcvu9p-flga2104-2L-e
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
module clk_250MHz_to_100MHz(clk_out_80MHz, clk_in1_p, clk_in1_n)
/* synthesis syn_black_box black_box_pad_pin="clk_out_80MHz,clk_in1_p,clk_in1_n" */;
  output clk_out_80MHz;
  input clk_in1_p;
  input clk_in1_n;
endmodule
