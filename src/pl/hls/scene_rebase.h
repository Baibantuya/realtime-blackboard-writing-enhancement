#ifndef WB_SCENE_REBASE_H
#define WB_SCENE_REBASE_H
#include <stdint.h>
// v15 initialize register: bit0 explicit initialization, bit1 auto enabled,
// bit2 source-frame geometry/photometry eligible; bits15:8 confirmation frames,
// bits31:16 cooldown frames. Zero fields select 8 / 64 processed frames.
// Enabled callers MUST allocate block_count + 4 words of block_state.
static const uint32_t WB_SCENE_MAGIC=0x57424331u;
static bool wb_scene_step(uint32_t* meta,uint32_t control,unsigned reasons){
#pragma HLS INLINE
    unsigned need=(control>>8)&255; if(!need)need=8;
    unsigned delay=control>>16; if(!delay)delay=64;
    unsigned streak=meta[1]&255,armed=(meta[1]>>8)&1,cool=meta[1]>>16;
    if(cool)--cool;
    // Only actual spatial obstruction evidence arms a new clear episode.
    // Motion, missing geometry or exposure changes alone never arm it.
    if(reasons&((1u<<1)|(1u<<3)))armed=1;
    if(reasons||cool||!armed)streak=0;
    else if(streak<need)++streak;
    bool rebase=armed&&!reasons&&!cool&&streak>=need;
    if(rebase){++meta[2];armed=0;streak=0;cool=delay;}
    meta[1]=streak|(armed<<8)|(cool<<16);
    meta[3]=reasons|(rebase?0x100u:0);
    return rebase;
}
#endif
