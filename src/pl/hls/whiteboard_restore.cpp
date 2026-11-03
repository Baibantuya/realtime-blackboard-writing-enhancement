#include "whiteboard_restore.h"
#include "rgb565.h"
#include "resource_math_inferred.h"
#include "local_sum_tree.h"
#include "scene_rebase.h"
#include "whiteboard_stream.h"

extern "C" uint8_t guarded_state(const uint8_t*,const uint8_t*,const uint8_t*,const uint8_t*,
    const uint8_t*,const uint8_t*,const uint16_t*,const uint8_t*,const uint8_t*,
    uint16_t*,uint8_t*,uint8_t*,uint8_t*,uint8_t*,int,int,uint16_t,uint8_t,uint8_t,uint8_t,uint8_t);

static int channel(uint32_t p,int c){return (wb_expand565(uint16_t(p))>>(8*c))&255;}
static int distance(uint32_t a,uint32_t b){
#pragma HLS INLINE
    int maximum=0;
    for(int c=0;c<3;++c){
#pragma HLS UNROLL
        int d=channel(a,c)-channel(b,c);if(d<0)d=-d;if(d>maximum)maximum=d;
    }
    return maximum;
}
static bool chalk(uint32_t p,int floor,int spread){
#pragma HLS INLINE
    int lo=channel(p,0),hi=lo;
    for(int c=1;c<3;++c){
#pragma HLS UNROLL
        int v=channel(p,c);if(v<lo)lo=v;if(v>hi)hi=v;
    }
    return lo>=floor&&hi-lo<=spread;
}
static bool fine_color(uint32_t p,bool bgr,int floor,int spread,int bias){
#pragma HLS INLINE
    int r=channel(p,bgr?2:0),b=channel(p,bgr?0:2),g=channel(p,1);
    return chalk(p,floor,spread)&&r<=b+bias&&r<=g+bias;
}
static uint32_t unpack(uint32_t a,uint32_t b,uint32_t c,int k){
#pragma HLS INLINE
    return ((k<2?a:b)>>((k&1)*16))&65535;
}
static void pack4(const uint32_t p[4],uint32_t &a,uint32_t &b,uint32_t &c){
#pragma HLS INLINE
    a=(p[0]&65535)|(p[1]<<16);b=(p[2]&65535)|(p[3]<<16);c=0;
}

static void neutral_pixels(const uint32_t* input,wb::stream<bool>& values,wb::stream<uint16_t>& pixels,wb::stream<uint16_t>& local_pixels,int width,int height,
                           bool bgr,int floor,int spread,int bias){
#pragma HLS INLINE off
    const int groups=width*height/4;
    for(int i=0;i<groups;++i){
#pragma HLS LOOP_TRIPCOUNT min=4 max=518400
        uint32_t a=input[2*i],b=input[2*i+1],c=0;
        for(int k=0;k<4;++k){
#pragma HLS PIPELINE II=1
            uint32_t p=unpack(a,b,c,k);
            pixels.write(p);local_pixels.write(p);values.write(fine_color(p,bgr,floor,spread,bias));
        }
    }
}

// Thin local positive contrast is independent of absolute brightness and ink
// hue. Wide illumination/shirt interiors do not become writing evidence.
static void local_ink(wb::stream<uint16_t>& input,wb::stream<bool>& output,int width,int height){
#pragma HLS INLINE off
    uint8_t lines[6][WB_MAX_WIDTH],win[7][7];
#pragma HLS ARRAY_PARTITION variable=lines complete dim=1
#pragma HLS BIND_STORAGE variable=lines type=ram_s2p impl=uram
#pragma HLS ARRAY_PARTITION variable=win complete dim=0
    for(int x=0;x<width;x++){
#pragma HLS PIPELINE II=1
        for(int row=0;row<6;row++){
#pragma HLS UNROLL
            lines[row][x]=0;
        }
    }
    for(int y=0;y<height+3;y++)for(int x=0;x<width+3;x++){
#pragma HLS PIPELINE II=1
        uint32_t p=(x<width&&y<height)?input.read():0;
        uint8_t lum=wb_luma(channel(p,0),channel(p,1),channel(p,2));
        uint16_t column[7];
#pragma HLS ARRAY_PARTITION variable=column complete
        for(int row=0;row<6;row++){
#pragma HLS UNROLL
            column[row]=x<width?lines[row][x]:0;
            if(x<width)lines[row][x]=(row==5)?lum:lines[row+1][x];
        }
        column[6]=lum;
        for(int row=0;row<7;row++){
#pragma HLS UNROLL
            for(int col=0;col<6;col++){
#pragma HLS UNROLL
                win[row][col]=x?win[row][col+1]:0;
            }
            win[row][6]=column[row];
        }
        const unsigned sum=wb_local_sum(win);
        if(y>=3&&x>=3)output.write(int(win[3][3])*49-int(sum)>=6*49);
    }
}

