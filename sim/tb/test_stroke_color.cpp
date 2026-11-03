#include "board_scene_quantize.h"
#include "rgb565.h"
#include <cstdio>
#include <vector>

int main() {
    const unsigned w=160,h=96;
    const uint16_t board=wb_pack565(32u|(64u<<8)|(40u<<16));
    const uint16_t color[5]={board,wb_pack565(184u|(184u<<8)|(184u<<16)),
        wb_pack565(208u|(64u<<8)|(64u<<16)),
        wb_pack565(64u|(80u<<8)|(208u<<16)),wb_pack565(48u|(180u<<8)|(48u<<16))};
    int errors=0,checks=0;
    for(unsigned label=1;label<=4;++label) for(unsigned width=1;width<=5;++width) {
        std::vector<uint16_t> raw(w*h,board);
        for(unsigned y=44;y<44+width;++y) for(unsigned x=12;x<148;++x) raw[y*w+x]=color[label];
        unsigned wrong=label==2?3:2;
        raw[44*w+40]=color[wrong];
        if(width>=2) for(unsigned y=44;y<46;++y) for(unsigned x=72;x<74;++x) raw[y*w+x]=color[wrong];
        // A genuine perpendicular differently colored stroke must retain its center.
        for(unsigned y=20;y<76;++y) raw[y*w+112]=color[wrong];
        // Separate punctuation must survive; no diffusion into bare material.
        raw[20*w+24]=color[wrong];
        std::vector<uint32_t> src(w*h/2),old(w*h/8,0x77777777u),next(old),out(w*h/2),meta(w/16*((h+15)/16));
        for(unsigned i=0;i<src.size();++i)src[i]=raw[i*2]|(uint32_t(raw[i*2+1])<<16);
        for(unsigned i=0;i<meta.size();++i)meta[i]=board|WB_SCENE_VISIBLE|WB_SCENE_SURFACE_VALID|WB_SCENE_INITIALIZE;
        errors+=board_scene_quantize(src.data(),old.data(),next.data(),meta.data(),out.data(),w,h,w*2,1,1,0,0,26,16,24)!=0;
        auto at=[&](unsigned x,unsigned y){return (next[(y*w+x)/8]>>(4*(x&7)))&7;};
        auto check=[&](unsigned x,unsigned y,unsigned expected,const char* name){++checks;if(at(x,y)!=expected){++errors;std::printf("FAIL %s label=%u width=%u x=%u y=%u got=%u want=%u\n",name,label,width,x,y,at(x,y),expected);}};
        check(40,44,label,"single_color_noise");
        if(width>=2)for(unsigned y=44;y<46;++y)for(unsigned x=72;x<74;++x)check(x,y,label,"two_by_two_color_noise");
        check(112,44,wrong,"real_color_crossing");
        check(24,20,wrong,"isolated_punctuation");
        check(40,43,0,"no_ink_expansion");
        check(40,44+width,0,"no_ink_expansion");
    }
    std::printf("STROKE_COLOR checks=%d errors=%d\n",checks,errors);
    return errors?1:0;
}
