#include <stdint.h>
#include "rgb565.h"
#include <math.h>
#ifdef WB_HLS
#include <hls_stream.h>
#else
#include <queue>
namespace hls { template<class T> class stream { std::queue<T> q;
public: void write(T v) { q.push(v); } T read() { T v=q.front(); q.pop(); return v; } }; }
#endif

static const uint32_t MAGIC=0x57424734u;
static const uint32_t INVALID=0xffffffffu;
static const int MAX_W=1920, MAX_H=1080;

static float as_float(uint32_t v) { union { uint32_t u; float f; } b; b.u=v; return b.f; }

static void coordinates(const float c[8], int width, int height,
                        int ox,int oy,int ow,int oh,hls::stream<uint32_t>& positions) {
    for(int y=0;y<height;++y) {
#pragma HLS LOOP_TRIPCOUNT min=16 max=1080
        for(int x=0;x<width;++x) {
#pragma HLS LOOP_TRIPCOUNT min=16 max=1920
#pragma HLS PIPELINE II=1
            int u=x-ox,v=y-oy; uint32_t index=INVALID;
            if(u>=0 && v>=0 && u<ow && v<oh) {
                float d=c[6]*u+c[7]*v+1.0f;
                if(d>1e-5f || d< -1e-5f) {
                    float sx=(c[0]*u+c[1]*v+c[2])/d;
                    float sy=(c[3]*u+c[4]*v+c[5])/d;
                    if(sx>=-0.5f && sx<(float)width-0.5f &&
                       sy>=-0.5f && sy<(float)height-0.5f) {
                        int ix=(int)(sx+0.5f),iy=(int)(sy+0.5f);
                        index=(uint32_t)(iy*width+ix);
                    }
                }
            }
            positions.write(index);
        }
    }
}

// Cache validity is reset every call, including when the camera reuses an address.
static uint32_t cached_word(const uint32_t* src,uint32_t word,int words,
                           uint32_t data[4][16],uint32_t tags[4],bool valid[4],uint32_t& hits,uint32_t& misses,uint32_t& loaded) {
    uint32_t line=word>>4; int slot=line&3;
    if(!valid[slot] || tags[slot]!=line) {
        misses++;
        uint32_t base=line<<4;
        // Keep the normal fill unconditional so HLS can infer a contiguous burst.
        if(base+16u<=uint32_t(words)) {
            for(int j=0;j<16;++j) {
#pragma HLS PIPELINE II=1
                data[slot][j]=src[base+j];
            }
            loaded+=16;
        } else for(int j=0;j<16;++j) {
#pragma HLS PIPELINE II=1
            data[slot][j]=(base+(uint32_t)j<(uint32_t)words)?src[base+j]:0;
            if(base+(uint32_t)j<(uint32_t)words)loaded++;
        }
        tags[slot]=line; valid[slot]=true;
    } else hits++;
    return data[slot][word&15];
}

static void fetch(const uint32_t* src,int pixels,int words,uint32_t binary_enable,
                  uint32_t mode,uint32_t threshold,uint32_t bgr,
                  hls::stream<uint32_t>& positions,hls::stream<uint32_t>& colors,uint32_t diagnostics[16]) {
    uint32_t data[4][16],tags[4]; bool valid[4]={false,false,false,false};
#pragma HLS ARRAY_PARTITION variable=data complete dim=1
#pragma HLS ARRAY_PARTITION variable=tags complete
#pragma HLS ARRAY_PARTITION variable=valid complete
    uint32_t hits=0,misses=0,loaded=0,cross=0,valid_pixels=0;
    for(int i=0;i<pixels;++i) {
#pragma HLS LOOP_TRIPCOUNT min=256 max=2073600
        uint32_t idx=positions.read(),rgb=0xffffffu;
        if(idx!=INVALID) {
            uint32_t word=idx>>1; int shift=(idx&1)*16;
            valid_pixels++;
            uint32_t lo=cached_word(src,word,words,data,tags,valid,hits,misses,loaded);
            rgb=wb_expand565(uint16_t(lo>>shift));
        }
        if(binary_enable&1) {
            uint32_t r=rgb&255,g=(rgb>>8)&255,b=(rgb>>16)&255;
            uint32_t y=(bgr&1)?(29*r+150*g+77*b)>>8:(77*r+150*g+29*b)>>8;
            bool white=(mode&1)?y>=(threshold&255):y>=(threshold&255);
            rgb=white?0xffffffu:0;
        }
        colors.write(rgb);
    }
    diagnostics[0]=0x57424436u;diagnostics[1]=pixels;diagnostics[2]=hits+misses;
    diagnostics[3]=hits;diagnostics[4]=misses;diagnostics[5]=loaded;
    diagnostics[6]=valid_pixels;diagnostics[7]=cross;diagnostics[8]=pixels-valid_pixels;
}