// Rectangular erosion/dilation with OpenCV's neutral constant borders:
// outside=true for erosion and outside=false for dilation. One bit per pixel.
template<int R,bool ERODE> static void box_filter(wb::stream<bool>& input,wb::stream<bool>& output,
                                                 int width,int height){
#pragma HLS INLINE off
    constexpr int K=2*R+1,PAD=WB_MAX_WIDTH+2*R;
    bool lines[2*R][PAD],window[K][K];
#pragma HLS ARRAY_PARTITION variable=lines complete dim=1
#pragma HLS BIND_STORAGE variable=lines type=ram_s2p impl=uram
#pragma HLS ARRAY_PARTITION variable=window complete dim=0
    for(int i=0;i<2*R;++i)for(int x=0;x<width+2*R;++x){
#pragma HLS PIPELINE II=1
        lines[i][x]=ERODE;
    }
    for(int i=0;i<K;++i)for(int j=0;j<K;++j)window[i][j]=ERODE;
    for(int y=0;y<height+2*R;++y){
#pragma HLS LOOP_TRIPCOUNT min=3 max=1086
        for(int x=0;x<width+2*R;++x){
#pragma HLS LOOP_TRIPCOUNT min=18 max=1926
#pragma HLS PIPELINE II=1
#pragma HLS DEPENDENCE variable=lines inter false
            bool p=ERODE;
            if(y>=R&&y<height+R&&x>=R&&x<width+R)p=input.read();
            bool column[K];
#pragma HLS ARRAY_PARTITION variable=column complete
            for(int i=0;i<2*R;++i){
#pragma HLS UNROLL
                column[i]=lines[i][x];
                lines[i][x]=(i==2*R-1)?p:lines[i+1][x];
            }
            column[K-1]=p;
            for(int i=0;i<K;++i){
#pragma HLS UNROLL
                for(int j=0;j<K-1;++j){
#pragma HLS UNROLL
                    window[i][j]=window[i][j+1];
                }
                window[i][K-1]=column[i];
            }
            bool result=ERODE;
            for(int i=0;i<K;++i){
#pragma HLS UNROLL
                for(int j=0;j<K;++j){
#pragma HLS UNROLL
                    if(ERODE)result&=window[i][j];else result|=window[i][j];
                }
            }
            if(y>=2*R&&x>=2*R)output.write(result);
        }
    }
}

