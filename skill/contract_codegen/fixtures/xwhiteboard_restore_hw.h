// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2025.2 (64-bit)
// Tool Version Limit: 2025.11
// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// 
// ==============================================================
// control
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

#define XWHITEBOARD_RESTORE_CONTROL_ADDR_AP_CTRL             0x00
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_GIE                 0x04
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_IER                 0x08
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_ISR                 0x0c
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_AP_RETURN           0x10
#define XWHITEBOARD_RESTORE_CONTROL_BITS_AP_RETURN           32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_INPUT_R_DATA        0x18
#define XWHITEBOARD_RESTORE_CONTROL_BITS_INPUT_R_DATA        64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_OUTPUT_R_DATA       0x24
#define XWHITEBOARD_RESTORE_CONTROL_BITS_OUTPUT_R_DATA       64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_BACKGROUND_DATA     0x30
#define XWHITEBOARD_RESTORE_CONTROL_BITS_BACKGROUND_DATA     64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_PREVIOUS_DATA       0x3c
#define XWHITEBOARD_RESTORE_CONTROL_BITS_PREVIOUS_DATA       64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_PIXEL_QUIET_DATA    0x48
#define XWHITEBOARD_RESTORE_CONTROL_BITS_PIXEL_QUIET_DATA    64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_BLOCK_STATE_DATA    0x54
#define XWHITEBOARD_RESTORE_CONTROL_BITS_BLOCK_STATE_DATA    64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_ROI_DATA            0x60
#define XWHITEBOARD_RESTORE_CONTROL_BITS_ROI_DATA            64
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_WIDTH_DATA          0x6c
#define XWHITEBOARD_RESTORE_CONTROL_BITS_WIDTH_DATA          32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_HEIGHT_DATA         0x74
#define XWHITEBOARD_RESTORE_CONTROL_BITS_HEIGHT_DATA         32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_INITIALIZE_DATA     0x7c
#define XWHITEBOARD_RESTORE_CONTROL_BITS_INITIALIZE_DATA     32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_BGR_DATA            0x84
#define XWHITEBOARD_RESTORE_CONTROL_BITS_BGR_DATA            32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_DELTA_DATA          0x8c
#define XWHITEBOARD_RESTORE_CONTROL_BITS_DELTA_DATA          32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_QUIET_DELTA_DATA    0x94
#define XWHITEBOARD_RESTORE_CONTROL_BITS_QUIET_DELTA_DATA    32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_DENSE_DATA          0x9c
#define XWHITEBOARD_RESTORE_CONTROL_BITS_DENSE_DATA          32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_WEAK_THRESHOLD_DATA 0xa4
#define XWHITEBOARD_RESTORE_CONTROL_BITS_WEAK_THRESHOLD_DATA 32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_HOLD_DATA           0xac
#define XWHITEBOARD_RESTORE_CONTROL_BITS_HOLD_DATA           32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_STABLE_R_DATA       0xb4
#define XWHITEBOARD_RESTORE_CONTROL_BITS_STABLE_R_DATA       32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_QUIET_MAX_DATA      0xbc
#define XWHITEBOARD_RESTORE_CONTROL_BITS_QUIET_MAX_DATA      32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_CHALK_MIN_DATA      0xc4
#define XWHITEBOARD_RESTORE_CONTROL_BITS_CHALK_MIN_DATA      32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_CHALK_SPREAD_DATA   0xcc
#define XWHITEBOARD_RESTORE_CONTROL_BITS_CHALK_SPREAD_DATA   32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_FINE_MIN_DATA       0xd4
#define XWHITEBOARD_RESTORE_CONTROL_BITS_FINE_MIN_DATA       32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_FINE_SPREAD_DATA    0xdc
#define XWHITEBOARD_RESTORE_CONTROL_BITS_FINE_SPREAD_DATA    32
#define XWHITEBOARD_RESTORE_CONTROL_ADDR_RED_BIAS_DATA       0xe4
#define XWHITEBOARD_RESTORE_CONTROL_BITS_RED_BIAS_DATA       32

