#pragma once
#include <stdint.h>

// Logical ABI; actual AXI-Lite offsets require a fresh HLS export/HWH.
enum { WB_SCENE_ABI = 0x57425321u, WB_SCENE_VISIBLE = 1u << 16,
       WB_SCENE_INITIALIZE = 1u << 17, WB_SCENE_SURFACE_VALID = 1u << 18,
       WB_SCENE_OCCLUDED = 1u << 19, WB_SCENE_REVEAL_OBSERVATION = 1u << 20, WB_SCENE_HOLD = 1u,
       WB_SCENE_UNKNOWN = 0u };
// Eight four-bit cells per word: bits[2:0] palette, bit[3] color vote pending.
// 0=board/unknown, 1=neutral chalk (black output), 2=red, 3=blue,
// 4=green, 5=orange, 6=yellow, 7=pink. A pending bit confirms a new color
// on the next visible frame while retaining the existing erase/reveal state.
extern "C" uint32_t wb_scene_abi();
extern "C" uint32_t board_scene_quantize(
    const uint32_t* src, const uint32_t* canvas_in, uint32_t* canvas_out,
    const uint32_t* metadata, uint32_t* dst,
    unsigned width, unsigned height, unsigned dst_stride,
    unsigned frame_cookie, unsigned metadata_cookie, unsigned control,
    unsigned order, unsigned ink_delta, unsigned erase_delta, unsigned color_margin);
