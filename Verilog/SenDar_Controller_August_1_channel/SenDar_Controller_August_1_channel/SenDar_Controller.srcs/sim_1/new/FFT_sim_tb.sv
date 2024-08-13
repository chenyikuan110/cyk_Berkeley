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


module FFT_sim_tb(

    );
    parameter SAMPLE_CNT_MAX = 8; // edit to 62500 while programming
    parameter PULSE_CNT_MAX = 8;   // edit to 200 while programming
    parameter BAUD_RATE = 921_600;
    parameter CYCLES_PER_SECOND = 250_000_000;
    
    logic CLK_250MHZ_CLK1_P;
    logic reset_input;
    
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
    
    assign output_real = m_axis_data_tdata[15:0];
    assign output_imag = m_axis_data_tdata[31:16];
    
    // 250 MHz Clock Generations
    initial begin
        CLK_250MHZ_CLK1_P = 0;
    end
    always begin           
        #2 CLK_250MHZ_CLK1_P = ~CLK_250MHZ_CLK1_P;  // period is 4 ns for 250MHz
    end
    
    // Cycle counter & sample counter
    logic [31:0] cycles, samples;
    always_ff @ (posedge CLK_250MHZ_CLK1_P) begin
        if(reset_input)begin
            cycles <= 0;
        end else begin
            if(s_axis_data_tvalid)begin
                cycles <= cycles + 1;
            end
        end
    end
        
    // Monitor
    always_comb begin
        samples = top.samples;
        s_axis_data_tdata = top.s_axis_data_tdata;
        s_axis_data_tlast = top.s_axis_data_tlast;
    end
    
    // Output sample count
    reg [31:0] output_sample_count;
    always_ff @ (posedge CLK_250MHZ_CLK1_P) begin
       if(reset_input)begin
           output_sample_count <= 0;
       end else begin
           if(m_axis_data_tlast)begin
              output_sample_count <= 0;
              if(m_axis_data_tvalid)
                 $display("%d, %d",output_sample_count, m_axis_data_tdata);
           end else if(m_axis_data_tvalid)begin
              output_sample_count <= output_sample_count + 1;
              $display("%d, %d",output_sample_count, m_axis_data_tdata);
           end
       end
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
        s_axis_config_tvalid = 0;
        
        repeat (1) @(posedge CLK_250MHZ_CLK1_P);    
        reset_input = 1;
        repeat (2) @(posedge CLK_250MHZ_CLK1_P);   
        reset_input = 0;
        
        wait (s_axis_config_tready == 1'b1);
        @(posedge CLK_250MHZ_CLK1_P);  
        #2 s_axis_config_tvalid = 1'b1;
        
        wait (s_axis_data_tready == 1'b1);
        @(posedge CLK_250MHZ_CLK1_P);  
        s_axis_data_tvalid = 1'b1; // starts transmitting
        
        // ... computing FFT ...
        // s_axis_data_tvalid = 1'b0; // stops transmitting
        
        wait (m_axis_data_tvalid == 1'b1);
        wait (m_axis_data_tvalid == 1'b0);
        
        repeat (200) @(posedge CLK_250MHZ_CLK1_P);   
    end
    
    top  #(
        .SAMPLE_CNT_MAX(    SAMPLE_CNT_MAX      ), // edit to 62500 while programming
        .PULSE_CNT_MAX(     PULSE_CNT_MAX       ),   // edit to 200 while programming
        .BAUD_RATE(         BAUD_RATE           ),
        .CYCLES_PER_SECOND( CYCLES_PER_SECOND   )
    ) top(
         .CLK_250MHZ_CLK1_P(     CLK_250MHZ_CLK1_P      )           
        ,.CLK_250MHZ_CLK1_N(    ~CLK_250MHZ_CLK1_P      )
        ,.reset_input(          reset_input             )
        
        ,.s_axis_config_tvalid( s_axis_config_tvalid    )
        ,.s_axis_config_tready( s_axis_config_tready    )
        
        //,.s_axis_data_tdata(    s_axis_data_tdata       )
        ,.s_axis_data_tvalid(   s_axis_data_tvalid      )
        //,.s_axis_data_tlast(    s_axis_data_tlast       )
        
        ,.s_axis_data_tready(   s_axis_data_tready      )   
        ,.m_axis_data_tdata(    m_axis_data_tdata       )
        ,.m_axis_data_tuser(    m_axis_data_tuser       )
        ,.m_axis_data_tvalid(   m_axis_data_tvalid      )
        ,.m_axis_data_tlast(    m_axis_data_tlast       )
        
        ,.event_frame_started(  event_frame_started     )
        ,.event_tlast_unexpected(event_tlast_unexpected )
        ,.event_tlast_missing(  event_tlast_missing     )
        ,.event_fft_overflow(   event_fft_overflow      )
        ,.event_data_in_channel_halt( event_data_in_channel_halt )   
    );
endmodule
