#include "board_scene_quantize.h"
#include "rgb565.h"
#include <algorithm>
#include <cstdio>
#include <vector>

int main() {
    // Bounded RTL regression of changed pigment rules plus existing AXI,
    // erase, HOLD and cookie behavior. Full 1920-width is validated on board.
    const unsigned w=160,h=33,stride=384;
    const uint16_t board=wb_pack565(32u|(64u<<8)|(40u<<16));
    const uint16_t white=wb_pack565(176u|(180u<<8)|(184u<<16));
    // HLS wrapc serializes the declared m_axi depth, even for a short frame.
    // Back every pointer with its full interface depth to avoid host overreads.
    std::vector<uint32_t> source(1036800,uint32_t(board)|(uint32_t(board)<<16));
    std::vector<uint32_t> a(259200,0x77777777u),b(a),meta(8160);
    std::vector<uint32_t> output(1658880,0xcdcdcdcdu);
    for(unsigned y=16;y<18;++y) for(unsigned x=8;x<40;x+=2)
        source[(y*w+x)/2]=uint32_t(white)|(uint32_t(white)<<16);
    const uint16_t red=wb_pack565(208u|(64u<<8)|(64u<<16));
    const uint16_t blue=wb_pack565(64u|(80u<<8)|(208u<<16));
    // A two-pixel red island must not recolor a continuous white stroke.
    source[(16*w+20)/2]=uint32_t(red)|(uint32_t(red)<<16);
    for(unsigned y=24;y<26;++y) for(unsigned x=8;x<40;x+=2)
        source[(y*w+x)/2]=uint32_t(red)|(uint32_t(red)<<16);
    source[(24*w+20)/2]=uint32_t(blue)|(uint32_t(blue)<<16);
    source[(25*w+20)/2]=uint32_t(blue)|(uint32_t(blue)<<16);
    // Actual bright white over colored ink must stay white.
    source[(24*w+32)/2]=uint32_t(white)|(uint32_t(red)<<16);
    std::fill(meta.begin(),meta.end(),uint32_t(board)|WB_SCENE_SURFACE_VALID|WB_SCENE_VISIBLE|WB_SCENE_INITIALIZE);
    unsigned status=board_scene_quantize(source.data(),a.data(),b.data(),meta.data(),output.data(),
                                        w,h,stride,1,1,0,0,26,16,16);
    int errors=status!=0;
    for(unsigned y=16;y<18;++y) for(unsigned x=8;x<40;++x)
        errors+=((b[(y*w+x)/8]>>(4*(x&7)))&7)!=1;
    for(unsigned y=24;y<26;++y) for(unsigned x=8;x<40;++x)
        errors+=((b[(y*w+x)/8]>>(4*(x&7)))&7)!=((y==24&&x==32)?1:2);
    a.swap(b);
    std::fill(source.begin(),source.end(),uint32_t(board)|(uint32_t(board)<<16));
    std::fill(meta.begin(),meta.end(),uint32_t(board)|WB_SCENE_SURFACE_VALID|WB_SCENE_VISIBLE);
    for(unsigned frame=2;frame<=3;++frame) {
        errors+=board_scene_quantize(source.data(),a.data(),b.data(),meta.data(),output.data(),
                                     w,h,stride,frame,frame,0,0,26,16,16)!=0;
        a.swap(b);
    }
    for(unsigned y=0;y<h;++y) {
        for(unsigned x=0;x<w;++x) errors+=((a[(y*w+x)/8]>>(4*(x&7)))&7)!=0;
        for(unsigned x=w/2;x<stride/4;++x) errors+=output[y*(stride/4)+x]!=0xcdcdcdcdu;
    }
    errors+=board_scene_quantize(source.data(),a.data(),b.data(),meta.data(),output.data(),
                                 w,h,stride,4,4,WB_SCENE_HOLD,0,26,16,16)!=0;
    a.swap(b);
    std::fill(b.begin(),b.end(),0xababababu);
    errors+=board_scene_quantize(source.data(),a.data(),b.data(),meta.data(),output.data(),
                                 w,h,stride,5,6,0,0,26,16,16)!=2;
    for(unsigned i=0;i<b.size();++i) errors+=b[i]!=0xababababu;
    // R6: all seven pigments and pending-neutral/chromatic conflicts must
    // survive the resource repair in actual RTL, not only native fixtures.
    const uint16_t palette[8]={board,white,wb_pack565(176u|(40u<<8)|(32u<<16)),
        wb_pack565(32u|(56u<<8)|(160u<<16)),wb_pack565(32u|(176u<<8)|(40u<<16)),
        wb_pack565(224u|(128u<<8)|(48u<<16)),wb_pack565(224u|(224u<<8)|(48u<<16)),
        wb_pack565(232u|(56u<<8)|(152u<<16))};
    std::fill(source.begin(),source.end(),uint32_t(board)|(uint32_t(board)<<16));
    for(unsigned c=1;c<=7;++c) for(unsigned y=5;y<28;++y) for(unsigned x=c*20-8;x<c*20-5;++x) {
        unsigned index=(y*w+x)/2,shift=(x&1)*16;
        source[index]=(source[index]&~(0xffffu<<shift))|(uint32_t(palette[c])<<shift);
    }
    std::fill(a.begin(),a.end(),0);
    std::fill(meta.begin(),meta.end(),uint32_t(board)|WB_SCENE_SURFACE_VALID|WB_SCENE_VISIBLE);
    for(unsigned frame=7;frame<=10;++frame) {
        if(frame==9) for(unsigned c=2;c<=7;++c) {
            unsigned x=c*20-7,index=(16*w+x)/8,shift=4*(x&7);
            a[index]=(a[index]&~(15u<<shift))|(9u<<shift); // pending neutral
        }
        errors+=board_scene_quantize(source.data(),a.data(),b.data(),meta.data(),output.data(),
                                     w,h,stride,frame,frame,0,0,26,16,24)!=0;
        for(unsigned c=1;c<=7;++c) {
            unsigned x=c*20-7,cell=(b[(16*w+x)/8]>>(4*(x&7)))&15;
            unsigned expected=c|((frame==7 || (frame==9 && c>=2))?8u:0u);
            if(cell!=expected) {++errors;std::printf("R6 palette/vote frame=%u color=%u got=%u want=%u\n",frame,c,cell,expected);}
        }
        a.swap(b);
    }
    std::printf("scene native/HLS-compatible testbench errors=%d\n",errors);
    return errors?1:0;
}