static void compose(wb::stream<uint16_t>& pixels,uint32_t* output,uint32_t* background,uint32_t* previous,
                    uint32_t* pixel_quiet,wb::stream<bool>& broad,wb::stream<bool>& thin,const uint8_t* region,
                    const uint8_t* mask,const uint8_t* writes,int width,int height,
                    bool bgr,int stable,int quiet_delta,int floor,int spread,int bias,bool freeze){
#pragma HLS INLINE off
    const int groups_per_row=width/4,words_per_row=width/2,gw=width/16;
    uint32_t prev_buf[WB_MAX_WIDTH/2],bg_buf[WB_MAX_WIDTH/2],quiet_buf[WB_MAX_WIDTH/4];
    uint32_t out_buf[WB_MAX_WIDTH/2],new_bg_buf[WB_MAX_WIDTH/2],new_prev_buf[WB_MAX_WIDTH/2],new_quiet_buf[WB_MAX_WIDTH/4];
#pragma HLS BIND_STORAGE variable=prev_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=bg_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=quiet_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=out_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=new_bg_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=new_prev_buf type=ram_t2p impl=uram
#pragma HLS BIND_STORAGE variable=new_quiet_buf type=ram_t2p impl=uram

    for(int y=0;y<height;++y){
#pragma HLS LOOP_TRIPCOUNT min=1 max=1080
        const int row_word=y*words_per_row,row_group=y*groups_per_row,block_row=(y/16)*gw;

        for(int w=0;w<words_per_row;++w){
#pragma HLS LOOP_TRIPCOUNT min=8 max=960
#pragma HLS PIPELINE II=1
            prev_buf[w]=previous[row_word+w];
        }
        for(int w=0;w<words_per_row;++w){
#pragma HLS LOOP_TRIPCOUNT min=8 max=960
#pragma HLS PIPELINE II=1
            bg_buf[w]=background[row_word+w];
        }
        for(int g=0;g<groups_per_row;++g){
#pragma HLS LOOP_TRIPCOUNT min=4 max=480
#pragma HLS PIPELINE II=1
            quiet_buf[g]=pixel_quiet[row_group+g];
        }

        for(int x=0;x<groups_per_row;++x){
#pragma HLS LOOP_TRIPCOUNT min=4 max=480
            const int word=2*x,block=block_row+x/4;
            uint32_t pa=prev_buf[word],pb=prev_buf[word+1],pc=0;
            uint32_t ba=bg_buf[word],bb=bg_buf[word+1],bc=0;
            uint32_t counters=quiet_buf[x],next_counters=0;
            uint32_t displayed[4],committed[4],current[4];
#pragma HLS ARRAY_PARTITION variable=current complete
#pragma HLS ARRAY_PARTITION variable=displayed complete
#pragma HLS ARRAY_PARTITION variable=committed complete
            for(int k=0;k<4;++k){
#pragma HLS PIPELINE II=1
                uint32_t c=pixels.read(),p=unpack(pa,pb,pc,k),b=unpack(ba,bb,bc,k);current[k]=c;
                int q=0;if(distance(c,p)<quiet_delta){q=((counters>>(8*k))&255)+1;if(q>stable)q=stable;}
                next_counters|=uint32_t(q)<<(8*k);
                bool is_broad=broad.read();
                bool ink=thin.read()&&!is_broad&&region[block]&&writes[block];
                displayed[k]=(mask[block]&&!ink)?b:c;
                bool trusted=writes[block]&&!mask[block]&&!freeze&&!is_broad&&q>=stable&&distance(c,b)<=quiet_delta/2;
                committed[k]=(trusted||(ink&&q>=stable&&!freeze))?c:b;
            }
            uint32_t oa,ob,oc,na,nb,nc;pack4(displayed,oa,ob,oc);pack4(committed,na,nb,nc);
            out_buf[word]=oa;out_buf[word+1]=ob;
            new_bg_buf[word]=na;new_bg_buf[word+1]=nb;
            uint32_t ca,cb,cc;pack4(current,ca,cb,cc);
            new_prev_buf[word]=ca;new_prev_buf[word+1]=cb;
            new_quiet_buf[x]=next_counters;
        }

        for(int w=0;w<words_per_row;++w){
#pragma HLS LOOP_TRIPCOUNT min=8 max=960
#pragma HLS PIPELINE II=1
            output[row_word+w]=out_buf[w];
        }
        for(int w=0;w<words_per_row;++w){
#pragma HLS LOOP_TRIPCOUNT min=8 max=960
#pragma HLS PIPELINE II=1
            background[row_word+w]=new_bg_buf[w];
        }
        for(int w=0;w<words_per_row;++w){
#pragma HLS LOOP_TRIPCOUNT min=8 max=960
#pragma HLS PIPELINE II=1
            previous[row_word+w]=new_prev_buf[w];
        }
        for(int g=0;g<groups_per_row;++g){
#pragma HLS LOOP_TRIPCOUNT min=4 max=480
#pragma HLS PIPELINE II=1
            pixel_quiet[row_group+g]=new_quiet_buf[g];
        }
    }
}

