// ==============================================================
// Vitis HLS - High-Level Synthesis from C, C++ and OpenCL v2021.2 (64-bit)
// Copyright 1986-2021 Xilinx, Inc. All Rights Reserved.
// ==============================================================
// control
// 0x00 : Control signals
//        bit 0  - ap_start (Read/Write/COH)
//        bit 1  - ap_done (Read/COR)
//        bit 2  - ap_idle (Read)
//        bit 3  - ap_ready (Read/COR)
//        bit 7  - auto_restart (Read/Write)
//        others - reserved
// 0x04 : Global Interrupt Enable Register
//        bit 0  - Global Interrupt Enable (Read/Write)
//        others - reserved
// 0x08 : IP Interrupt Enable Register (Read/Write)
//        bit 0 - enable ap_done interrupt (Read/Write)
//        bit 1 - enable ap_ready interrupt (Read/Write)
//        bit 5 - enable ap_local_deadlock interrupt (Read/Write)
//        others - reserved
// 0x0c : IP Interrupt Status Register (Read/TOW)
//        bit 0 - ap_done (COR/TOW)
//        bit 1 - ap_ready (COR/TOW)
//        bit 5 - ap_local_deadlock (COR/TOW)
//        others - reserved
// 0x10 : Data signal of ap_return
//        bit 31~0 - ap_return[31:0] (Read)
// 0x18 : Data signal of src
//        bit 31~0 - src[31:0] (Read/Write)
// 0x1c : reserved
// 0x20 : Data signal of canvas_in
//        bit 31~0 - canvas_in[31:0] (Read/Write)
// 0x24 : reserved
// 0x28 : Data signal of canvas_out
//        bit 31~0 - canvas_out[31:0] (Read/Write)
// 0x2c : reserved
// 0x30 : Data signal of metadata
//        bit 31~0 - metadata[31:0] (Read/Write)
// 0x34 : reserved
// 0x38 : Data signal of dst
//        bit 31~0 - dst[31:0] (Read/Write)
// 0x3c : reserved
// 0x40 : Data signal of width
//        bit 31~0 - width[31:0] (Read/Write)
// 0x44 : reserved
// 0x48 : Data signal of height
//        bit 31~0 - height[31:0] (Read/Write)
// 0x4c : reserved
// 0x50 : Data signal of dst_stride
//        bit 31~0 - dst_stride[31:0] (Read/Write)
// 0x54 : reserved
// 0x58 : Data signal of frame_cookie
//        bit 31~0 - frame_cookie[31:0] (Read/Write)
// 0x5c : reserved
// 0x60 : Data signal of metadata_cookie
//        bit 31~0 - metadata_cookie[31:0] (Read/Write)
// 0x64 : reserved
// 0x68 : Data signal of control
//        bit 31~0 - control[31:0] (Read/Write)
// 0x6c : reserved
// 0x70 : Data signal of order
//        bit 31~0 - order[31:0] (Read/Write)
// 0x74 : reserved
// 0x78 : Data signal of ink_delta
//        bit 31~0 - ink_delta[31:0] (Read/Write)
// 0x7c : reserved
// 0x80 : Data signal of erase_delta
//        bit 31~0 - erase_delta[31:0] (Read/Write)
// 0x84 : reserved
// 0x88 : Data signal of color_margin
//        bit 31~0 - color_margin[31:0] (Read/Write)
// 0x8c : reserved
// (SC = Self Clear, COR = Clear on Read, TOW = Toggle on Write, COH = Clear on Handshake)

#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_AP_CTRL              0x00
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_GIE                  0x04
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_IER                  0x08
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_ISR                  0x0c
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_AP_RETURN            0x10
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_AP_RETURN            32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_SRC_DATA             0x18
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_SRC_DATA             32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_CANVAS_IN_DATA       0x20
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_CANVAS_IN_DATA       32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_CANVAS_OUT_DATA      0x28
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_CANVAS_OUT_DATA      32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_METADATA_DATA        0x30
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_METADATA_DATA        32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_DST_DATA             0x38
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_DST_DATA             32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_WIDTH_DATA           0x40
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_WIDTH_DATA           32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_HEIGHT_DATA          0x48
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_HEIGHT_DATA          32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_DST_STRIDE_DATA      0x50
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_DST_STRIDE_DATA      32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_FRAME_COOKIE_DATA    0x58
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_FRAME_COOKIE_DATA    32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_METADATA_COOKIE_DATA 0x60
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_METADATA_COOKIE_DATA 32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_CONTROL_DATA         0x68
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_CONTROL_DATA         32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_ORDER_DATA           0x70
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_ORDER_DATA           32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_INK_DELTA_DATA       0x78
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_INK_DELTA_DATA       32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_ERASE_DELTA_DATA     0x80
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_ERASE_DELTA_DATA     32
#define XBOARD_SCENE_QUANTIZE_CONTROL_ADDR_COLOR_MARGIN_DATA    0x88
#define XBOARD_SCENE_QUANTIZE_CONTROL_BITS_COLOR_MARGIN_DATA    32

