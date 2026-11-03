#ifndef WB_LOCAL_SUM_TREE_H
#define WB_LOCAL_SUM_TREE_H
#include <stdint.h>
// Original 49 unsigned luminance values sum to at most 12495.
// Pad with zero; use a registered fabric reduction, preserving exact integers.
inline uint16_t wb_local_sum(const uint8_t win[7][7]) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=win complete dim=0
    uint16_t terms[64];
#pragma HLS ARRAY_PARTITION variable=terms complete
    for(unsigned i=0;i<64;++i) {
#pragma HLS UNROLL
        terms[i]=i<49?win[i/7][i%7]:0;
    }
    for(unsigned span=32;span>0;span/=2) {
#pragma HLS UNROLL
        for(unsigned i=0;i<span;++i) {
#pragma HLS UNROLL
            uint16_t partial=terms[2*i]+terms[2*i+1];
#pragma HLS BIND_OP variable=partial op=add impl=fabric latency=1
            terms[i]=partial;
        }
    }
    return terms[0];
}
#endif
