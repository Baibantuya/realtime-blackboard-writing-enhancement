#ifndef WB_SCENE_RAY_TALLY_H
#define WB_SCENE_RAY_TALLY_H
#include <stdint.h>

namespace wb_scene_detail {
// Six binary terms, padded to eight; every sum is in [0, 6].
inline uint8_t sum8(uint8_t terms[8]) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=terms complete
    for(unsigned span=4;span>0;span/=2) {
#pragma HLS UNROLL
        for(unsigned i=0;i<span;++i) {
#pragma HLS UNROLL
            uint8_t partial=terms[2*i]+terms[2*i+1];
#pragma HLS BIND_OP variable=partial op=add impl=fabric
            terms[i]=partial;
        }
    }
    return terms[0];
}

inline void ray_tally(const uint8_t labels[6], uint8_t count[8],
                      uint8_t &positive, uint8_t &negative, uint8_t &total) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=labels complete
#pragma HLS ARRAY_PARTITION variable=count complete
    bool valid[6];
    uint8_t masks[6];
    uint8_t total_terms[8]={0,0,0,0,0,0,0,0};
#pragma HLS ARRAY_PARTITION variable=valid complete
#pragma HLS ARRAY_PARTITION variable=masks complete
#pragma HLS ARRAY_PARTITION variable=total_terms complete
    for(unsigned side=0;side<2;++side) {
#pragma HLS UNROLL
        bool connected=true;
        for(unsigned k=0;k<3;++k) {
#pragma HLS UNROLL
            const unsigned slot=side*3+k;
            const unsigned label=labels[slot];
            // Invalid nonzero labels do not break connectivity in the original.
            connected=connected && label!=0;
            valid[slot]=connected && label<=7;
            total_terms[slot]=valid[slot]?1:0;
            masks[slot]=valid[slot]?uint8_t(1u<<label):uint8_t(0);
        }
    }
    negative=masks[0]|masks[1]|masks[2];
    positive=masks[3]|masks[4]|masks[5];
    total=sum8(total_terms);
    count[0]=0;
    for(unsigned c=1;c<=7;++c) {
#pragma HLS UNROLL
        uint8_t terms[8]={0,0,0,0,0,0,0,0};
#pragma HLS ARRAY_PARTITION variable=terms complete
        for(unsigned j=0;j<6;++j) {
#pragma HLS UNROLL
            terms[j]=(valid[j] && labels[j]==c)?1:0;
        }
        count[c]=sum8(terms);
    }
}
}
#endif
