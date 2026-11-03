/* Plain C reference/native display operations. No image enhancement here. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
void ps_copy565(uint16_t *dst,size_t dst_stride,const uint16_t *src,size_t src_stride,
                unsigned width,unsigned height){
    for(unsigned y=0;y<height;y++)memcpy((char*)dst+y*dst_stride,(const char*)src+y*src_stride,width*2);
}
void ps_blend565(uint16_t *image,size_t stride,const uint8_t *bgra,size_t ui_stride,
                 uint16_t *original,unsigned width,unsigned height){
    for(unsigned y=0;y<height;y++){
        uint16_t *row=(uint16_t*)((char*)image+y*stride);
        const uint8_t *ui=bgra+y*ui_stride;
        for(unsigned x=0;x<width;x++){
            unsigned p=row[x],a=ui[4*x+3]; original[y*width+x]=(uint16_t)p;
            if(!a)continue;
            unsigned r=((p>>11)*255+15)/31,g=(((p>>5)&63)*255+31)/63,b=((p&31)*255+15)/31;
            r=(r*(255-a)+ui[4*x+2]*a+127)/255;
            g=(g*(255-a)+ui[4*x+1]*a+127)/255;
            b=(b*(255-a)+ui[4*x]*a+127)/255;
            row[x]=(uint16_t)(((r>>3)<<11)|((g>>2)<<5)|(b>>3));
        }
    }
}
