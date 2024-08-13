`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: Yikuan Chen
// 
// Create Date: 03/07/2024 12:43:32 PM
// Design Name: 
// Module Name: top
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
module top #(
    parameter INPUT_STREAM_MAX_COUNT = 1100,
    parameter INPUT_STREAM_ARRAY_LENGTH = 1000,
    parameter DOWNSAMPLING_FACTOR = 10,
    parameter NUM_AVG = 10,
    parameter N_SAMPLE_TO_SEND = 512,
    parameter N_WAIT_FRAME = 165,    // when no input stream decimation, this is NUM_AVG times faster
    parameter SAMPLE_CNT_MAX = 62500, // edit to 62500 while programming
    parameter PULSE_CNT_MAX = 200,   // edit to 200 while programming
    parameter BAUD_RATE = 115200, //115_200,  // 921_600,
    parameter CYCLES_PER_SECOND = 100_000_000 //250_000_000
)(
    input wire CLK_250MHZ_CLK1_P,           
    input wire CLK_250MHZ_CLK1_N,
    input wire reset_input,
    input wire data_flow_en_in,
    input wire transmission_mode_in,
    
    input wire s_axis_config_tvalid_in,  
//    output wire s_axis_config_tready,
    
    // input wire s_axis_data_tvalid,
    // input wire [15:0] s_axis_data_tdata,
    // input wire s_axis_data_tlast,
    
//    output wire s_axis_data_tready,
//    output wire m_axis_data_tvalid,
//    output wire [31:0] m_axis_data_tdata,
//    output wire [7:0] m_axis_data_tuser,
//    output wire m_axis_data_tlast,
    
//    output wire event_frame_started,
//    output wire event_tlast_unexpected,
//    output wire event_tlast_missing,
//    output wire event_fft_overflow,
//    output wire event_data_in_channel_halt,
    
    input wire FPGA_SERIAL_RX_PIN,
    output wire FPGA_SERIAL_TX_PIN,
    
    output wire GPIO_LED2,
    output wire GPIO_LED1,
    output wire GPIO_LED0
    
);
    wire reset_buffered, reset_vio, reset;
    wire data_flow_en_in_buffered, data_flow_en_in_vio;
    wire transmission_mode_in_buffered;
    wire s_axis_config_tvalid_in_buffered, s_axis_config_tvalid_in_vio,s_axis_config_tvalid;
    wire s_axis_config_tready;
    wire s_axis_data_tready;
    wire s_axis_data_tvalid;
    wire m_axis_data_tvalid;
    wire [31:0] m_axis_data_tdata;
    wire [7:0] m_axis_data_tuser;
    wire m_axis_data_tlast;
    
    wire event_frame_started;
    wire event_tlast_unexpected;
    wire event_tlast_missing;
    wire event_fft_overflow;
    wire event_data_in_channel_halt;
    reg data_flow_en;
    wire FPGA_SERIAL_RX, FPGA_SERIAL_TX;
//    wire clk_global_250MHz; // 250 MHz Clk
    
    OBUF #(.IOSTANDARD("LVCMOS12")) OBUF_s_axis_data_tready(.O(GPIO_LED2), .I(s_axis_data_tready)); 
    OBUF #(.IOSTANDARD("LVCMOS12")) OBUF_s_axis_config_tready(.O(GPIO_LED1), .I(s_axis_config_tready)); 
    OBUF #(.IOSTANDARD("LVCMOS12")) OBUF_data_flow_en (.O(GPIO_LED0), .I(data_flow_en)); 
    OBUF #(.IOSTANDARD("LVCMOS18")) OBUF_FPGA_SERIAL_TX(.O(FPGA_SERIAL_TX_PIN), .I(FPGA_SERIAL_TX)); 
    
//    IBUFGDS CLK_BUF(.O(   clk_global_250MHz ),
//                    .I (   CLK_250MHZ_CLK1_P          ),
//                    .IB(   CLK_250MHZ_CLK1_N          )
//                    );   
    IBUF RESET_BUF ( .O(reset_buffered  ),
                     .I(reset_input     )
                     );
    IBUF DATA_FLOW_EN_BUF ( .O(data_flow_en_in_buffered  ),
                      .I(data_flow_en_in     )
                      ); 
    IBUF TMODE_IN_BUF ( .O(transmission_mode_in_buffered  ),
                        .I(transmission_mode_in     )
                        );                     
    IBUF S_AXIS_CONFIG_TVALID_BUF ( .O(s_axis_config_tvalid_in_buffered  ),
                .I(s_axis_config_tvalid_in     )
                ); 
    IBUF UART_RX_BUF(.O(FPGA_SERIAL_RX ),
                .I(FPGA_SERIAL_RX_PIN  ));  
                
    /* 
        The core clock
    */
    wire clk_global_100MHz;
    clk_250MHz_to_100MHz  clk_250MHz_to_100MHz_inst(
        .clk_in1_p(CLK_250MHZ_CLK1_P)
       ,.clk_in1_n(CLK_250MHZ_CLK1_N)
       ,.clk_out_100MHz(clk_global_100MHz)
    );
    
     /*
        VIO
     */
     wire transmission_mode_vio;
     wire DAC_mem_select;    
     wire DAC_cosine_select;
     wire Downsampling_enable;
     
     wire [13:0] TX_DAC_frequency_word;
     wire [13:0] VM_DAC_frequency_word;
     wire [15:0] TX_DAC_initial_phase,TX_IQ_phase_diff;
     wire [15:0] VM_DAC_initial_phase,VM_IQ_phase_diff;
     
     wire TX_Mult_enable;
     wire VM_Mult_enable;
     wire [16:0] TX_Mult_gain;
     wire [16:0] VM_Mult_gain;
     
     wire trigger;// internal signal, needs to be buffered to an actual output
     
     reg transmission_mode;
     reg [31:0] event_frame_started_count;
     reg [31:0] event_tlast_unexpected_count;
     reg [31:0] event_tlast_missing_count;
     reg [31:0] event_fft_overflowed_count;
     
     vio_0 vio_rst (
     
       .clk (clk_global_100MHz) 
       ,.probe_in0 (event_frame_started_count)
       ,.probe_in1 (event_tlast_unexpected_count)
       ,.probe_in2 (event_tlast_missing_count)
       ,.probe_in3 (event_fft_overflowed_count)   
       
       ,.probe_in4 (TX_DAC_frequency_word)
       ,.probe_in5 (TX_DAC_initial_phase)
       ,.probe_in6 (TX_IQ_phase_diff)      
       ,.probe_in7 (TX_Mult_enable)
       ,.probe_in8 (TX_Mult_gain)
       
       ,.probe_in9 (VM_DAC_frequency_word)
       ,.probe_in10 (VM_DAC_initial_phase)
       ,.probe_in11 (VM_IQ_phase_diff)      
       ,.probe_in12 (VM_Mult_enable)
       ,.probe_in13 (VM_Mult_gain)     
       
       ,.probe_out0 (reset_vio)
       ,.probe_out1 (data_flow_en_in_vio)
       ,.probe_out2 (s_axis_config_tvalid_in_vio)
       ,.probe_out3 (transmission_mode_vio) // 1 is raw data, 0 is fft-results
       
       ,.probe_out4 (DAC_cosine_select)
       ,.probe_out5 (DAC_mem_select)
       ,.probe_out6 (Downsampling_enable) // latency = 0 when disabled, 1 when enabled   
         
     );
     
    always_ff @ (posedge clk_global_100MHz)begin
        if(reset)
            transmission_mode <= 1'b0;
        else
            transmission_mode <= (data_flow_en)? transmission_mode : (transmission_mode_vio | transmission_mode_in_buffered); // doesn't allow change mode during data flow
    end
     
    // testbench reg has timing issue, so we buffer it                 
     always_ff @ (posedge clk_global_100MHz)begin
         if(data_flow_en == 0) //turning on
            data_flow_en <= (data_flow_en_in_buffered | data_flow_en_in_vio);
         else begin
            if(data_flow_en_in_buffered | data_flow_en_in_vio)
                 data_flow_en <= 1;
            else
                 data_flow_en <= (s_axis_data_tvalid)? 1 : 0;// block the turn off it if still transmitting
         end
     end
                   
     assign reset = reset_vio | reset_buffered;
     assign s_axis_config_tvalid = s_axis_config_tvalid_in_vio | s_axis_config_tvalid_in_buffered;
    

    /*
        Cycle counter since data begin to flow
    */
    reg [31:0] cycles;
    always_ff @ (posedge clk_global_100MHz) begin
        if(reset)begin
            cycles <= 0;
        end else begin
            if(data_flow_en)begin
                cycles <= cycles + 1;
            end
        end
    end   

    
    /*
        Input stream control - stays high 1000 sample per 1100 clk cycles
    */
    wire DeserializeBuffer_enable;
    InputStreamControl 
    #(
        .DOWNSAMPLING_FACTOR(DOWNSAMPLING_FACTOR),
        .MAX_COUNT(INPUT_STREAM_MAX_COUNT),
        .ARRAY_LENGTH(INPUT_STREAM_ARRAY_LENGTH),
        .COUNTER_WIDTH(32)
    ) InputStreamControl_inst(
        .clk(clk_global_100MHz)
       ,.reset(reset)
       ,.downsample_enable(Downsampling_enable)
       ,.count_enable(data_flow_en) // when enable = 1, count will increment on the next clk pos edge
       ,.shift_enable(DeserializeBuffer_enable)
    );
    
    
    /*
        AWG Trigger
    */
    TriggerGen 
    #(
        .ARRAY_LENGTH(11_000),
        .HIGH_SAMPLES(10_000),
        .CLK_FREQ(100_000_000),
        .COUNTER_WIDTH(32)
    ) TriggerGen_inst(
         .clk(clk_global_100MHz) // Clock signal
        ,.reset(reset) // Synchronous reset
        ,.count_enable(data_flow_en)
        ,.trigger(trigger) // 11-bit counter output
    );
        
            
    /*
        playback memory as the input source emulator (non-stopping)
    */
    wire [31:0] samples;
    wire [15:0] mem_dataout, s_axis_data_tdata;
    wire mem_dataout_last, s_axis_data_tlast;
    
    // sine wave: I_data[i] = int(np.sin((i % 1024) / 40) * 8192 )
    playback_mem #
    (
        .MAX_DATA_ADDR(1100)
    ) playback_mem_inst (
        .clk(clk_global_100MHz)
       ,.reset(reset)
       ,.enable(data_flow_en) // when enable = 1, addr will increment on the next clk pos edge
       ,.samples(samples)
       ,.data(mem_dataout)
       ,.last_data(mem_dataout_last)
    );
    
    /*
        DAC
    */
    wire DAC_enable;
    wire TX_DAC_next_sample, VM_DAC_next_sample;

    wire [15:0] TX_DAC_output, TX_DAC_output_sine, TX_DAC_output_cosine; 
    wire [15:0] VM_DAC_output, VM_DAC_output_sine, VM_DAC_output_cosine; 
//    assign DAC_mem_select = 0;
//    assign DAC_initial_phase = 1;
//    assign DAC_frequency_word = 1;
    assign TX_DAC_next_sample = DeserializeBuffer_enable;
    assign VM_DAC_next_sample = DeserializeBuffer_enable;
    assign DAC_enable = data_flow_en & DeserializeBuffer_enable;
    
    // TX
    SineWaveGenerator #(
        .ADDR_WIDTH(14),
        .LUT_SIZE(16384)
    ) SineWaveGenerator_TX_inst(
         .clk(clk_global_100MHz) // Clock input, let's say it is 100MHz, and we at minimum support 1KHz, this is 100k points!
        ,.reset(reset) // Reset input
        ,.enable(DAC_enable) // Enable signal for the DAC, when is 0, the phase should reset to initial_phase
        ,.next_sample(TX_DAC_next_sample) // a one-cycle signal to update the output
        ,.frequency_word(TX_DAC_frequency_word) // This is the number of index to advance every output cycle, range 0 - 16383 (2^14-1)
        ,.initial_phase(TX_DAC_initial_phase) // Initial phase (in index), range 0 - 65535 (2^16-1)
        ,.IQ_phase_diff(TX_IQ_phase_diff)
        ,.cosine_output(TX_DAC_output_cosine)
        ,.sine_output(TX_DAC_output_sine) // Sine wave output (16-bit resolution)
    );
    
    // VM
    SineWaveGenerator #(
        .ADDR_WIDTH(14),
        .LUT_SIZE(16384)
    ) SineWaveGenerator_VM_inst(
         .clk(clk_global_100MHz) // Clock input, let's say it is 100MHz, and we at minimum support 1KHz, this is 100k points!
        ,.reset(reset) // Reset input
        ,.enable(DAC_enable) // Enable signal for the DAC, when is 0, the phase should reset to initial_phase
        ,.next_sample(VM_DAC_next_sample) // a one-cycle signal to update the output
        ,.frequency_word(VM_DAC_frequency_word) // This is the number of index to advance every output cycle, range 0 - 16383 (2^14-1)
        ,.initial_phase(VM_DAC_initial_phase) // Initial phase (in index), range 0 - 65535 (2^16-1)
        ,.IQ_phase_diff(VM_IQ_phase_diff)
        ,.cosine_output(VM_DAC_output_cosine)
        ,.sine_output(VM_DAC_output_sine) // Sine wave output (16-bit resolution)
    );
    

    /*
        Variable Gain Multiplier
    */
    // TX I and Q   
    wire [15:0] TX_VGB_out_I, TX_VGB_out_Q;

    VariableGainBuffer VariableGainBuffer_TX_I_inst(
         .data_in(TX_DAC_output_cosine)
        ,.enable(TX_Mult_enable)
        ,.gain(TX_Mult_gain)
        ,.data_out(TX_VGB_out_I)
    );   
    
    VariableGainBuffer VariableGainBuffer_TX_Q_Inst(
         .data_in(TX_DAC_output_sine)
        ,.enable(TX_Mult_enable)
        ,.gain(TX_Mult_gain)
        ,.data_out(TX_VGB_out_Q)
    );   
        
    // VM I and Q    
    wire [15:0] VM_VGB_out, VM_VGB_out_Q;

    VariableGainBuffer VariableGainBuffer_VM_I_inst(
         .data_in(VM_DAC_output_cosine)
        ,.enable(VM_Mult_enable)
        ,.gain(VM_Mult_gain)
        ,.data_out(VM_VGB_out_I)
    );   
    
    VariableGainBuffer VariableGainBuffer_VM_Q_Inst(
         .data_in(VM_DAC_output_sine)
        ,.enable(VM_Mult_enable)
        ,.gain(VM_Mult_gain)
        ,.data_out(VM_VGB_out_Q)
    );   
        
        
   /*
        Downsampling block
    */
    wire [15:0] Downsampler_in, Downsampler_out;
    assign TX_DAC_output = DAC_cosine_select? TX_VGB_out_I : TX_VGB_out_Q;
    assign Downsampler_in = DAC_mem_select ? TX_DAC_output : mem_dataout;
    
    wire sample_valid;
//    assign Downsampling_enable = 1'b1; //1=slowdown, 0=bypass
    
    Downsampler #(
        .DOWNSAMPLING_FACTOR(DOWNSAMPLING_FACTOR)
    ) Downsampler_RX_inst(
         .clk(clk_global_100MHz)       // Clock input
        ,.reset(reset)     // Asynchronous reset (active low)
        ,.enable(Downsampling_enable & data_flow_en)    // if disabled, will just keep data flowing
        ,.in(Downsampler_in) // Input data (16-bit wide)
        ,.output_valid(sample_valid)
        ,.out(Downsampler_out) // Output data (16-bit wide)
    );
            
    /*
        Deserialize the incoming data stream
    */
    
    wire [15:0] Deserialized_data [0:1000-1];
    wire Deserialized_data_valid;

    SampleDeserializeBuffer
    #(
        .ARRAY_LENGTH(1000),
        .DATA_WIDTH(16)
    ) SampleDeserializeBuffer_inst(
        .clk(clk_global_100MHz),          // Clock input
        .reset(reset),        // Reset input
        .enable(DeserializeBuffer_enable),       // when enable = 1, data_in will shift in on the next clk pos edge
        .data_in_valid(sample_valid),
        .data_in(Downsampler_out),  // 16-bit data input
        .data_out(Deserialized_data),  // 1000-sample parallel data outputs
        .data_out_valid(Deserialized_data_valid) // one cycle pulse showing the output is ready to be loaded
    );
    
    /*
        Averager
    */
    wire [15:0] Averaged_data [0:1000-1];
    wire Averaged_data_valid;
    ArrayAverager #(
       .ARRAY_LENGTH(1000),
       .NUM_AVG(NUM_AVG),
       .DATA_WIDTH(16)
    ) ArrayAverager_inst(
         .clk(clk_global_100MHz)          // Clock signal
        ,.reset(reset)        // Asynchronous reset (active high)
        ,.data_in_valid(Deserialized_data_valid)   // Data valid signal
//        ,.num_avg(4'd2) // Number of chirps to average
        ,.input_array(Deserialized_data) // Input array (1024 samples)
        ,.output_array(Averaged_data)// Averaged array (1024 samples)
        ,.data_out_valid(Averaged_data_valid)
    );
    
    /*
        Re-serialize the data (after averaging)
    */
    wire ReSerializedDataOutBegin;

    SamplePlaybackSerializeBuffer
    #(
        .INPUT_ARRAY_LENGTH(1000),
        .OUTPUT_ARRAY_LENGTH(1024),
        .DATA_WIDTH(16)
    ) SamplePlaybackSerializeBuffer_inst(
        .clk(clk_global_100MHz)          // Clock input
        ,.reset(reset)        // Reset input
        ,.data_in(Averaged_data)  // 1024 parallel data outputs
        ,.data_in_valid(Averaged_data_valid) // one cycle pulse showing the output is ready to be loaded
        ,.data_out_valid(s_axis_data_tvalid)
        ,.fft_core_tready(s_axis_data_tready) // data_out ready
        ,.new_data_out_begin(ReSerializedDataOutBegin)
        ,.data_out_last(s_axis_data_tlast)
        ,.data_out(s_axis_data_tdata) // goes into the fft module
    );
    
    
    /*
        FFT Core Instantiation
    */
    // FFT parameters
    wire [15:0] s_axis_config_tdata;
    //wire [4:0] NFFT; // NOT_USED
    //wire [6:0] CP_LEN; // NOT_USED
    wire FWD_INV;
    wire [9:0] SCALE_SCH;

    //assign NFFT = 5'b01010; // 1024 NOT_USED
    //assign CP_LEN = 7'b0; // NOT_USED
    assign FWD_INV = 1'b1; // forward
    assign SCALE_SCH = 10'b10_10_10_10_11; // [9:0] = 2,2,2,2,3, two stages share one factor
    
    assign s_axis_config_tdata = {5'b0,SCALE_SCH,FWD_INV};
    
    xfft_0 myxfft(
        .aclk(                  clk_global_100MHz       )
        ,.aclken(               1'b1                    )
        ,.aresetn(              ~reset                  )
        
        ,.s_axis_config_tdata(  s_axis_config_tdata     )
        ,.s_axis_config_tvalid( s_axis_config_tvalid    )
        ,.s_axis_config_tready( s_axis_config_tready    )
        
        ,.s_axis_data_tdata(    {16'b0, s_axis_data_tdata}       )
        ,.s_axis_data_tvalid(   s_axis_data_tvalid      )
        ,.s_axis_data_tready(   s_axis_data_tready      )
        ,.s_axis_data_tlast(    s_axis_data_tlast       )
        
        ,.m_axis_data_tdata(    m_axis_data_tdata       )
        ,.m_axis_data_tuser(    m_axis_data_tuser       )
        ,.m_axis_data_tvalid(   m_axis_data_tvalid      )
        ,.m_axis_data_tlast(    m_axis_data_tlast       )
        
        ,.m_axis_status_tdata()
        ,.m_axis_status_tvalid()
        
        ,.event_frame_started(  event_frame_started     )
        ,.event_tlast_unexpected(event_tlast_unexpected )
        ,.event_tlast_missing(  event_tlast_missing     )
        ,.event_fft_overflow(   event_fft_overflow      )
        ,.event_data_in_channel_halt( event_data_in_channel_halt )   
    );
 
// Overflow event counter

always_ff @(posedge clk_global_100MHz) begin
    if(reset) begin
        event_frame_started_count <= 0;
        event_tlast_unexpected_count <= 0;
        event_tlast_missing_count <= 0;
        event_fft_overflowed_count <= 0;      
    end else begin
        if(event_frame_started)
            event_frame_started_count <= event_frame_started_count + 1;
        if(event_tlast_unexpected)
            event_tlast_unexpected_count <= event_tlast_unexpected_count + 1;
        if(event_tlast_missing)
            event_tlast_missing_count <= event_tlast_missing_count + 1;
        if(event_fft_overflow)
            event_fft_overflowed_count <= event_fft_overflowed_count + 1;            
    end
end
    
/*
    FIFO to consume the FFT results
*/
reg [31:0] frame_counter;
reg [11:0] s_sample_counter,m_sample_counter; // count to N_SAMPLE_TO_SEND to stop fifo writing 
wire fft_result_fifo_full, fft_result_fifo_empty;
wire fft_result_fifo_write_en,fifo_rd_en;
wire raw_result_fifo_write_en;
wire [31:0] fft_result_fifo_dout;

always @(posedge clk_global_100MHz) begin
    if(reset)
        s_sample_counter <= 0;
    else if (s_axis_data_tvalid & s_axis_data_tready) //this lasts 1024 cycles
        s_sample_counter <= (s_sample_counter < N_SAMPLE_TO_SEND)? s_sample_counter + 1 : s_sample_counter;
    else if (~s_axis_data_tvalid) // don't clear during that non-ready cycle
        s_sample_counter <= 0;
end
always @(posedge clk_global_100MHz) begin
    if(reset)
        m_sample_counter <= 0;
    else if (m_axis_data_tvalid) //this lasts 1024 cycles
        m_sample_counter <= (m_sample_counter < N_SAMPLE_TO_SEND)? m_sample_counter + 1 : m_sample_counter;
    else
        m_sample_counter <= 0;
end

assign fft_result_fifo_write_en = m_axis_data_tvalid & ~fft_result_fifo_full & (frame_counter == 0) & m_sample_counter < N_SAMPLE_TO_SEND; // uart must completely offload before frame_counter reaches 0 again
assign raw_result_fifo_write_en = s_axis_data_tvalid& s_axis_data_tready & ~fft_result_fifo_full & (frame_counter == 0) & s_sample_counter < N_SAMPLE_TO_SEND; //avoid that duplicated bit

wire fifo_write_en;
assign fifo_write_en = (transmission_mode == 1'b0)? fft_result_fifo_write_en : raw_result_fifo_write_en;

wire [31:0] fifo_din;
assign fifo_din = (transmission_mode == 1'b0)? m_axis_data_tdata : {16'b0, s_axis_data_tdata};

fifo #(
    .DATA_WIDTH(32),
    .DEPTH(N_SAMPLE_TO_SEND), 
    .POINTER_WIDTH($clog2(N_SAMPLE_TO_SEND))
) fft_result_fifo_inst(
     .clk(clk_global_100MHz)
    ,. rst(reset)
    ,.wr_en(fifo_write_en)
    ,.din(fifo_din)
    ,.full(fft_result_fifo_full)    
    ,.rd_en(fifo_rd_en)
    ,.dout(fft_result_fifo_dout)
    ,.empty(fft_result_fifo_empty)
);

localparam LONG_N_WAIT_FRAME = N_WAIT_FRAME * DOWNSAMPLING_FACTOR; 
wire [31:0] frame_to_wait_val;
assign frame_to_wait_val = Downsampling_enable? N_WAIT_FRAME : LONG_N_WAIT_FRAME; // if downsampling is disabled, frame rate is higher

always @(posedge clk_global_100MHz) begin
    if(reset)
        frame_counter <= 0;
    else if (m_axis_data_tvalid & m_axis_data_tlast) //this only lasts 1 cycle per frame
        frame_counter <= (frame_counter < frame_to_wait_val-1)? frame_counter + 1 : 0;
end

/*
    UART peripherals
*/
wire uart_tx_data_ready;
wire uart_tx_data_valid;
wire [7:0] uart_tx_data;
 
uart_controller uart_controller_inst(
     .clk(clk_global_100MHz)
    ,.reset(reset)
    ,.fft_result_fifo_dout(fft_result_fifo_dout)
    ,.fifo_empty(fft_result_fifo_empty)
    ,.uart_tx_data_ready(uart_tx_data_ready)
    ,.fifo_rd_en(fifo_rd_en)
    ,.uart_tx_data_valid(uart_tx_data_valid)
    ,.uart_tx_data(uart_tx_data)
);


wire rx_fifo_wr_en,rx_fifo_rd_en;
wire rx_fifo_full, rx_fifo_empty;
wire uart_rx_data_ready;
wire uart_rx_data_valid; 
wire [7:0] rx_data_out, rx_fifo_data_out;

assign uart_rx_data_ready = ~rx_fifo_full;
assign rx_fifo_wr_en = uart_rx_data_valid && ~rx_fifo_full;

fifo #(
    .DATA_WIDTH(8),
    .DEPTH(64), 
    .POINTER_WIDTH(6)
) vio_fifo_inst(
     .clk(clk_global_100MHz)
    ,.rst(reset)
    ,.wr_en(rx_fifo_wr_en)
    ,.din(rx_data_out)
    ,.full(rx_fifo_full)    
    ,.rd_en(rx_fifo_rd_en)
    ,.dout(rx_fifo_data_out)
    ,.empty(rx_fifo_empty)
);

// This module modifies the vio using uart
mem_controller #(
    .FIFO_WIDTH(8)
) mem_controller_inst(
    .clk(clk_global_100MHz)
    ,.rst(reset)
    ,.rx_fifo_empty(rx_fifo_empty | DeserializeBuffer_enable) // both must be 0 to initiate a write
    ,.din(rx_fifo_data_out)
    ,.rx_fifo_rd_en(rx_fifo_rd_en) 
    
    ,.TX_DAC_frequency_word(TX_DAC_frequency_word)
    ,.TX_DAC_initial_phase(TX_DAC_initial_phase)
    ,.TX_IQ_phase_diff(TX_IQ_phase_diff)      
    ,.TX_Mult_enable(TX_Mult_enable)
    ,.TX_Mult_gain(TX_Mult_gain)
    ,.VM_DAC_frequency_word(VM_DAC_frequency_word)
    ,.VM_DAC_initial_phase(VM_DAC_initial_phase)
    ,.VM_IQ_phase_diff(VM_IQ_phase_diff)      
    ,.VM_Mult_enable(VM_Mult_enable)
    ,.VM_Mult_gain(VM_Mult_gain)   
);

uart #(
    .CLOCK_FREQ(CYCLES_PER_SECOND),
    .BAUD_RATE(BAUD_RATE)
)  on_chip_uart (
    .clk(clk_global_100MHz),
    .reset(reset),
    .data_in(uart_tx_data),
    .data_in_valid(uart_tx_data_valid),
    .data_in_ready(uart_tx_data_ready),
    
    .data_out(rx_data_out ),
    .data_out_valid( uart_rx_data_valid),
    .data_out_ready( uart_rx_data_ready),
    
    .serial_in(FPGA_SERIAL_RX),
    .serial_out(FPGA_SERIAL_TX)
);

endmodule