static void pack(int groups,hls::stream<uint32_t>& colors,hls::stream<uint32_t>& words) {
    for(int i=0;i<groups;++i) {
#pragma HLS LOOP_TRIPCOUNT min=64 max=518400
        uint32_t a=colors.read(),b=colors.read(),c=colors.read(),d=colors.read();
        words.write(uint32_t(wb_pack565(a))|(uint32_t(wb_pack565(b))<<16));
        words.write(uint32_t(wb_pack565(c))|(uint32_t(wb_pack565(d))<<16));
    }
}

static void write_frame(uint32_t* dst,int count,hls::stream<uint32_t>& words) {
    for(int i=0;i<count;++i) {
#pragma HLS LOOP_TRIPCOUNT min=192 max=1555200
#pragma HLS PIPELINE II=1
        dst[i]=words.read();
    }
}

static void render(const uint32_t* src,uint32_t* dst,const float c[8],
                   int width,int height,int ox,int oy,int ow,int oh,
                   uint32_t binary_enable,uint32_t mode,uint32_t threshold,uint32_t bgr,uint32_t diagnostics[16]) {
#pragma HLS DATAFLOW
    hls::stream<uint32_t> positions,colors,words;
#pragma HLS STREAM variable=positions depth=256
#pragma HLS STREAM variable=colors depth=64
#pragma HLS STREAM variable=words depth=128
    int pixels=width*height,count=pixels/2;
    coordinates(c,width,height,ox,oy,ow,oh,positions);
    fetch(src,pixels,count,binary_enable,mode,threshold,bgr,positions,colors,diagnostics);
    pack(pixels/4,colors,words);
    write_frame(dst,count,words);
}

extern "C" void board_rectify_rgb(const uint32_t* src,uint32_t* dst,
    uint32_t* status,uint32_t* hint,uint32_t corners[4],uint32_t binary_enable,
    uint32_t mode,uint32_t threshold,uint32_t bgr,const uint32_t geometry[20],uint32_t diagnostics[16]) {
#pragma HLS INTERFACE m_axi port=src offset=slave bundle=gmem0 depth=1036800 max_read_burst_length=16 num_read_outstanding=16
#pragma HLS INTERFACE m_axi port=dst offset=slave bundle=gmem1 depth=1036800 max_write_burst_length=64 num_write_outstanding=16
#pragma HLS INTERFACE m_axi port=status offset=slave bundle=gmem2 depth=1
#pragma HLS INTERFACE m_axi port=hint offset=slave bundle=gmem2 depth=1
#pragma HLS INTERFACE m_axi port=corners offset=slave bundle=gmem2 depth=4
#pragma HLS INTERFACE m_axi port=geometry offset=slave bundle=gmem2 depth=20
#pragma HLS INTERFACE m_axi port=diagnostics offset=slave bundle=gmem2 depth=16
#pragma HLS INTERFACE s_axilite port=src bundle=control
#pragma HLS INTERFACE s_axilite port=dst bundle=control
#pragma HLS INTERFACE s_axilite port=status bundle=control
#pragma HLS INTERFACE s_axilite port=hint bundle=control
#pragma HLS INTERFACE s_axilite port=corners bundle=control
#pragma HLS INTERFACE s_axilite port=binary_enable bundle=control
#pragma HLS INTERFACE s_axilite port=mode bundle=control
#pragma HLS INTERFACE s_axilite port=threshold bundle=control
#pragma HLS INTERFACE s_axilite port=bgr bundle=control
#pragma HLS INTERFACE s_axilite port=geometry bundle=control
#pragma HLS INTERFACE s_axilite port=diagnostics bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    uint32_t g[20];
    for(int i=0;i<20;++i) g[i]=geometry[i];
    int width=g[2],height=g[3],ox=g[4],oy=g[5],ow=g[6],oh=g[7];
    bool ok=g[0]==MAGIC && g[1]!=0 && width>=16 && width<=MAX_W && !(width&15)
        && height>=1 && height<=MAX_H && ox>=0 && oy>=0 && ow>=2 && oh>=2
        && ow<=width && oh<=height && ox<=width-ow && oy<=height-oh;
    float c[8];
#pragma HLS ARRAY_PARTITION variable=c complete
    for(int i=0;i<8;++i) { c[i]=as_float(g[8+i]); ok=ok && c[i]==c[i] && fabsf(c[i])<=1e7f; }
    *status=ok?0:1; *hint=ok?0:64;
    for(int i=0;i<4;++i) corners[i]=ok?g[16+i]:0;
    // Invalid geometry is atomic: output is left untouched, never used to seed history.
    if(ok) render(src,dst,c,width,height,ox,oy,ow,oh,binary_enable,mode,threshold,bgr,diagnostics);
}