static void render_frame(const uint32_t* input,uint32_t* output,uint32_t* background,uint32_t* previous,
                         uint32_t* pixel_quiet,const uint8_t* region,const uint8_t* mask,const uint8_t* writes,
                         int width,int height,bool bgr,int stable,int quiet_delta,int floor,int spread,int bias,bool freeze){
#pragma HLS INLINE off
#pragma HLS DATAFLOW
    wb::stream<bool> neutral,eroded,opened,broad;
    wb::stream<uint16_t> pixels,local_pixels;
    wb::stream<bool> thin;
// Seven rows of morphology lookahead at maximum width plus FIFO/padding slack.
#pragma HLS STREAM variable=pixels depth=16384
#pragma HLS BIND_STORAGE variable=pixels type=fifo impl=uram
#pragma HLS STREAM variable=local_pixels depth=128
#pragma HLS BIND_STORAGE variable=local_pixels type=fifo impl=lutram
#pragma HLS STREAM variable=thin depth=16384
#pragma HLS BIND_STORAGE variable=thin type=fifo impl=uram
#pragma HLS STREAM variable=neutral depth=128
#pragma HLS BIND_STORAGE variable=neutral type=fifo impl=lutram
#pragma HLS STREAM variable=eroded depth=128
#pragma HLS BIND_STORAGE variable=eroded type=fifo impl=lutram
#pragma HLS STREAM variable=opened depth=128
#pragma HLS BIND_STORAGE variable=opened type=fifo impl=lutram
#pragma HLS STREAM variable=broad depth=128
#pragma HLS BIND_STORAGE variable=broad type=fifo impl=lutram
    neutral_pixels(input,neutral,pixels,local_pixels,width,height,bgr,floor,spread,bias);
    local_ink(local_pixels,thin,width,height);
    box_filter<3,true>(neutral,eroded,width,height);
    box_filter<3,false>(eroded,opened,width,height);
    box_filter<1,false>(opened,broad,width,height);
    compose(pixels,output,background,previous,pixel_quiet,broad,thin,region,mask,writes,
            width,height,bgr,stable,quiet_delta,floor,spread,bias,freeze);
}

static void initialize_frame(const uint32_t* input,uint32_t* output,uint32_t* background,
                             uint32_t* previous,uint32_t* pixel_quiet,uint32_t* block_state,
                             int width,int height,int count,unsigned stable){
#pragma HLS INLINE off
        const int words=width*height/2,groups=width*height/4;
        for(int i=0;i<words;++i){
#pragma HLS LOOP_TRIPCOUNT min=12 max=1555200
#pragma HLS PIPELINE II=1
            uint32_t p=input[i];output[i]=p;background[i]=p;previous[i]=p;
        }
        for(int i=0;i<groups;++i){
#pragma HLS LOOP_TRIPCOUNT min=4 max=518400
#pragma HLS PIPELINE II=1
            pixel_quiet[i]=stable*0x01010101u;
        }
        for(int i=0;i<count;++i){
#pragma HLS LOOP_TRIPCOUNT min=1 max=8160
#pragma HLS PIPELINE II=1
            block_state[i]=stable<<16;
        }
}

