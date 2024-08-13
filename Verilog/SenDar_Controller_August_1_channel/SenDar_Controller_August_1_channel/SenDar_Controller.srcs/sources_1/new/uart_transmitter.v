// from eecs151 fa22 lab5 reference
module uart_transmitter #(
    parameter CLOCK_FREQ = 100_000_000, //250_000_000
    parameter BAUD_RATE = 115_200 // 921_600, this baud rate literally means 115200 bits per second, including start/end bits
)
(
    input clk,
    input reset,

    input [7:0] data_in,
    input data_in_valid,
    output data_in_ready,

    output serial_out
);
    // See diagram in the lab guide
    localparam  SYMBOL_EDGE_TIME    =   CLOCK_FREQ / BAUD_RATE;
    localparam  CLOCK_COUNTER_WIDTH =   16;//log2(SYMBOL_EDGE_TIME);

    wire symbol_edge;
    wire tx_running;

    reg [9:0] tx_shift;
    reg [3:0] bit_counter;
    reg [CLOCK_COUNTER_WIDTH-1:0] clock_counter;

    //--|Signal Assignments|------------------------------------------------------

    // Goes high at every symbol edge
    assign symbol_edge = (clock_counter == SYMBOL_EDGE_TIME - 1);

    // Goes high when currently receiving a character
    assign tx_running = bit_counter != 4'd0;

    // Outputs
    assign data_in_ready = !tx_running;
    assign serial_out = tx_shift[0];

    //--|Counters|----------------------------------------------------------------

    // Counts cycles until a single symbol is done
    always @ (posedge clk) begin
        clock_counter <= (data_in_valid || reset || symbol_edge) ? 0 : clock_counter + 1;
    end

    // Counts down from 10 bits for every character
    always @ (posedge clk) begin
        if (reset) begin
            bit_counter <= 4'd0;
        end else if (data_in_valid && !tx_running) begin
            bit_counter <= 4'd10;
        end else if (symbol_edge && tx_running) begin
            bit_counter <= bit_counter - 1;
        end
    end

    //--|Shift Register|-----------------------------------------------------------

    always @(posedge clk) begin
        if (reset) tx_shift <= 10'd1;
        else if (symbol_edge && tx_running) tx_shift <= {1'b1, tx_shift[9:1]};
        else if (data_in_valid) tx_shift <= {1'b1, data_in, 1'b0};
    end
endmodule