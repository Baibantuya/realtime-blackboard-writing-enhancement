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
// 0x10 : Data signal of src
//        bit 31~0 - src[31:0] (Read/Write)
// 0x14 : reserved
// 0x18 : Data signal of dst
//        bit 31~0 - dst[31:0] (Read/Write)
// 0x1c : reserved
// 0x20 : Data signal of status
//        bit 31~0 - status[31:0] (Read/Write)
// 0x24 : reserved
// 0x28 : Data signal of hint
//        bit 31~0 - hint[31:0] (Read/Write)
// 0x2c : reserved
// 0x30 : Data signal of corners
//        bit 31~0 - corners[31:0] (Read/Write)
// 0x34 : reserved
// 0x38 : Data signal of binary_enable
//        bit 31~0 - binary_enable[31:0] (Read/Write)
// 0x3c : reserved
// 0x40 : Data signal of mode
//        bit 31~0 - mode[31:0] (Read/Write)
// 0x44 : reserved
// 0x48 : Data signal of threshold
//        bit 31~0 - threshold[31:0] (Read/Write)
// 0x4c : reserved
// 0x50 : Data signal of bgr
//        bit 31~0 - bgr[31:0] (Read/Write)
// 0x54 : reserved
// 0x58 : Data signal of geometry
//        bit 31~0 - geometry[31:0] (Read/Write)
// 0x5c : reserved
// 0x60 : Data signal of diagnostics
//        bit 31~0 - diagnostics[31:0] (Read/Write)
// 0x64 : reserved
// (SC = Self Clear, COR = Clear on Read, TOW = Toggle on Write, COH = Clear on Handshake)

#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_AP_CTRL            0x00
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_GIE                0x04
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_IER                0x08
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_ISR                0x0c
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_SRC_DATA           0x10
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_SRC_DATA           32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_DST_DATA           0x18
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_DST_DATA           32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_STATUS_DATA        0x20
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_STATUS_DATA        32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_HINT_DATA          0x28
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_HINT_DATA          32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_CORNERS_DATA       0x30
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_CORNERS_DATA       32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_BINARY_ENABLE_DATA 0x38
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_BINARY_ENABLE_DATA 32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_MODE_DATA          0x40
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_MODE_DATA          32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_THRESHOLD_DATA     0x48
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_THRESHOLD_DATA     32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_BGR_DATA           0x50
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_BGR_DATA           32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_GEOMETRY_DATA      0x58
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_GEOMETRY_DATA      32
#define XBOARD_RECTIFY_RGB_CONTROL_ADDR_DIAGNOSTICS_DATA   0x60
#define XBOARD_RECTIFY_RGB_CONTROL_BITS_DIAGNOSTICS_DATA   32

