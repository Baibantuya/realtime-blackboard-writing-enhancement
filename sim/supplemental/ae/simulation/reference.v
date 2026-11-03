// Frame-luma negative-feedback controller status tap for the CSI video stream.
// The stream remains untouched; PS reads a stable status word through AXI GPIO
// and applies exposure/gain with the Linux IMX219 V4L2 sensor driver. This
// avoids two I2C masters contending for the carrier PCA9546 camera channel.
// status[15:0]=coarse integration lines, [23:16]=analogue gain code,
// [31:24]=latest frame mean luma (8-bit).
module axis_ae_status_reference #(
    parameter integer FRAME_PIXELS = 1920*1080
) (
    input wire aclk,
    input wire aresetn,
    input wire [23:0] s_axis_tdata,
    input wire s_axis_tvalid,
    input wire s_axis_tready,
    input wire s_axis_tuser,
    output wire [31:0] status
);
    wire frame_valid;
    wire [7:0] mean_luma;
    wire update_valid;
    wire [15:0] exposure_lines;
    wire [7:0] analogue_gain;

    axis_luma_meter #(.FRAME_PIXELS(FRAME_PIXELS)) meter (
        .aclk(aclk),
        .aresetn(aresetn),
        .s_tdata(s_axis_tdata),
        .s_tvalid(s_axis_tvalid && s_axis_tready),
        .s_tuser(s_axis_tuser),
        .frame_valid(frame_valid),
        .frame_mean(mean_luma)
    );

    // Every update is accepted immediately. Values persist until next frame.
    ae_controller #(.FRAME_LENGTH(16'd1763)) controller (
        .aclk(aclk),
        .aresetn(aresetn),
        .frame_valid(frame_valid),
        .mean_luma(mean_luma),
        .update_valid(update_valid),
        .update_ready(1'b1),
        .coarse_integration(exposure_lines),
        .analog_gain(analogue_gain)
    );

    assign status = {mean_luma, analogue_gain, exposure_lines};
endmodule

