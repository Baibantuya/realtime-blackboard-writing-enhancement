#pragma once
#include <cstdint>
constexpr int WB_MAX_WIDTH=1920,WB_MAX_HEIGHT=1080;
constexpr int WB_MAX_BLOCKS=8160;
// Auto scene reset (initialize bit1): reserve four words after active blocks.
constexpr int WB_SCENE_META_WORDS=4;
constexpr int WB_FRAME_WORDS=1555200,WB_QUIET_WORDS=518400;
extern "C" uint32_t whiteboard_restore(
    const uint32_t* input,uint32_t* output,uint32_t* background,uint32_t* previous,
    uint32_t* pixel_quiet,uint32_t* block_state,const uint8_t* roi,
    int width,int height,uint32_t initialize,uint32_t bgr,
    uint32_t delta,uint32_t quiet_delta,uint32_t dense,uint32_t weak_threshold,
    uint32_t hold,uint32_t stable,uint32_t quiet_max,uint32_t chalk_min,uint32_t chalk_spread,
    uint32_t fine_min,uint32_t fine_spread,uint32_t red_bias);
