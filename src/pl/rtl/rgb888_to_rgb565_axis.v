`timescale 1ns/1ps
// Continuous, storage-free AXIS formatter. UG934 input R:B:G, one pixel/beat.
// Low 16 bits carry little-endian RGB565; vendor YUYV8 stores Y/UV bytes verbatim.
module rgb888_to_rgb565_axis (
 (* X_INTERFACE_INFO="xilinx.com:signal:clock:1.0 aclk CLK",
    X_INTERFACE_PARAMETER="ASSOCIATED_BUSIF s_axis_video:m_axis_video, ASSOCIATED_RESET aresetn" *) input wire aclk,
 (* X_INTERFACE_INFO="xilinx.com:signal:reset:1.0 aresetn RST",
    X_INTERFACE_PARAMETER="POLARITY ACTIVE_LOW" *) input wire aresetn,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 s_axis_video TDATA" *) input wire [23:0] s_axis_tdata,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 s_axis_video TVALID" *) input wire s_axis_tvalid,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 s_axis_video TREADY" *) output wire s_axis_tready,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 s_axis_video TLAST" *) input wire s_axis_tlast,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 s_axis_video TUSER" *) input wire s_axis_tuser,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 m_axis_video TDATA" *) output wire [23:0] m_axis_tdata,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 m_axis_video TVALID" *) output wire m_axis_tvalid,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 m_axis_video TREADY" *) input wire m_axis_tready,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 m_axis_video TLAST" *) output wire m_axis_tlast,
 (* X_INTERFACE_INFO="xilinx.com:interface:axis:1.0 m_axis_video TUSER" *) output wire m_axis_tuser
);
 assign m_axis_tdata={8'd0,s_axis_tdata[23:19],s_axis_tdata[7:2],s_axis_tdata[15:11]};
 assign m_axis_tvalid=s_axis_tvalid && aresetn;
 assign s_axis_tready=m_axis_tready && aresetn;
 assign m_axis_tlast=s_axis_tlast;
 assign m_axis_tuser=s_axis_tuser;
endmodule
