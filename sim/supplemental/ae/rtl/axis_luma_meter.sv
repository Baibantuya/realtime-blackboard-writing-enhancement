`timescale 1ns/1ps

// Frame-average luma meter for RGB888 AXI4-Stream Video.
module axis_luma_meter #(
    parameter integer FRAME_PIXELS = 1920*1080,
    parameter integer PIXEL_COUNT_W = $clog2(FRAME_PIXELS + 1)
) (
    input wire aclk, input wire aresetn,
    input wire [23:0] s_tdata, input wire s_tvalid, input wire s_tuser,
    output reg frame_valid, output reg [7:0] frame_mean
);
    localparam integer SUM_W = PIXEL_COUNT_W + 8;
    localparam [SUM_W-1:0] FRAME_DIVISOR = FRAME_PIXELS;

    reg [SUM_W-1:0] sum;
    reg [PIXEL_COUNT_W-1:0] count;
    wire [15:0] y_sum = ({8'd0,s_tdata[23:16]} * 16'd77) +
                        ({8'd0,s_tdata[15:8]} * 16'd150) +
                        ({8'd0,s_tdata[7:0]} * 16'd29);
    wire [7:0] y = y_sum[15:8];
    reg [7:0] y_pipe;
    reg valid_pipe;
    reg user_pipe;
    wire [SUM_W-1:0] y_ext = {{(SUM_W-8){1'b0}}, y_pipe};
    wire [SUM_W-1:0] sum_plus_y = sum + y_ext;

    wire frame_complete = valid_pipe && !user_pipe &&
                          (count == FRAME_PIXELS-1);
    wire partial_frame_end = valid_pipe && user_pipe && (count != 0);
    wire [SUM_W-1:0] division_numerator = frame_complete ? sum_plus_y : sum;

    // frame_mean is only needed once per frame. Compute the exact 8-bit
    // quotient over eight cycles instead of placing a wide constant divider
    // on the 200 MHz pixel path.
    reg [SUM_W-1:0] div_remainder;
    reg [SUM_W-1:0] div_trial;
    reg [7:0] div_quotient;
    reg [2:0] div_bit;
    reg div_busy;
    wire start_division = (frame_complete || partial_frame_end) && !div_busy;
    wire [SUM_W:0] div_difference = {1'b0, div_remainder} -
                                      {1'b0, div_trial};
    wire div_take = !div_difference[SUM_W];

    always @(posedge aclk) begin
        if (!aresetn) begin
            sum <= 0;
            count <= 0;
            y_pipe <= 0;
            valid_pipe <= 0;
            user_pipe <= 0;
            frame_valid <= 0;
            frame_mean <= 0;
            div_remainder <= 0;
            div_trial <= 0;
            div_quotient <= 0;
            div_bit <= 0;
            div_busy <= 0;
        end else begin
            frame_valid <= 0;
            valid_pipe <= s_tvalid;
            user_pipe <= s_tuser;
            if (s_tvalid)
                y_pipe <= y;

            if (start_division) begin
                div_remainder <= division_numerator;
                div_trial <= FRAME_DIVISOR << 7;
                div_quotient <= 0;
                div_bit <= 3'd7;
                div_busy <= 1;
            end else if (div_busy) begin
                if (div_take) begin
                    div_remainder <= div_difference[SUM_W-1:0];
                    div_quotient[div_bit] <= 1'b1;
                end

                if (div_bit == 0) begin
                    frame_mean <= {div_quotient[7:1], div_take};
                    frame_valid <= 1;
                    div_busy <= 0;
                end else begin
                    div_trial <= div_trial >> 1;
                    div_bit <= div_bit - 1'b1;
                end
            end

            if (valid_pipe) begin
                if (user_pipe) begin
                    sum <= y_ext;
                    count <= 1;
                end else begin
                    sum <= sum_plus_y;
                    count <= count + 1'b1;
                    if (frame_complete) begin
                        sum <= 0;
                        count <= 0;
                    end
                end
            end
        end
    end
endmodule
