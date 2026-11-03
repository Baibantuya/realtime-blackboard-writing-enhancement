// Processing core after AMD MIPI CSI-2 RX Subsystem + Video Demosaic.
// Contract: one RGB888 pixel/beat; TUSER[0]=SOF, TLAST=EOL.
module imx219_video_core #(
    parameter integer FRAME_PIXELS=1920*1080,
    parameter integer CLK_HZ=100_000_000
) (
    input wire aclk, input wire aresetn,
    input wire [23:0] s_axis_tdata, input wire s_axis_tvalid, output wire s_axis_tready,
    input wire s_axis_tuser, input wire s_axis_tlast,
    output wire [23:0] m_axis_tdata, output wire m_axis_tvalid, input wire m_axis_tready,
    output wire m_axis_tuser, output wire m_axis_tlast,
    output wire sensor_resetn, output wire i2c_scl, inout wire i2c_sda,
    output wire sensor_init_done, output wire [7:0] measured_mean
);
    wire gamma_ready;
    wire [7:0] mean_luma;
    wire frame_valid;
    wire ae_valid, ae_ready, sensor_busy;
    wire [15:0] exposure;
    wire [7:0] gain;
    assign s_axis_tready=gamma_ready;
    assign measured_mean=mean_luma;

    axis_gamma_rgb24 gamma (
      .aclk(aclk),.aresetn(aresetn),.s_tdata(s_axis_tdata),.s_tvalid(s_axis_tvalid),.s_tready(gamma_ready),
      .s_tuser(s_axis_tuser),.s_tlast(s_axis_tlast),.m_tdata(m_axis_tdata),.m_tvalid(m_axis_tvalid),
      .m_tready(m_axis_tready),.m_tuser(m_axis_tuser),.m_tlast(m_axis_tlast));
    axis_luma_meter #(.FRAME_PIXELS(FRAME_PIXELS)) meter (
      .aclk(aclk),.aresetn(aresetn),.s_tdata(s_axis_tdata),.s_tvalid(s_axis_tvalid && gamma_ready),
      .s_tuser(s_axis_tuser),.frame_valid(frame_valid),.frame_mean(mean_luma));
    ae_controller #(.FRAME_LENGTH(16'd1763)) ae (
      .aclk(aclk),.aresetn(aresetn),.frame_valid(frame_valid),.mean_luma(mean_luma),
      .update_valid(ae_valid),.update_ready(ae_ready),.coarse_integration(exposure),.analog_gain(gain));
    assign ae_ready=sensor_init_done && !sensor_busy;
    imx219_sensor_ctrl #(.CLK_HZ(CLK_HZ)) sensor (
      .clk(aclk),.resetn(aresetn),.ae_update(ae_valid && ae_ready),.ae_exposure(exposure),.ae_gain(gain),
      .init_done(sensor_init_done),.busy(sensor_busy),.sensor_resetn(sensor_resetn),
      .i2c_scl(i2c_scl),.i2c_sda(i2c_sda));
endmodule
