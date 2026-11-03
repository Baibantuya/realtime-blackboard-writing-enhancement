// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2025.2 (64-bit)
// Tool Version Limit: 2025.11
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
`timescale 1ns/1ps
(* DowngradeIPIdentifiedWarnings="yes" *) module whiteboard_restore_control_s_axi
#(parameter
    C_S_AXI_ADDR_WIDTH = 8,
    C_S_AXI_DATA_WIDTH = 32
)(
    input  wire                          ACLK,
    input  wire                          ARESET,
    input  wire                          ACLK_EN,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0] AWADDR,
    input  wire                          AWVALID,
    output wire                          AWREADY,
    input  wire [C_S_AXI_DATA_WIDTH-1:0] WDATA,
    input  wire [C_S_AXI_DATA_WIDTH/8-1:0] WSTRB,
    input  wire                          WVALID,
    output wire                          WREADY,
    output wire [1:0]                    BRESP,
    output wire                          BVALID,
    input  wire                          BREADY,
    input  wire [C_S_AXI_ADDR_WIDTH-1:0] ARADDR,
    input  wire                          ARVALID,
    output wire                          ARREADY,
    output wire [C_S_AXI_DATA_WIDTH-1:0] RDATA,
    output wire [1:0]                    RRESP,
    output wire                          RVALID,
    input  wire                          RREADY,
    output wire                          interrupt,
    output wire                          ap_start,
    input  wire                          ap_done,
    input  wire                          ap_ready,
    input  wire                          ap_idle,
    input  wire [31:0]                   ap_return,
    output wire [63:0]                   input_r,
    output wire [63:0]                   output_r,
    output wire [63:0]                   background,
    output wire [63:0]                   previous,
    output wire [63:0]                   pixel_quiet,
    output wire [63:0]                   block_state,
    output wire [63:0]                   roi,
    output wire [31:0]                   width,
    output wire [31:0]                   height,
    output wire [31:0]                   initialize,
    output wire [31:0]                   bgr,
    output wire [31:0]                   delta,
    output wire [31:0]                   quiet_delta,
    output wire [31:0]                   dense,
    output wire [31:0]                   weak_threshold,
    output wire [31:0]                   hold,
    output wire [31:0]                   stable_r,
    output wire [31:0]                   quiet_max,
    output wire [31:0]                   chalk_min,
    output wire [31:0]                   chalk_spread,
    output wire [31:0]                   fine_min,
    output wire [31:0]                   fine_spread,
    output wire [31:0]                   red_bias
);
//------------------------Address Info-------------------
// Protocol Used: ap_ctrl_hs
//
// 0x00 : Control signals
//        bit 0  - ap_start (Read/Write/COH)
//        bit 1  - ap_done (Read/COR)
//        bit 2  - ap_idle (Read)
//        bit 3  - ap_ready (Read/COR)
//        bit 7  - auto_restart (Read/Write)
//        bit 9  - interrupt (Read)
//        others - reserved
// 0x04 : Global Interrupt Enable Register
//        bit 0  - Global Interrupt Enable (Read/Write)
//        others - reserved
// 0x08 : IP Interrupt Enable Register (Read/Write)
//        bit 0 - enable ap_done interrupt (Read/Write)
//        bit 1 - enable ap_ready interrupt (Read/Write)
//        others - reserved
// 0x0c : IP Interrupt Status Register (Read/TOW)
//        bit 0 - ap_done (Read/TOW)
//        bit 1 - ap_ready (Read/TOW)
//        others - reserved
// 0x10 : Data signal of ap_return
//        bit 31~0 - ap_return[31:0] (Read)
// 0x18 : Data signal of input_r
//        bit 31~0 - input_r[31:0] (Read/Write)
// 0x1c : Data signal of input_r
//        bit 31~0 - input_r[63:32] (Read/Write)
// 0x20 : reserved
// 0x24 : Data signal of output_r
//        bit 31~0 - output_r[31:0] (Read/Write)
// 0x28 : Data signal of output_r
//        bit 31~0 - output_r[63:32] (Read/Write)
// 0x2c : reserved
// 0x30 : Data signal of background
//        bit 31~0 - background[31:0] (Read/Write)
// 0x34 : Data signal of background
//        bit 31~0 - background[63:32] (Read/Write)
// 0x38 : reserved
// 0x3c : Data signal of previous
//        bit 31~0 - previous[31:0] (Read/Write)
// 0x40 : Data signal of previous
//        bit 31~0 - previous[63:32] (Read/Write)
// 0x44 : reserved
// 0x48 : Data signal of pixel_quiet
//        bit 31~0 - pixel_quiet[31:0] (Read/Write)
// 0x4c : Data signal of pixel_quiet
//        bit 31~0 - pixel_quiet[63:32] (Read/Write)
// 0x50 : reserved
// 0x54 : Data signal of block_state
//        bit 31~0 - block_state[31:0] (Read/Write)
// 0x58 : Data signal of block_state
//        bit 31~0 - block_state[63:32] (Read/Write)
// 0x5c : reserved
// 0x60 : Data signal of roi
//        bit 31~0 - roi[31:0] (Read/Write)
// 0x64 : Data signal of roi
//        bit 31~0 - roi[63:32] (Read/Write)
// 0x68 : reserved
// 0x6c : Data signal of width
//        bit 31~0 - width[31:0] (Read/Write)
// 0x70 : reserved
// 0x74 : Data signal of height
//        bit 31~0 - height[31:0] (Read/Write)
// 0x78 : reserved
// 0x7c : Data signal of initialize
//        bit 31~0 - initialize[31:0] (Read/Write)
// 0x80 : reserved
// 0x84 : Data signal of bgr
//        bit 31~0 - bgr[31:0] (Read/Write)
// 0x88 : reserved
// 0x8c : Data signal of delta
//        bit 31~0 - delta[31:0] (Read/Write)
// 0x90 : reserved
// 0x94 : Data signal of quiet_delta
//        bit 31~0 - quiet_delta[31:0] (Read/Write)
// 0x98 : reserved
// 0x9c : Data signal of dense
//        bit 31~0 - dense[31:0] (Read/Write)
// 0xa0 : reserved
// 0xa4 : Data signal of weak_threshold
//        bit 31~0 - weak_threshold[31:0] (Read/Write)
// 0xa8 : reserved
// 0xac : Data signal of hold
//        bit 31~0 - hold[31:0] (Read/Write)
// 0xb0 : reserved
// 0xb4 : Data signal of stable_r
//        bit 31~0 - stable_r[31:0] (Read/Write)
// 0xb8 : reserved
// 0xbc : Data signal of quiet_max
//        bit 31~0 - quiet_max[31:0] (Read/Write)
// 0xc0 : reserved
// 0xc4 : Data signal of chalk_min
//        bit 31~0 - chalk_min[31:0] (Read/Write)
// 0xc8 : reserved
// 0xcc : Data signal of chalk_spread
//        bit 31~0 - chalk_spread[31:0] (Read/Write)
// 0xd0 : reserved
// 0xd4 : Data signal of fine_min
//        bit 31~0 - fine_min[31:0] (Read/Write)
// 0xd8 : reserved
// 0xdc : Data signal of fine_spread
//        bit 31~0 - fine_spread[31:0] (Read/Write)
// 0xe0 : reserved
// 0xe4 : Data signal of red_bias
//        bit 31~0 - red_bias[31:0] (Read/Write)
// 0xe8 : reserved
// (SC = Self Clear, COR = Clear on Read, TOW = Toggle on Write, COH = Clear on Handshake)

//------------------------Parameter----------------------
localparam
    ADDR_AP_CTRL               = 8'h00,
    ADDR_GIE                   = 8'h04,
    ADDR_IER                   = 8'h08,
    ADDR_ISR                   = 8'h0c,
    ADDR_AP_RETURN_0           = 8'h10,
    ADDR_INPUT_R_DATA_0        = 8'h18,
    ADDR_INPUT_R_DATA_1        = 8'h1c,
    ADDR_INPUT_R_CTRL          = 8'h20,
    ADDR_OUTPUT_R_DATA_0       = 8'h24,
    ADDR_OUTPUT_R_DATA_1       = 8'h28,
    ADDR_OUTPUT_R_CTRL         = 8'h2c,
    ADDR_BACKGROUND_DATA_0     = 8'h30,
    ADDR_BACKGROUND_DATA_1     = 8'h34,
    ADDR_BACKGROUND_CTRL       = 8'h38,
    ADDR_PREVIOUS_DATA_0       = 8'h3c,
    ADDR_PREVIOUS_DATA_1       = 8'h40,
    ADDR_PREVIOUS_CTRL         = 8'h44,
    ADDR_PIXEL_QUIET_DATA_0    = 8'h48,
    ADDR_PIXEL_QUIET_DATA_1    = 8'h4c,
    ADDR_PIXEL_QUIET_CTRL      = 8'h50,
    ADDR_BLOCK_STATE_DATA_0    = 8'h54,
    ADDR_BLOCK_STATE_DATA_1    = 8'h58,
    ADDR_BLOCK_STATE_CTRL      = 8'h5c,
    ADDR_ROI_DATA_0            = 8'h60,
    ADDR_ROI_DATA_1            = 8'h64,
    ADDR_ROI_CTRL              = 8'h68,
    ADDR_WIDTH_DATA_0          = 8'h6c,
    ADDR_WIDTH_CTRL            = 8'h70,
    ADDR_HEIGHT_DATA_0         = 8'h74,
    ADDR_HEIGHT_CTRL           = 8'h78,
    ADDR_INITIALIZE_DATA_0     = 8'h7c,
    ADDR_INITIALIZE_CTRL       = 8'h80,
    ADDR_BGR_DATA_0            = 8'h84,
    ADDR_BGR_CTRL              = 8'h88,
    ADDR_DELTA_DATA_0          = 8'h8c,
    ADDR_DELTA_CTRL            = 8'h90,
    ADDR_QUIET_DELTA_DATA_0    = 8'h94,
    ADDR_QUIET_DELTA_CTRL      = 8'h98,
    ADDR_DENSE_DATA_0          = 8'h9c,
    ADDR_DENSE_CTRL            = 8'ha0,
    ADDR_WEAK_THRESHOLD_DATA_0 = 8'ha4,
    ADDR_WEAK_THRESHOLD_CTRL   = 8'ha8,
    ADDR_HOLD_DATA_0           = 8'hac,
    ADDR_HOLD_CTRL             = 8'hb0,
    ADDR_STABLE_R_DATA_0       = 8'hb4,
    ADDR_STABLE_R_CTRL         = 8'hb8,
    ADDR_QUIET_MAX_DATA_0      = 8'hbc,
    ADDR_QUIET_MAX_CTRL        = 8'hc0,
    ADDR_CHALK_MIN_DATA_0      = 8'hc4,
    ADDR_CHALK_MIN_CTRL        = 8'hc8,
    ADDR_CHALK_SPREAD_DATA_0   = 8'hcc,
    ADDR_CHALK_SPREAD_CTRL     = 8'hd0,
    ADDR_FINE_MIN_DATA_0       = 8'hd4,
    ADDR_FINE_MIN_CTRL         = 8'hd8,
    ADDR_FINE_SPREAD_DATA_0    = 8'hdc,
    ADDR_FINE_SPREAD_CTRL      = 8'he0,
    ADDR_RED_BIAS_DATA_0       = 8'he4,
    ADDR_RED_BIAS_CTRL         = 8'he8,
    WRIDLE                     = 2'd0,
    WRDATA                     = 2'd1,
    WRRESP                     = 2'd2,
    WRRESET                    = 2'd3,
    RDIDLE                     = 2'd0,
    RDDATA                     = 2'd1,
    RDRESET                    = 2'd2,
    ADDR_BITS                = 8;

//------------------------Local signal-------------------
    reg  [1:0]                    wstate = WRRESET;
    reg  [1:0]                    wnext;
    reg  [ADDR_BITS-1:0]          waddr;
    wire [C_S_AXI_DATA_WIDTH-1:0] wmask;
    wire                          aw_hs;
    wire                          w_hs;
    reg  [1:0]                    rstate = RDRESET;
    reg  [1:0]                    rnext;
    reg  [C_S_AXI_DATA_WIDTH-1:0] rdata;
    wire                          ar_hs;
    wire [ADDR_BITS-1:0]          raddr;
    // internal registers
    reg                           int_ap_idle = 1'b0;
    reg                           int_ap_ready = 1'b0;
    wire                          task_ap_ready;
    reg                           int_ap_done = 1'b0;
    wire                          task_ap_done;
    reg                           int_task_ap_done = 1'b0;
    reg                           int_ap_start = 1'b0;
    reg                           int_interrupt = 1'b0;
    reg                           int_auto_restart = 1'b0;
    reg                           auto_restart_status = 1'b0;
    wire                          auto_restart_done;
    reg                           int_gie = 1'b0;
    reg  [1:0]                    int_ier = 2'b0;
    reg  [1:0]                    int_isr = 2'b0;
    reg  [31:0]                   int_ap_return;
    reg  [63:0]                   int_input_r = 'b0;
    reg  [63:0]                   int_output_r = 'b0;
    reg  [63:0]                   int_background = 'b0;
    reg  [63:0]                   int_previous = 'b0;
    reg  [63:0]                   int_pixel_quiet = 'b0;
    reg  [63:0]                   int_block_state = 'b0;
    reg  [63:0]                   int_roi = 'b0;
    reg  [31:0]                   int_width = 'b0;
    reg  [31:0]                   int_height = 'b0;
    reg  [31:0]                   int_initialize = 'b0;
    reg  [31:0]                   int_bgr = 'b0;
    reg  [31:0]                   int_delta = 'b0;
    reg  [31:0]                   int_quiet_delta = 'b0;
    reg  [31:0]                   int_dense = 'b0;
    reg  [31:0]                   int_weak_threshold = 'b0;
    reg  [31:0]                   int_hold = 'b0;
    reg  [31:0]                   int_stable_r = 'b0;
    reg  [31:0]                   int_quiet_max = 'b0;
    reg  [31:0]                   int_chalk_min = 'b0;
    reg  [31:0]                   int_chalk_spread = 'b0;
    reg  [31:0]                   int_fine_min = 'b0;
    reg  [31:0]                   int_fine_spread = 'b0;
    reg  [31:0]                   int_red_bias = 'b0;

//------------------------Instantiation------------------


//------------------------AXI write fsm------------------
assign AWREADY = (wstate == WRIDLE);
assign WREADY  = (wstate == WRDATA);
assign BVALID  = (wstate == WRRESP);
assign BRESP   = 2'b00;  // OKAY
assign wmask   = { {8{WSTRB[3]}}, {8{WSTRB[2]}}, {8{WSTRB[1]}}, {8{WSTRB[0]}} };
assign aw_hs   = AWVALID & AWREADY;
assign w_hs    = WVALID & WREADY;

// wstate
always @(posedge ACLK) begin
    if (ARESET)
        wstate <= WRRESET;
    else if (ACLK_EN)
        wstate <= wnext;
end

// wnext
always @(*) begin
    case (wstate)
        WRIDLE:
            if (AWVALID)
                wnext = WRDATA;
            else
                wnext = WRIDLE;
        WRDATA:
            if (WVALID)
                wnext = WRRESP;
            else
                wnext = WRDATA;
        WRRESP:
            if (BREADY & BVALID)
                wnext = WRIDLE;
            else
                wnext = WRRESP;
        default:
            wnext = WRIDLE;
    endcase
end

// waddr
always @(posedge ACLK) begin
    if (ACLK_EN) begin
        if (aw_hs)
            waddr <= {AWADDR[ADDR_BITS-1:2], {2{1'b0}}};
    end
end

//------------------------AXI read fsm-------------------
assign ARREADY = (rstate == RDIDLE);
assign RDATA   = rdata;
assign RRESP   = 2'b00;  // OKAY
assign RVALID  = (rstate == RDDATA);
assign ar_hs   = ARVALID & ARREADY;
assign raddr   = ARADDR[ADDR_BITS-1:0];

// rstate
always @(posedge ACLK) begin
    if (ARESET)
        rstate <= RDRESET;
    else if (ACLK_EN)
        rstate <= rnext;
end

// rnext
always @(*) begin
    case (rstate)
        RDIDLE:
            if (ARVALID)
                rnext = RDDATA;
            else
                rnext = RDIDLE;
        RDDATA:
            if (RREADY & RVALID)
                rnext = RDIDLE;
            else
                rnext = RDDATA;
        default:
            rnext = RDIDLE;
    endcase
end

// rdata
always @(posedge ACLK) begin
    if (ACLK_EN) begin
        if (ar_hs) begin
            rdata <= 'b0;
            case (raddr)
                ADDR_AP_CTRL: begin
                    rdata[0] <= int_ap_start;
                    rdata[1] <= int_task_ap_done;
                    rdata[2] <= int_ap_idle;
                    rdata[3] <= int_ap_ready;
                    rdata[7] <= int_auto_restart;
                    rdata[9] <= int_interrupt;
                end
                ADDR_GIE: begin
                    rdata <= int_gie;
                end
                ADDR_IER: begin
                    rdata <= int_ier;
                end
                ADDR_ISR: begin
                    rdata <= int_isr;
                end
                ADDR_AP_RETURN_0: begin
                    rdata <= int_ap_return[31:0];
                end
                ADDR_INPUT_R_DATA_0: begin
                    rdata <= int_input_r[31:0];
                end
                ADDR_INPUT_R_DATA_1: begin
                    rdata <= int_input_r[63:32];
                end
                ADDR_OUTPUT_R_DATA_0: begin
                    rdata <= int_output_r[31:0];
                end
                ADDR_OUTPUT_R_DATA_1: begin
                    rdata <= int_output_r[63:32];
                end
                ADDR_BACKGROUND_DATA_0: begin
                    rdata <= int_background[31:0];
                end
                ADDR_BACKGROUND_DATA_1: begin
                    rdata <= int_background[63:32];
                end
                ADDR_PREVIOUS_DATA_0: begin
                    rdata <= int_previous[31:0];
                end
                ADDR_PREVIOUS_DATA_1: begin
                    rdata <= int_previous[63:32];
                end
                ADDR_PIXEL_QUIET_DATA_0: begin
                    rdata <= int_pixel_quiet[31:0];
                end
                ADDR_PIXEL_QUIET_DATA_1: begin
                    rdata <= int_pixel_quiet[63:32];
                end
                ADDR_BLOCK_STATE_DATA_0: begin
                    rdata <= int_block_state[31:0];
                end
                ADDR_BLOCK_STATE_DATA_1: begin
                    rdata <= int_block_state[63:32];
                end
                ADDR_ROI_DATA_0: begin
                    rdata <= int_roi[31:0];
                end
                ADDR_ROI_DATA_1: begin
                    rdata <= int_roi[63:32];
                end
                ADDR_WIDTH_DATA_0: begin
                    rdata <= int_width[31:0];
                end
                ADDR_HEIGHT_DATA_0: begin
                    rdata <= int_height[31:0];
                end
                ADDR_INITIALIZE_DATA_0: begin
                    rdata <= int_initialize[31:0];
                end
                ADDR_BGR_DATA_0: begin
                    rdata <= int_bgr[31:0];
                end
                ADDR_DELTA_DATA_0: begin
                    rdata <= int_delta[31:0];
                end
                ADDR_QUIET_DELTA_DATA_0: begin
                    rdata <= int_quiet_delta[31:0];
                end
                ADDR_DENSE_DATA_0: begin
                    rdata <= int_dense[31:0];
                end
                ADDR_WEAK_THRESHOLD_DATA_0: begin
                    rdata <= int_weak_threshold[31:0];
                end
                ADDR_HOLD_DATA_0: begin
                    rdata <= int_hold[31:0];
                end
                ADDR_STABLE_R_DATA_0: begin
                    rdata <= int_stable_r[31:0];
                end
                ADDR_QUIET_MAX_DATA_0: begin
                    rdata <= int_quiet_max[31:0];
                end
                ADDR_CHALK_MIN_DATA_0: begin
                    rdata <= int_chalk_min[31:0];
                end
                ADDR_CHALK_SPREAD_DATA_0: begin
                    rdata <= int_chalk_spread[31:0];
                end
                ADDR_FINE_MIN_DATA_0: begin
                    rdata <= int_fine_min[31:0];
                end
                ADDR_FINE_SPREAD_DATA_0: begin
                    rdata <= int_fine_spread[31:0];
                end
                ADDR_RED_BIAS_DATA_0: begin
                    rdata <= int_red_bias[31:0];
                end
            endcase
        end
    end
end


//------------------------Register logic-----------------
assign interrupt         = int_interrupt;
assign ap_start          = int_ap_start;
assign task_ap_done      = (ap_done && !auto_restart_status) || auto_restart_done;
assign task_ap_ready     = ap_ready && !int_auto_restart;
assign auto_restart_done = auto_restart_status && (ap_idle && !int_ap_idle);
assign input_r           = int_input_r;
assign output_r          = int_output_r;
assign background        = int_background;
assign previous          = int_previous;
assign pixel_quiet       = int_pixel_quiet;
assign block_state       = int_block_state;
assign roi               = int_roi;
assign width             = int_width;
assign height            = int_height;
assign initialize        = int_initialize;
assign bgr               = int_bgr;
assign delta             = int_delta;
assign quiet_delta       = int_quiet_delta;
assign dense             = int_dense;
assign weak_threshold    = int_weak_threshold;
assign hold              = int_hold;
assign stable_r          = int_stable_r;
assign quiet_max         = int_quiet_max;
assign chalk_min         = int_chalk_min;
assign chalk_spread      = int_chalk_spread;
assign fine_min          = int_fine_min;
assign fine_spread       = int_fine_spread;
assign red_bias          = int_red_bias;
// int_interrupt
always @(posedge ACLK) begin
    if (ARESET)
        int_interrupt <= 1'b0;
    else if (ACLK_EN) begin
        if (int_gie && (|int_isr))
            int_interrupt <= 1'b1;
        else
            int_interrupt <= 1'b0;
    end
end

// int_ap_start
always @(posedge ACLK) begin
    if (ARESET)
        int_ap_start <= 1'b0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_AP_CTRL && WSTRB[0] && WDATA[0])
            int_ap_start <= 1'b1;
        else if (ap_ready)
            int_ap_start <= int_auto_restart; // clear on handshake/auto restart
    end
end

// int_ap_done
always @(posedge ACLK) begin
    if (ARESET)
        int_ap_done <= 1'b0;
    else if (ACLK_EN) begin
            int_ap_done <= ap_done;
    end
end

// int_task_ap_done
always @(posedge ACLK) begin
    if (ARESET)
        int_task_ap_done <= 1'b0;
    else if (ACLK_EN) begin
        if (task_ap_done)
            int_task_ap_done <= 1'b1;
        else if (ar_hs && raddr == ADDR_AP_CTRL)
            int_task_ap_done <= 1'b0; // clear on read
    end
end

// int_ap_idle
always @(posedge ACLK) begin
    if (ARESET)
        int_ap_idle <= 1'b0;
    else if (ACLK_EN) begin
            int_ap_idle <= ap_idle;
    end
end

// int_ap_ready
always @(posedge ACLK) begin
    if (ARESET)
        int_ap_ready <= 1'b0;
    else if (ACLK_EN) begin
        if (task_ap_ready)
            int_ap_ready <= 1'b1;
        else if (ar_hs && raddr == ADDR_AP_CTRL)
            int_ap_ready <= 1'b0;
    end
end

// int_auto_restart
always @(posedge ACLK) begin
    if (ARESET)
        int_auto_restart <= 1'b0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_AP_CTRL && WSTRB[0])
            int_auto_restart <= WDATA[7];
    end
end

// auto_restart_status
always @(posedge ACLK) begin
    if (ARESET)
        auto_restart_status <= 1'b0;
    else if (ACLK_EN) begin
        if (int_auto_restart)
            auto_restart_status <= 1'b1;
        else if (ap_idle)
            auto_restart_status <= 1'b0;
    end
end

// int_gie
always @(posedge ACLK) begin
    if (ARESET)
        int_gie <= 1'b0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_GIE && WSTRB[0])
            int_gie <= WDATA[0];
    end
end

// int_ier
always @(posedge ACLK) begin
    if (ARESET)
        int_ier <= 1'b0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_IER && WSTRB[0])
            int_ier <= WDATA[1:0];
    end
end

// int_isr[0]
always @(posedge ACLK) begin
    if (ARESET)
        int_isr[0] <= 1'b0;
    else if (ACLK_EN) begin
        if (int_ier[0] & ap_done)
            int_isr[0] <= 1'b1;
        else if (w_hs && waddr == ADDR_ISR && WSTRB[0])
            int_isr[0] <= int_isr[0] ^ WDATA[0]; // toggle on write
    end
end

// int_isr[1]
always @(posedge ACLK) begin
    if (ARESET)
        int_isr[1] <= 1'b0;
    else if (ACLK_EN) begin
        if (int_ier[1] & ap_ready)
            int_isr[1] <= 1'b1;
        else if (w_hs && waddr == ADDR_ISR && WSTRB[0])
            int_isr[1] <= int_isr[1] ^ WDATA[1]; // toggle on write
    end
end

// int_ap_return
always @(posedge ACLK) begin
    if (ARESET)
        int_ap_return <= 0;
    else if (ACLK_EN) begin
        if (ap_done)
            int_ap_return <= ap_return;
    end
end

// int_input_r[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_input_r[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_INPUT_R_DATA_0)
            int_input_r[31:0] <= (WDATA[31:0] & wmask) | (int_input_r[31:0] & ~wmask);
    end
end

// int_input_r[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_input_r[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_INPUT_R_DATA_1)
            int_input_r[63:32] <= (WDATA[31:0] & wmask) | (int_input_r[63:32] & ~wmask);
    end
end

// int_output_r[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_output_r[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_OUTPUT_R_DATA_0)
            int_output_r[31:0] <= (WDATA[31:0] & wmask) | (int_output_r[31:0] & ~wmask);
    end
end

// int_output_r[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_output_r[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_OUTPUT_R_DATA_1)
            int_output_r[63:32] <= (WDATA[31:0] & wmask) | (int_output_r[63:32] & ~wmask);
    end
end

// int_background[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_background[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_BACKGROUND_DATA_0)
            int_background[31:0] <= (WDATA[31:0] & wmask) | (int_background[31:0] & ~wmask);
    end
end

// int_background[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_background[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_BACKGROUND_DATA_1)
            int_background[63:32] <= (WDATA[31:0] & wmask) | (int_background[63:32] & ~wmask);
    end
end

// int_previous[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_previous[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_PREVIOUS_DATA_0)
            int_previous[31:0] <= (WDATA[31:0] & wmask) | (int_previous[31:0] & ~wmask);
    end
end

// int_previous[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_previous[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_PREVIOUS_DATA_1)
            int_previous[63:32] <= (WDATA[31:0] & wmask) | (int_previous[63:32] & ~wmask);
    end
end

// int_pixel_quiet[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_pixel_quiet[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_PIXEL_QUIET_DATA_0)
            int_pixel_quiet[31:0] <= (WDATA[31:0] & wmask) | (int_pixel_quiet[31:0] & ~wmask);
    end
end

// int_pixel_quiet[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_pixel_quiet[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_PIXEL_QUIET_DATA_1)
            int_pixel_quiet[63:32] <= (WDATA[31:0] & wmask) | (int_pixel_quiet[63:32] & ~wmask);
    end
end

// int_block_state[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_block_state[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_BLOCK_STATE_DATA_0)
            int_block_state[31:0] <= (WDATA[31:0] & wmask) | (int_block_state[31:0] & ~wmask);
    end
end

// int_block_state[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_block_state[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_BLOCK_STATE_DATA_1)
            int_block_state[63:32] <= (WDATA[31:0] & wmask) | (int_block_state[63:32] & ~wmask);
    end
end

// int_roi[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_roi[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_ROI_DATA_0)
            int_roi[31:0] <= (WDATA[31:0] & wmask) | (int_roi[31:0] & ~wmask);
    end
end

// int_roi[63:32]
always @(posedge ACLK) begin
    if (ARESET)
        int_roi[63:32] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_ROI_DATA_1)
            int_roi[63:32] <= (WDATA[31:0] & wmask) | (int_roi[63:32] & ~wmask);
    end
end

// int_width[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_width[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_WIDTH_DATA_0)
            int_width[31:0] <= (WDATA[31:0] & wmask) | (int_width[31:0] & ~wmask);
    end
end

// int_height[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_height[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_HEIGHT_DATA_0)
            int_height[31:0] <= (WDATA[31:0] & wmask) | (int_height[31:0] & ~wmask);
    end
end

// int_initialize[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_initialize[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_INITIALIZE_DATA_0)
            int_initialize[31:0] <= (WDATA[31:0] & wmask) | (int_initialize[31:0] & ~wmask);
    end
end

// int_bgr[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_bgr[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_BGR_DATA_0)
            int_bgr[31:0] <= (WDATA[31:0] & wmask) | (int_bgr[31:0] & ~wmask);
    end
end

// int_delta[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_delta[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_DELTA_DATA_0)
            int_delta[31:0] <= (WDATA[31:0] & wmask) | (int_delta[31:0] & ~wmask);
    end
end

// int_quiet_delta[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_quiet_delta[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_QUIET_DELTA_DATA_0)
            int_quiet_delta[31:0] <= (WDATA[31:0] & wmask) | (int_quiet_delta[31:0] & ~wmask);
    end
end

// int_dense[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_dense[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_DENSE_DATA_0)
            int_dense[31:0] <= (WDATA[31:0] & wmask) | (int_dense[31:0] & ~wmask);
    end
end

// int_weak_threshold[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_weak_threshold[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_WEAK_THRESHOLD_DATA_0)
            int_weak_threshold[31:0] <= (WDATA[31:0] & wmask) | (int_weak_threshold[31:0] & ~wmask);
    end
end

// int_hold[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_hold[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_HOLD_DATA_0)
            int_hold[31:0] <= (WDATA[31:0] & wmask) | (int_hold[31:0] & ~wmask);
    end
end

// int_stable_r[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_stable_r[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_STABLE_R_DATA_0)
            int_stable_r[31:0] <= (WDATA[31:0] & wmask) | (int_stable_r[31:0] & ~wmask);
    end
end

// int_quiet_max[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_quiet_max[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_QUIET_MAX_DATA_0)
            int_quiet_max[31:0] <= (WDATA[31:0] & wmask) | (int_quiet_max[31:0] & ~wmask);
    end
end

// int_chalk_min[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_chalk_min[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_CHALK_MIN_DATA_0)
            int_chalk_min[31:0] <= (WDATA[31:0] & wmask) | (int_chalk_min[31:0] & ~wmask);
    end
end

// int_chalk_spread[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_chalk_spread[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_CHALK_SPREAD_DATA_0)
            int_chalk_spread[31:0] <= (WDATA[31:0] & wmask) | (int_chalk_spread[31:0] & ~wmask);
    end
end

// int_fine_min[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_fine_min[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_FINE_MIN_DATA_0)
            int_fine_min[31:0] <= (WDATA[31:0] & wmask) | (int_fine_min[31:0] & ~wmask);
    end
end

// int_fine_spread[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_fine_spread[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_FINE_SPREAD_DATA_0)
            int_fine_spread[31:0] <= (WDATA[31:0] & wmask) | (int_fine_spread[31:0] & ~wmask);
    end
end

// int_red_bias[31:0]
always @(posedge ACLK) begin
    if (ARESET)
        int_red_bias[31:0] <= 0;
    else if (ACLK_EN) begin
        if (w_hs && waddr == ADDR_RED_BIAS_DATA_0)
            int_red_bias[31:0] <= (WDATA[31:0] & wmask) | (int_red_bias[31:0] & ~wmask);
    end
end

//synthesis translate_off
always @(posedge ACLK) begin
    if (ACLK_EN) begin
        if (int_gie & ~int_isr[0] & int_ier[0] & ap_done)
            $display ("// Interrupt Monitor : interrupt for ap_done detected @ \"%0t\"", $time);
        if (int_gie & ~int_isr[1] & int_ier[1] & ap_ready)
            $display ("// Interrupt Monitor : interrupt for ap_ready detected @ \"%0t\"", $time);
    end
end
//synthesis translate_on

//------------------------Memory logic-------------------

endmodule