extern "C" uint32_t whiteboard_restore(const uint32_t* input,uint32_t* output,uint32_t* background,uint32_t* previous,
    uint32_t* pixel_quiet,uint32_t* block_state,const uint8_t* roi,
    int width,int height,uint32_t initialize,uint32_t bgr,uint32_t delta,uint32_t quiet_delta,
    uint32_t dense,uint32_t weak_threshold,uint32_t hold,uint32_t stable,uint32_t quiet_max,
    uint32_t chalk_min,uint32_t chalk_spread,uint32_t fine_min,uint32_t fine_spread,uint32_t red_bias){
#pragma HLS INTERFACE m_axi port=input offset=slave bundle=frame_in depth=1036800 max_read_burst_length=64
#pragma HLS INTERFACE m_axi port=output offset=slave bundle=frame_out depth=1036800 max_write_burst_length=64
#pragma HLS INTERFACE m_axi port=background offset=slave bundle=history depth=1036800 max_read_burst_length=64 max_write_burst_length=64
#pragma HLS INTERFACE m_axi port=previous offset=slave bundle=previous_frame depth=1036800 max_read_burst_length=64 max_write_burst_length=64
#pragma HLS INTERFACE m_axi port=pixel_quiet offset=slave bundle=pixel_state depth=518400 max_read_burst_length=64 max_write_burst_length=64
#pragma HLS INTERFACE m_axi port=block_state offset=slave bundle=block_memory depth=8164
#pragma HLS INTERFACE m_axi port=roi offset=slave bundle=block_memory depth=8160
#pragma HLS INTERFACE s_axilite port=input bundle=control
#pragma HLS INTERFACE s_axilite port=output bundle=control
#pragma HLS INTERFACE s_axilite port=background bundle=control
#pragma HLS INTERFACE s_axilite port=previous bundle=control
#pragma HLS INTERFACE s_axilite port=pixel_quiet bundle=control
#pragma HLS INTERFACE s_axilite port=block_state bundle=control
#pragma HLS INTERFACE s_axilite port=roi bundle=control
#pragma HLS INTERFACE s_axilite port=width bundle=control
#pragma HLS INTERFACE s_axilite port=height bundle=control
#pragma HLS INTERFACE s_axilite port=initialize bundle=control
#pragma HLS INTERFACE s_axilite port=bgr bundle=control
#pragma HLS INTERFACE s_axilite port=delta bundle=control
#pragma HLS INTERFACE s_axilite port=quiet_delta bundle=control
#pragma HLS INTERFACE s_axilite port=dense bundle=control
#pragma HLS INTERFACE s_axilite port=weak_threshold bundle=control
#pragma HLS INTERFACE s_axilite port=hold bundle=control
#pragma HLS INTERFACE s_axilite port=stable bundle=control
#pragma HLS INTERFACE s_axilite port=quiet_max bundle=control
#pragma HLS INTERFACE s_axilite port=chalk_min bundle=control
#pragma HLS INTERFACE s_axilite port=chalk_spread bundle=control
#pragma HLS INTERFACE s_axilite port=fine_min bundle=control
#pragma HLS INTERFACE s_axilite port=fine_spread bundle=control
#pragma HLS INTERFACE s_axilite port=red_bias bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    if(width<16||width>1920||width%16||height<1||height>1080||(initialize&0xf8u)||(!(initialize&2u)&&initialize>1)||bgr>1||
       !delta||delta>255||!quiet_delta||quiet_delta>255||!dense||dense>16||!weak_threshold||weak_threshold>dense||
       !hold||hold>65535||!stable||stable>15||quiet_max>16||chalk_min>255||chalk_spread>255||
       fine_min>255||fine_spread>255||red_bias>255)return 1;
    const bool explicit_init=(initialize&1u)!=0,auto_clear=(initialize&2u)!=0;
    int gw=width/16,gh=(height+15)/16,count=gw*gh;
    uint32_t* scene_meta=block_state+count;
    if(auto_clear&&!explicit_init&&scene_meta[0]!=WB_SCENE_MAGIC)return 4;
    uint8_t occupied[WB_MAX_BLOCKS],motion[WB_MAX_BLOCKS],quiet[WB_MAX_BLOCKS],changed[WB_MAX_BLOCKS];
    uint8_t n[WB_MAX_BLOCKS],region[WB_MAX_BLOCKS],old_q[WB_MAX_BLOCKS],old_occupied[WB_MAX_BLOCKS];
    uint8_t q[WB_MAX_BLOCKS],seed[WB_MAX_BLOCKS],mask[WB_MAX_BLOCKS],writes[WB_MAX_BLOCKS];
    uint16_t old_ttl[WB_MAX_BLOCKS],ttl[WB_MAX_BLOCKS];
