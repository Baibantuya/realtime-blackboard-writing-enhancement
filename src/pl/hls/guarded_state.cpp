#include <cstdint>
constexpr int DEPTH=8160;
extern "C" uint8_t guarded_state(const uint8_t* occupied,const uint8_t* motion,const uint8_t* quiet,
    const uint8_t* changed,const uint8_t* samples,const uint8_t* roi,const uint16_t* old_ttl,const uint8_t* old_q,const uint8_t* old_occupied,
    uint16_t* ttl_out,uint8_t* q_out,uint8_t* seed_out,uint8_t* m_out,uint8_t* w_out,
    int gw,int gh,uint16_t hold,uint8_t dense_threshold,uint8_t weak_threshold,uint8_t stable,uint8_t quiet_max) {
#pragma HLS INTERFACE m_axi port=occupied offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=motion offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=quiet offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=changed offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=samples offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=roi offset=slave bundle=gmem0 depth=8160
#pragma HLS INTERFACE m_axi port=old_ttl offset=slave bundle=gmem1 depth=8160
#pragma HLS INTERFACE m_axi port=old_q offset=slave bundle=gmem1 depth=8160
#pragma HLS INTERFACE m_axi port=old_occupied offset=slave bundle=gmem1 depth=8160
#pragma HLS INTERFACE m_axi port=ttl_out offset=slave bundle=gmem2 depth=8160
#pragma HLS INTERFACE m_axi port=q_out offset=slave bundle=gmem2 depth=8160
#pragma HLS INTERFACE m_axi port=seed_out offset=slave bundle=gmem3 depth=8160
#pragma HLS INTERFACE m_axi port=m_out offset=slave bundle=gmem3 depth=8160
#pragma HLS INTERFACE m_axi port=w_out offset=slave bundle=gmem3 depth=8160
#pragma HLS INTERFACE s_axilite port=gw bundle=control
#pragma HLS INTERFACE s_axilite port=gh bundle=control
#pragma HLS INTERFACE s_axilite port=hold bundle=control
#pragma HLS INTERFACE s_axilite port=dense_threshold bundle=control
#pragma HLS INTERFACE s_axilite port=weak_threshold bundle=control
#pragma HLS INTERFACE s_axilite port=stable bundle=control
#pragma HLS INTERFACE s_axilite port=quiet_max bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    if(gw<1||gw>120||gh<1||gh>68||!hold||!dense_threshold||dense_threshold>16||!weak_threshold||weak_threshold>dense_threshold||!stable||stable>15||quiet_max>16)return 1;
    uint8_t weak[DEPTH],seed[DEPTH],q[DEPTH],region[DEPTH],core[DEPTH];
    uint16_t dec[DEPTH],ttl[DEPTH];
#pragma HLS BIND_STORAGE variable=weak type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=seed type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=q type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=region type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=core type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=dec type=ram_t2p impl=bram
#pragma HLS BIND_STORAGE variable=ttl type=ram_t2p impl=bram
    bool invalid=false;const int count=gw*gh;int roi_count=0,dense_count=0;
load:
    for(int i=0;i<count;++i){
#pragma HLS LOOP_TRIPCOUNT min=1 max=8160
#pragma HLS PIPELINE II=1
        const int n=samples[i],o=occupied[i],mo=motion[i],qu=quiet[i],oo=old_occupied[i];
        invalid|=n<1||n>16||o>n||mo>n||qu>n||oo>n||changed[i]>n||o>changed[i]||roi[i]>1;
        region[i]=roi[i];weak[i]=(16*o>=weak_threshold*n)&&roi[i];
        roi_count+=roi[i]!=0;dense_count+=roi[i]&&(16*o>=dense_threshold*n);
        // Pack a 4-bit quiet counter and 4-bit block confidence into the
        // existing byte; this adds no DDR state plane.
        const int old_confidence=old_q[i]>>4;
        const int old_count=old_q[i]&15;
        const bool stable_now=16*qu<=quiet_max*n;
        const int inc=old_count+1;
        const uint8_t next_count=stable_now?uint8_t(inc>stable?stable:inc):0;
        const bool release_evidence=(o==0)&&(mo==0)&&stable_now;
        const bool new_activity=weak[i]&&mo>0&&(16*oo<weak_threshold*n);
        int z=weak[i]?10:0;
        if(16*o>=dense_threshold*n)z=15;
        int c=old_confidence;
        if(16*o>=dense_threshold*n)c=15;
        else if(new_activity&&c<10)c=10;
        else if(old_confidence>=8&&weak[i]&&!release_evidence)c=old_confidence;
        else {
            if(release_evidence)z=0;
            int diff=z-c;
            if(diff>0)c+=(diff+2)/4;
            else if(diff<0){int step=(-diff+2)/4;if(step==0)step=1;c-=step;}
        }
        if(c<0)c=0;if(c>15)c=15;
        q[i]=uint8_t((uint8_t(c)<<4)|next_count);
        seed[i]=weak[i]&&((16*o>=dense_threshold*n)||
                          (mo>0&&16*oo<weak_threshold*n)||c>=10);
        const uint16_t old=old_ttl[i]>hold?hold:old_ttl[i];dec[i]=old?old-1:0;
    }
    if(invalid)return 2;
    if(roi_count>0 && 4*dense_count>=3*roi_count){
        for(int i=0;i<count;++i){
#pragma HLS LOOP_TRIPCOUNT min=1 max=8160
#pragma HLS PIPELINE II=1
            ttl_out[i]=old_ttl[i]>hold?hold:old_ttl[i];
            q_out[i]=old_q[i];seed_out[i]=0;
            m_out[i]=region[i]&&(old_q[i]>>4)>=8;w_out[i]=0;
        }
        return 0;
    }
    const int dy[12]={-1,-1,-1,0,0,1,1,1,-2,2,0,0};
    const int dx[12]={-1,0,1,-1,1,-1,0,1,0,0,-2,2};
propagate:
    for(int y=0;y<gh;++y){
#pragma HLS LOOP_TRIPCOUNT min=1 max=68
        for(int x=0;x<gw;++x){
#pragma HLS LOOP_TRIPCOUNT min=1 max=120
            const int i=y*gw+x;uint16_t next=(seed[i]||(q[i]>>4)>=8)?hold:dec[i];
            for(int k=0;k<12;++k){
                const int ny=y+dy[k],nx=x+dx[k];
                if(ny>=0&&ny<gh&&nx>=0&&nx<gw){const int ni=ny*gw+nx;if(weak[ni]&&dec[ni]>next)next=dec[ni];}
            }
            const bool newly_confirmed=(q[i]>>4)>=10;
            const bool previously_confirmed=(old_q[i]>>4)>=8;
            ttl[i]=weak[i]?next:0;
            core[i]=weak[i]&&(newly_confirmed||previously_confirmed||ttl[i]>0);
        }
    }
guard:
    for(int y=0;y<gh;++y){
#pragma HLS LOOP_TRIPCOUNT min=1 max=68
        for(int x=0;x<gw;++x){
#pragma HLS LOOP_TRIPCOUNT min=1 max=120
            const int i=y*gw+x;bool display=false,protect=false;
            for(int oy=-2;oy<=2;++oy){for(int ox=-2;ox<=2;++ox){
                const int ny=y+oy,nx=x+ox;
                if(ny>=0&&ny<gh&&nx>=0&&nx<gw&&core[ny*gw+nx]){
                    protect=true;if(oy>=-1&&oy<=1&&ox>=-1&&ox<=1)display=true;
                }
            }}
            ttl_out[i]=ttl[i];q_out[i]=q[i];seed_out[i]=seed[i];
            m_out[i]=region[i]&&display;w_out[i]=region[i]&&!protect&&(q[i]&15)>=stable;
        }
    }
    return 0;
}
