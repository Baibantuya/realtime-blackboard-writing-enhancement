// Slow frame-rate proportional exposure controller. Sensor updates occur at frame boundary.
module ae_controller #(
    parameter [7:0] TARGET_MEAN = 8'd112,
    parameter [15:0] EXPOSURE_MIN = 16'd16,
    parameter [15:0] EXPOSURE_MAX = 16'd1759,
    parameter [7:0] GAIN_MIN = 8'd0,
    parameter [7:0] GAIN_MAX = 8'd232,
    parameter [15:0] FRAME_LENGTH = 16'd1763
) (
    input wire aclk, input wire aresetn, input wire frame_valid,
    input wire [7:0] mean_luma,
    output reg update_valid, input wire update_ready,
    output reg [15:0] coarse_integration, output reg [7:0] analog_gain
);
    wire [16:0] exposure_step_up = {1'b0,coarse_integration} + {4'b0000,coarse_integration[15:3]} + 17'd1;
    always @(posedge aclk) begin
        if (!aresetn) begin coarse_integration <= 16'd600; analog_gain <= 0; update_valid <= 0; end
        else begin
            if (update_valid && update_ready) update_valid <= 0;
            if (frame_valid && !update_valid) begin
                // Dead band ±3 DN; adjust integration first, then analogue gain.
                if (mean_luma < TARGET_MEAN - 8'd3) begin
                    if (exposure_step_up < FRAME_LENGTH-4 && exposure_step_up < EXPOSURE_MAX) coarse_integration <= exposure_step_up[15:0];
                    else if (analog_gain < GAIN_MAX-8'd8) analog_gain <= analog_gain + 8'd8;
                    else coarse_integration <= FRAME_LENGTH-4;
                    update_valid <= 1;
                end else if (mean_luma > TARGET_MEAN + 8'd3) begin
                    if (coarse_integration > EXPOSURE_MIN + (coarse_integration >> 3)) coarse_integration <= coarse_integration - (coarse_integration >> 3);
                    else if (analog_gain > GAIN_MIN+8'd8) analog_gain <= analog_gain - 8'd8;
                    else coarse_integration <= EXPOSURE_MIN;
                    update_valid <= 1;
                end
            end
        end
    end
endmodule