#pragma HLS BIND_STORAGE variable=occupied type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=motion type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=quiet type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=changed type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=n type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=region type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=old_q type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=old_occupied type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=q type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=seed type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=mask type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=writes type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=old_ttl type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=ttl type=ram_t2p impl=bram
    bool invalid=false;
    for(int i=0;i<count;++i){
#pragma HLS LOOP_TRIPCOUNT min=1 max=8160
#pragma HLS PIPELINE II=1
        int rows=height-16*(i/gw);if(rows>16)rows=16;n[i]=((rows+3)/4)*4;
        uint32_t old=explicit_init?0:block_state[i];
        old_ttl[i]=old&65535;old_q[i]=(old>>16)&255;old_occupied[i]=old>>24;
        region[i]=roi[i];invalid|=region[i]>1||old_occupied[i]>n[i];
    }
    if(invalid)return 2;
    if(explicit_init){
        initialize_frame(input,output,background,previous,pixel_quiet,block_state,width,height,count,stable);
        if(auto_clear){scene_meta[0]=WB_SCENE_MAGIC;scene_meta[1]=0;scene_meta[2]=0;scene_meta[3]=0;}
        return 0;
    }
    int dense_count=0,roi_count=0;
    bool scene_occupied=false,scene_unstable=false,scene_bulk_white=false,scene_old_guard=false;
    for(int by=0;by<gh;++by){
#pragma HLS LOOP_TRIPCOUNT min=1 max=68
        for(int bx=0;bx<gw;++bx){
#pragma HLS LOOP_TRIPCOUNT min=1 max=120
            int i=by*gw+bx;uint8_t o=0,mo=0,qu=0,ch=0,white_changed=0;
            for(int s=0;s<16;++s){
#pragma HLS PIPELINE II=1
                if(s<n[i]){
                    int y=16*by+4*(s/4),x=16*bx+4*(s%4);
                    int off=(y*width+x)/2;
                    uint32_t c=input[off]&65535,p=previous[off]&65535,b=background[off]&65535;
                    int db=distance(c,b),df=distance(c,p);bool cc=chalk(c,chalk_min,chalk_spread);
                    o+=db>=int(delta)&&!cc&&!chalk(b,chalk_min,chalk_spread);
                    mo+=df>=int(delta)&&!cc&&!chalk(p,chalk_min,chalk_spread);
                    qu+=df>=int(quiet_delta);ch+=db>=int(delta);
                    white_changed+=(db>=int(delta)&&cc);
                }
            }
            occupied[i]=o;motion[i]=mo;quiet[i]=qu;changed[i]=ch;
            if(region[i]){
                scene_occupied|=o!=0;
                scene_unstable|=qu!=0;
                scene_bulk_white|=2*white_changed>=n[i];
                scene_old_guard|=(old_q[i]>>4)>=8;
            }
            roi_count+=region[i]!=0;dense_count+=region[i]&&16*o>=int(dense)*n[i];
        }
    }
    if(auto_clear){
        unsigned reasons=((initialize&4u)?0u:1u)|(scene_occupied?2u:0u)|
                         (scene_unstable?4u:0u)|(scene_bulk_white?8u:0u)|
                         (scene_old_guard?16u:0u)|(roi_count?0u:32u);
        if(wb_scene_step(scene_meta,initialize,reasons)){
            initialize_frame(input,output,background,previous,pixel_quiet,block_state,width,height,count,stable);
            return 0;
        }
    }
    uint8_t status=guarded_state(occupied,motion,quiet,changed,n,region,old_ttl,old_q,old_occupied,
                               ttl,q,seed,mask,writes,gw,gh,hold,dense,weak_threshold,stable,quiet_max);
    if(status)return 3;
    for(int i=0;i<count;++i){
#pragma HLS LOOP_TRIPCOUNT min=1 max=8160
#pragma HLS PIPELINE II=1
        block_state[i]=uint32_t(ttl[i])|(uint32_t(q[i])<<16)|(uint32_t(occupied[i])<<24);
    }
    bool freeze=roi_count>0&&4*dense_count>=3*roi_count;
    render_frame(input,output,background,previous,pixel_quiet,region,mask,writes,width,height,bgr,
                 stable,quiet_delta,fine_min,fine_spread,red_bias,freeze);
    return 0;
}
