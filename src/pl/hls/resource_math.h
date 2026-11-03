#ifndef WB_RESOURCE_MATH_H
#define WB_RESOURCE_MATH_H
// Explicitly bind the three luminance products. No change to integer rounding.
static int wb_luma(int r,int g,int b){
#pragma HLS INLINE
    int r77=77*r,g150=150*g,b29=29*b;
#pragma HLS BIND_OP variable=r77 op=mul impl=dsp latency=2
#pragma HLS BIND_OP variable=g150 op=mul impl=dsp latency=2
#pragma HLS BIND_OP variable=b29 op=mul impl=dsp latency=2
    return (r77+g150+b29)>>8;
}
#endif
