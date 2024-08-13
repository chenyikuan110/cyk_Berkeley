`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Yikuan Chen
// 
// Create Date: 03/07/2024 01:43:10 PM
// Design Name: 
// Module Name: FFT_sim_tb
// 
//////////////////////////////////////////////////////////////////////////////////


module tb_top_sim(

    );

    parameter DOWNSAMPLING_FACTOR = 2;
    parameter INPUT_STREAM_MAX_COUNT = 1100;
    parameter INPUT_STREAM_ARRAY_LENGTH = 1000;
    parameter N_SAMPLE_TO_SEND = 16;
    parameter N_WAIT_FRAME = 4;
    parameter NUM_AVG = 10;
    parameter SAMPLE_CNT_MAX = 8; // edit to 62500 while programming
    parameter PULSE_CNT_MAX = 8;   // edit to 200 while programming
    parameter BAUD_RATE = 1_250_000;//921_600;
    parameter CYCLES_PER_SECOND = 100_000_000; //250_000_000;
    
    logic CLK_250MHZ_CLK1_P;
    logic CLK_100MHZ_CLK1_P;
    logic reset_input;
    logic data_flow_en;
    logic transmission_mode_in;
    
    logic s_axis_config_tvalid;
    logic s_axis_config_tready;
    
    logic s_axis_data_tvalid;
    logic [15:0] s_axis_data_tdata;
    logic s_axis_data_tlast;
    
    logic s_axis_data_tready;
    logic m_axis_data_tvalid;
    logic [31:0] m_axis_data_tdata;
    logic [15:0] output_real;
    logic [15:0] output_imag;
    logic [7:0] m_axis_data_tuser;
    logic m_axis_data_tlast;
    
    logic event_frame_started;
    logic event_tlast_unexpected;
    logic event_tlast_missing;
    logic event_fft_overflow;
    logic event_data_in_channel_halt;
    
    logic FPGA_SERIAL_RX;
    logic FPGA_SERIAL_TX;
    
//    assign FPGA_SERIAL_RX = 1'b1;
    
    assign output_real = m_axis_data_tdata[15:0];
    assign output_imag = m_axis_data_tdata[31:16];
    
    // 250 MHz Clock Generations
    initial begin
        CLK_250MHZ_CLK1_P = 0;
    end
    always begin           
        #2 CLK_250MHZ_CLK1_P = ~CLK_250MHZ_CLK1_P;  // period is 4 ns for 250MHz
    end
    
     // 100 MHz Clock Generations
    initial begin
        CLK_100MHZ_CLK1_P = 0;
    end
    always begin           
        #5 CLK_100MHZ_CLK1_P = ~CLK_100MHZ_CLK1_P;  // period is 4 ns for 250MHz
    end   
    
    // Cycle counter & sample counter
    logic [31:0] cycles, samples;
        
    // Monitor
    logic [15:0] mem_dataout;
    logic DeserializeBuffer_enable;
    logic Deserialized_data_valid;
    logic [15:0] Deserialized_data [0:1000-1];
    logic SerializedDataOutBegin;
    
    always_comb begin
        samples = top.samples;
        cycles = top.cycles;
        s_axis_data_tdata = top.s_axis_data_tdata;
        s_axis_data_tlast = top.s_axis_data_tlast;
        DeserializeBuffer_enable = top.DeserializeBuffer_enable;
        Deserialized_data_valid = top.Deserialized_data_valid;
        Deserialized_data = top.Deserialized_data;
        SerializedDataOutBegin = top.ReSerializedDataOutBegin;
        mem_dataout = top.mem_dataout;
        s_axis_config_tready = top.s_axis_config_tready;
        s_axis_data_tvalid = top.s_axis_data_tvalid;
        s_axis_data_tready = top.s_axis_data_tready;
        m_axis_data_tdata = top.m_axis_data_tdata;
        m_axis_data_tlast = top.m_axis_data_tlast;
        m_axis_data_tvalid = top.m_axis_data_tvalid;
    end
    
    // Output sample count
    reg [31:0] output_sample_count;
    always_ff @ (posedge CLK_100MHZ_CLK1_P) begin
       if(reset_input)begin
           output_sample_count <= 0;
       end else begin
           if(m_axis_data_tlast)begin
              output_sample_count <= 0;
              //if(m_axis_data_tvalid)
                 //$display("%d, %d",output_sample_count, m_axis_data_tdata);
           end else if(m_axis_data_tvalid)begin
              output_sample_count <= output_sample_count + 1;
              //$display("%d, %d",output_sample_count, m_axis_data_tdata);
           end
       end
    end
    
    /* UART offchip emulator*/
    logic [7:0] off_chip_data_in;
    logic  off_chip_data_in_valid; 
    logic  off_chip_data_out_ready;
    logic off_chip_data_out_valid;
    logic off_chip_data_in_ready;
    logic [7:0] off_chip_data_out;
    
    /* Define a task that checks data received by the off_chip_uart from z1_top */
    logic [10:0] received_byte_count;
    task off_chip_uart_receive;
     begin
       while (!off_chip_data_out_valid) begin
             @(posedge top.clk_global_100MHz);
         end
         #1;
         off_chip_data_out_ready = 1'b0;   
         //$display("%d", off_chip_data_out);
         received_byte_count = received_byte_count+1;
         repeat(2)@(posedge top.clk_global_100MHz);
         off_chip_data_out_ready = 1'b1;
     end
    endtask 
    
    // uart monitor
    initial begin
        received_byte_count = 0;
        off_chip_data_out_ready = 1'b1; // for the uart
        @(posedge CLK_100MHZ_CLK1_P);    
        forever off_chip_uart_receive();
    end
    
    always_ff @ (posedge top.clk_global_100MHz)begin
        if(off_chip_data_out_ready == 0)
            $display("%d, %d, 0x%0h",received_byte_count, off_chip_data_out, off_chip_data_out);
    end
    
    // Load the memory file
//    reg [15:0] sine_lut [0:255];
//    logic [7:0] addr;
//    initial begin
//       $readmemb("sine.bin", sine_lut);
//    end
    
//    always_ff @ (posedge CLK_250MHZ_CLK1_P) begin
//        if(reset_input)begin
//            addr <= 0;
//            samples <= 0;
//        end else begin
//            if(s_axis_data_tvalid && s_axis_data_tready)begin
//                addr <= addr + 1;
//                samples <= samples + 1;
//            end
//        end
//    end
    
//    assign s_axis_data_tdata = sine_lut[addr];
//    assign s_axis_data_tlast = (samples % 1024 == 1023);
    
    // initial begin
    // Sequential actions
    initial begin
        reset_input = 0;
        data_flow_en = 0;
        transmission_mode_in = 1; // 0 FFT, 1 Raw
        s_axis_config_tvalid = 0;
        
        repeat (2) @(posedge CLK_100MHZ_CLK1_P);    
        reset_input = 1;
        repeat (4) @(posedge top.clk_global_100MHz);   
        reset_input = 0;
        
        wait (s_axis_config_tready == 1'b1);
        @(posedge top.clk_global_100MHz);  
        #2 s_axis_config_tvalid = 1'b1;
        
        wait (s_axis_data_tready == 1'b1);
        @(posedge top.clk_global_100MHz);  
        data_flow_en = 1'b1; // starts transmitting
        
        wait (s_axis_data_tvalid == 1'b1);   
        repeat (2) @(posedge top.clk_global_100MHz);   
//        data_flow_en = 1'b0; // test if it terminates early
        
        repeat (2000) @(posedge top.clk_global_100MHz);    
        data_flow_en = 1'b1; // turn it back on 
        // ... computing FFT ...
 
        wait (s_axis_data_tvalid == 1'b1);
        repeat (2) @(posedge top.clk_global_100MHz);   
//        data_flow_en = 1'b0; // test if it terminates early
        transmission_mode_in = 1; // Raw
        repeat (2000) @(posedge top.clk_global_100MHz);   
        data_flow_en = 1'b1; // turn it back on 
        
        wait (m_axis_data_tvalid == 1'b1);
        wait (m_axis_data_tvalid == 1'b0);
        
        repeat (200) @(posedge CLK_250MHZ_CLK1_P);   
    end
    
    //
    top  #(
        .INPUT_STREAM_MAX_COUNT(    INPUT_STREAM_MAX_COUNT       ),
        .INPUT_STREAM_ARRAY_LENGTH( INPUT_STREAM_ARRAY_LENGTH    ),
        .DOWNSAMPLING_FACTOR(DOWNSAMPLING_FACTOR),
        .NUM_AVG(           NUM_AVG             ),
        .N_SAMPLE_TO_SEND(  N_SAMPLE_TO_SEND    ),
        .N_WAIT_FRAME(      N_WAIT_FRAME        ),
        .SAMPLE_CNT_MAX(    SAMPLE_CNT_MAX      ), // edit to 62500 while programming
        .PULSE_CNT_MAX(     PULSE_CNT_MAX       ),   // edit to 200 while programming
        .BAUD_RATE(         BAUD_RATE           ),
        .CYCLES_PER_SECOND( CYCLES_PER_SECOND   )
    ) top(
         .CLK_250MHZ_CLK1_P(     CLK_250MHZ_CLK1_P      )           
        ,.CLK_250MHZ_CLK1_N(    ~CLK_250MHZ_CLK1_P      )
        ,.reset_input(          reset_input             )
        ,.data_flow_en_in(      data_flow_en            )
        ,.transmission_mode_in(transmission_mode_in     )
        
        ,.s_axis_config_tvalid_in( s_axis_config_tvalid )
//        ,.s_axis_config_tready( s_axis_config_tready    )
        
        //,.s_axis_data_tdata(    s_axis_data_tdata       )
        //,.s_axis_data_tvalid(   s_axis_data_tvalid      )
        //,.s_axis_data_tlast(    s_axis_data_tlast       )
        
//        ,.s_axis_data_tready(   s_axis_data_tready      )   
//        ,.m_axis_data_tdata(    m_axis_data_tdata       )
//        ,.m_axis_data_tuser(    m_axis_data_tuser       )
//        ,.m_axis_data_tvalid(   m_axis_data_tvalid      )
//        ,.m_axis_data_tlast(    m_axis_data_tlast       )
        
//        ,.event_frame_started(  event_frame_started     )
//        ,.event_tlast_unexpected(event_tlast_unexpected )
//        ,.event_tlast_missing(  event_tlast_missing     )
//        ,.event_fft_overflow(   event_fft_overflow      )
//        ,.event_data_in_channel_halt( event_data_in_channel_halt )   
        
        ,.FPGA_SERIAL_RX_PIN(FPGA_SERIAL_RX)
        ,.FPGA_SERIAL_TX_PIN(FPGA_SERIAL_TX)
    );
    
    // Uart sink emulator
    uart #(
          .BAUD_RATE(BAUD_RATE),
          .CLOCK_FREQ(CYCLES_PER_SECOND)
      ) off_chip_uart (
          .clk(top.clk_global_100MHz),
          .reset(reset_input),
          .data_in(off_chip_data_in),
          .data_in_valid(off_chip_data_in_valid),
          .data_in_ready(off_chip_data_in_ready),
          .data_out(off_chip_data_out),
          .data_out_valid(off_chip_data_out_valid),
          .data_out_ready(off_chip_data_out_ready),
          .serial_in(FPGA_SERIAL_TX),
          .serial_out(FPGA_SERIAL_RX)
      );
endmodule
