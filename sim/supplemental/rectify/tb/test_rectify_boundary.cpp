#include <stdint.h>
#include "rgb565.h"
#include <stdio.h>
#include <vector>
#include <math.h>
#include <string.h>
extern "C" void board_rectify_rgb(const uint32_t*,uint32_t*,uint32_t*,uint32_t*,uint32_t*,uint32_t,uint32_t,uint32_t,uint32_t,const uint32_t*,uint32_t*);
static uint32_t bits(float f) { uint32_t u; memcpy(&u,&f,4); return u; }
static int one(int w,int h,int kind,bool binary,bool bgr) {
    int bytes=w*h*2,words=bytes/4;
    std::vector<uint32_t> src(1555200+16),dst(1555200+16,0xdeadbeef);
    uint8_t* s=(uint8_t*)src.data(); uint8_t* d=(uint8_t*)dst.data();
    for(int i=0;i<bytes;++i) s[i]=(uint8_t)((i*13+(i/17)*7)&255);
    uint32_t g[20]={0x57424734,1,(uint32_t)w,(uint32_t)h,0,0,(uint32_t)w,(uint32_t)h};
    float c[8]={1,0,0,0,1,0,0,0};
    if(kind==1) { c[0]=-1;c[2]=w-1;c[4]=-1;c[5]=h-1; }
    if(kind==2) { c[2]=3;c[5]=-2; }
    if(kind==3) { c[0]=0.83f;c[1]=0.03f;c[2]=2;c[3]=-0.02f;c[4]=0.87f;c[5]=1;c[6]=0.0002f;c[7]=-0.0001f; }
    if(kind==4) { g[4]=w/4;g[5]=h/4;g[6]=w/2;g[7]=h/2; }
    for(int i=0;i<8;++i)g[8+i]=bits(c[i]);
    for(int i=0;i<4;++i)g[16+i]=i+100;
    uint32_t status=99,hint=99,corner[4]={0},diagnostics[16]={0};
    board_rectify_rgb(src.data(),dst.data(),&status,&hint,corner,binary,1,128,bgr,g,diagnostics);
    if(diagnostics[0]!=0x57424436 || diagnostics[1]!=unsigned(w*h) || diagnostics[2]!=diagnostics[3]+diagnostics[4])return 2;
    if(status || hint || memcmp(corner,g+16,16))return 1;
    for(int y=0;y<h;++y)for(int x=0;x<w;++x) {
        uint8_t rgb[3]={255,255,255};int u=x-(int)g[4],v=y-(int)g[5];
        if(u>=0 && v>=0 && u<(int)g[6] && v<(int)g[7]) {
            float den=c[6]*u+c[7]*v+1;
            if(fabsf(den)>1e-5f) {
                float fx=(c[0]*u+c[1]*v+c[2])/den,fy=(c[3]*u+c[4]*v+c[5])/den;
                if(fx>=-0.5f && fx<w-0.5f && fy>=-0.5f && fy<h-0.5f) {
                    int sx=(int)(fx+0.5f),sy=(int)(fy+0.5f);
                    uint32_t value=wb_expand565(((const uint16_t*)s)[sy*w+sx]);rgb[0]=value;rgb[1]=value>>8;rgb[2]=value>>16;
                }
            }
        }
        if(binary) { int l=(bgr?29*rgb[0]+150*rgb[1]+77*rgb[2]:77*rgb[0]+150*rgb[1]+29*rgb[2])>>8;
            rgb[0]=rgb[1]=rgb[2]=l>=128?255:0; }
        if(wb_pack565(rgb[0]|(rgb[1]<<8)|(rgb[2]<<16))!=((const uint16_t*)d)[y*w+x]) { printf("mismatch %d %d kind%d\n",x,y,kind);return 2; }
    }
    for(int i=words;i<words+16;++i)if(dst[i]!=0xdeadbeef)return 3;
    // Reused capture physical address must not reuse cached pixels.
    for(int i=0;i<bytes;++i)s[i]^=255;
    g[8]=bits(1);g[9]=bits(0);g[10]=bits(0);g[11]=bits(0);g[12]=bits(1);g[13]=g[14]=g[15]=0;
    g[4]=g[5]=0;g[6]=w;g[7]=h;
    board_rectify_rgb(src.data(),dst.data(),&status,&hint,corner,0,1,128,0,g,diagnostics);
    if(memcmp(s,d,bytes))return 4;
    g[0]=0;dst[0]=0x12345678;
    board_rectify_rgb(src.data(),dst.data(),&status,&hint,corner,0,1,128,0,g,diagnostics);
    if(status!=1 || dst[0]!=0x12345678)return 5;
    return 0;
}
int main() {
    int rc=one(1920,3,0,false,false); if(rc)return rc;
    rc=one(16,1080,0,false,false); if(rc)return rc;
    rc=one(1920,3,3,true,false); if(rc)return rc;
    rc=one(16,1080,3,true,true); if(rc)return rc;
    printf("PASS 4 boundary cases 1920x3 and 16x1080, identity/projective, RGB/binary/BGR, cache refresh, atomic invalid and guards\n");
    return 0;
}
