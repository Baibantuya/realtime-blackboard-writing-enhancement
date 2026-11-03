#include "board_scene_quantize.h"
#include "rgb565.h"
#include "scene_stream.h"
#include "ray_tally.h"

namespace {
// Six shared RGB565 line buffers; no additional frame/metadata plane.
// WB_FUSION_WINDOW=5 is a native A/B probe, not a runtime hardware parameter.
#ifndef WB_FUSION_WINDOW
#define WB_FUSION_WINDOW 7
#endif
#ifndef WB_FUSION_DARK
#define WB_FUSION_DARK 1
#endif
#ifndef WB_FUSION_HUE
#define WB_FUSION_HUE 1
#endif
#ifndef WB_COLOR_VOTE_FRAMES
#define WB_COLOR_VOTE_FRAMES 2
#endif
#ifndef WB_COLOR_PREFER_CHROMA
#define WB_COLOR_PREFER_CHROMA 1
#endif
const unsigned MAX_W = 1920, N = WB_FUSION_WINDOW, RADIUS = N/2, AREA=N*N;
int maximum(int a, int b) {
#pragma HLS INLINE
    return a > b ? a : b;
}
int absolute(int a) {
#pragma HLS INLINE
    return a < 0 ? -a : a;
}
uint8_t channel(uint16_t p, unsigned c) {
#pragma HLS INLINE
    return (wb_expand565(p) >> (8*c)) & 255;
}

// Explicit balanced reductions avoid serial conditional accumulator chains.
// All spatial sums fit 16 bits (49 * 255); ray counts fit 8 bits (24).
template<typename T, unsigned SIZE> T balanced_sum(T terms[SIZE]) {
#pragma HLS INLINE
#pragma HLS ARRAY_PARTITION variable=terms complete
    for(unsigned span=SIZE/2;span>0;span/=2) {
#pragma HLS UNROLL
        for(unsigned i=0;i<span;++i) {
#pragma HLS UNROLL
            if (sizeof(T)==1) {
                // Vote counts are at most 24; infer LUT/carry logic for the
                // narrow add tree instead of chaining dedicated DSP blocks.
                T vote_sum=terms[2*i]+terms[2*i+1];
#pragma HLS BIND_OP variable=vote_sum op=add impl=fabric
                terms[i]=vote_sum;
            } else {
                // Preserve the sum and its type; register each fabric add
                // instead of cascading multiple DSP ALUs in one cycle.
                T spatial_sum=terms[2*i]+terms[2*i+1];
#pragma HLS BIND_OP variable=spatial_sum op=add impl=fabric latency=1
                terms[i]=spatial_sum;
            }
        }
    }
    return terms[0];
}
int residual(uint16_t p, uint16_t surface) {
#pragma HLS INLINE
    int d = 0;
    for (unsigned c=0; c<3; ++c) {
#pragma HLS UNROLL
        d = maximum(d, absolute(channel(p,c)-channel(surface,c)));
    }
    return d;
}
bool dark_material(uint16_t p, uint16_t surface) {
#pragma HLS INLINE
    int level=maximum(channel(p,0),maximum(channel(p,1),channel(p,2)));
    int board=maximum(channel(surface,0),maximum(channel(surface,1),channel(surface,2)));
    // Do not lower the accepted bright-region thresholds. Both observed ink
    // and trusted material must indicate a shadow, never current people alone.
    return WB_FUSION_DARK && level<112 && board<80;
}
bool neutral(uint16_t p, uint16_t surface) {
#pragma HLS INLINE
    int r=channel(p,0), g=channel(p,1), b=channel(p,2);
    int hi=maximum(r,maximum(g,b)), lo=r<g?(r<b?r:b):(g<b?g:b);
    // Confirmed neutral is protected from every color seed in its window.
    // At low signal a fixed 24-level neutral range swallowed faint blue.
    // Use a relative spread with RGB565 allowance, still protecting true gray.
    if(dark_material(p,surface)) return lo>=32 && hi-lo<=maximum(12,((hi*24)>>8)+8);
    return lo>=64 && hi-lo<=24;
}
bool soft_hue(uint16_t p, unsigned wanted) {
#pragma HLS INLINE
    int r=channel(p,0),g=channel(p,1),b=channel(p,2);
    int lo=r<g?(r<b?r:b):(g<b?g:b),hi=maximum(r,maximum(g,b));
    // A low-signal red/blue-biased sample is not confirmed neutral. A true gray
    // or a <=12-level white tint cannot borrow this directional hue. The floor
    // includes the unequal 5/6/5-bit expansion error on faint white samples.
    bool biased=wanted==2?(r>=b+8 && r>=g+4):(b>=r+8 && b>=g+4);
    return lo<112 && hi-lo>12 && biased;
}
uint8_t color_chroma(uint16_t p, uint16_t surface, uint8_t delta, uint8_t margin) {
#pragma HLS INLINE
    if (residual(p,surface)<int(delta)) return 0;
    if (neutral(p,surface)) return 1;
    int r=channel(p,0), g=channel(p,1), b=channel(p,2);
    int surface_g=channel(surface,1);
    if(dark_material(p,surface)) {
        unsigned level=maximum(r,maximum(g,b));
        margin=maximum(8,int((margin*level+255)>>8));
    }
    int half_margin=maximum(4,int(margin>>1));
    // The thresholds deliberately separate the four added chalk colors from
    // the existing red/blue/green classes. Orange and pink are red-led hues;
    // yellow is the balanced high-red/high-green case.
    if (r>=b+int(margin) && g>=b+int(margin) && absolute(r-g)<=2*int(margin)) return 6; // yellow
    if (r>=g+int(margin) && r>=b+int(margin)) {
        if (b>=g+half_margin) return 7; // pink
        if (g>=b+half_margin) return 5; // orange
        return 2;                        // red
    }
    if (b>=r+int(margin) && b>=g+int(margin)) return 3;
    // A green board is not green ink; require contrast above the material.
    if (g>=r+int(margin) && g>=b+int(margin) && g-surface_g>=int(delta)) return 4;
    return 0;
}
uint8_t pigment(uint16_t p, uint16_t surface, uint8_t delta, uint8_t margin) {
#pragma HLS INLINE
    return color_chroma(p,surface,delta,margin);
}
uint16_t palette(unsigned label, unsigned order) {
#pragma HLS INLINE
    uint16_t p=0xffff;
    if(label==1) p=0;
    else if(label==2) p=wb_pack565(255u);
    else if(label==3) p=wb_pack565((96u<<8)|(255u<<16));
    else if(label==4) p=wb_pack565(160u<<8);
    else if(label==5) p=wb_pack565(255u|(128u<<8));
    else if(label==6) p=wb_pack565(255u|(220u<<8)|(32u<<16));
    else if(label==7) p=wb_pack565(255u|(96u<<8)|(160u<<16));
    return order&2 ? wb_swap565(p) : p;
}

unsigned color_vote_next(unsigned old, unsigned observed, bool bare, bool visible) {
#pragma HLS INLINE
    if(!visible) return old;
    unsigned label=old&7;
    bool pending=(old&8)!=0;
    // The existing 4-bit canvas cell is the only persistent PL-side state.
    // R6 uses it for a bounded two-frame confirmation instead of adding a
    // frame-sized history buffer or changing the PS/PL ABI.
    if(label==0) {
        if(!observed || bare) return 0;
#if WB_COLOR_VOTE_FRAMES > 1
        return observed|8u;
#else
        return observed;
#endif
    }
    if(pending) {
        if(bare) return 0; // second bare frame confirms erase
        if(observed==label) return label; // agreeing second frame locks color
        if(!observed) return old;
#if WB_COLOR_PREFER_CHROMA
        if(label==1 && observed>=2) return observed|8u;
        if(observed==1 && label>=2) return label|8u;
#endif
        return label|8u; // retain the first candidate on a color disagreement
    }
    if(bare) return label|8u;
    // Once confirmed, the label is stable until an erase/reveal path clears it.
    return label;
}

// The same finite window provides structure and color evidence. No full-frame
// on-chip candidate plane, sorting network or floating-point datapath.
unsigned stroke(uint16_t win[N][N], uint16_t surface, unsigned delta,
                unsigned margin, unsigned cx, unsigned cy, unsigned w, unsigned h) {
#pragma HLS INLINE
    uint16_t center=win[RADIUS][RADIUS];
    bool shadow=dark_material(center,surface);
    uint16_t sums[3]={0,0,0};
    uint16_t sum_terms[3][64]={{0}};
#pragma HLS ARRAY_PARTITION variable=sum_terms complete dim=0
#pragma HLS ARRAY_PARTITION variable=sums complete
    for(unsigned row=0;row<N;++row) {
#pragma HLS UNROLL
        for(unsigned col=0;col<N;++col) {
#pragma HLS UNROLL
            int nx=int(cx)+int(col)-int(RADIUS),ny=int(cy)+int(row)-int(RADIUS);
            // Invalid padding contributes the center, never black. At an image
            // edge the valid contrast is conservative rather than manufactured.
            uint16_t p=nx>=0&&ny>=0&&nx<int(w)&&ny<int(h)?win[row][col]:center;
            for(unsigned c=0;c<3;++c) {
#pragma HLS UNROLL
                sum_terms[c][row*N+col]=channel(p,c);
            }
        }
    }
    for(unsigned c=0;c<3;++c) {
#pragma HLS UNROLL
        sums[c]=balanced_sum<uint16_t,64>(sum_terms[c]);
    }
    int contrast=0;
    int background_rise=0;
    for(unsigned c=0;c<3;++c) {
#pragma HLS UNROLL
        contrast=maximum(contrast,int(AREA)*channel(center,c)-sums[c]);
        background_rise=maximum(background_rise,sums[c]-int(AREA)*channel(surface,c));
    }
    // A broad lifted neighborhood is illumination, not evidence that this is
    // an underexposed stroke. Keep the accepted glare thresholds in that case.
    shadow=shadow && background_rise<=int(24*AREA);
    if(shadow) {
        int board=maximum(channel(surface,0),maximum(channel(surface,1),channel(surface,2)));
        int scaled=maximum(12,int(delta)*board/80);
        if(scaled<int(delta)) delta=scaled;
    }
    // Absolute frozen-material difference alone cannot admit smooth glare.
    // Every center, including an inherited edge, needs its own local evidence.
    unsigned weak=maximum(shadow?4:6,int((delta+2)/3));
    if(contrast<int(weak*AREA)) return 0;
    unsigned own=pigment(center,surface,delta,margin);
    // A low-contrast edge is not a seed. It may only inherit from two or more
    // strong aligned samples of a single pigment; material itself stays board.
    if(!own && residual(center,surface)>=int((delta+1)>>1)) own=8; // ambiguous, not orange
    if(!own) return 0;
    uint8_t votes[8]={0,0,0,0,0,0,0,0};
#pragma HLS ARRAY_PARTITION variable=votes complete
    // Reuse the directional evidence below for the local color estimate.
    // Keeping the estimate as small ray counts avoids a second set of three
    // fully unrolled RGB accumulators, which otherwise expands the Q enough
    // to exceed the KV260 CLB/LUT budget.
    unsigned support=0;

    uint8_t directions[4]={0,0,0,0};
#pragma HLS ARRAY_PARTITION variable=directions complete
    uint8_t hue_direction[2][4]={{0,0,0,0},{0,0,0,0}},white_direction[4]={0,0,0,0};
    uint8_t opposed_direction[2][4]={{0,0,0,0},{0,0,0,0}};
    uint8_t positive_hue[2]={0,0},negative_hue[2]={0,0};
    // V23: six local ray samples per direction, reusing the existing 7x7
    // pigment classification. No flood-fill, label frame or extra line RAM.
    // Every ray prefix must be ink: a bare gap prevents another stroke voting.
    uint8_t ray_labels[4][6]={{0}};
#pragma HLS ARRAY_PARTITION variable=ray_labels complete dim=0
#pragma HLS ARRAY_PARTITION variable=hue_direction complete dim=0
#pragma HLS ARRAY_PARTITION variable=white_direction complete
#pragma HLS ARRAY_PARTITION variable=opposed_direction complete dim=0
#pragma HLS ARRAY_PARTITION variable=positive_hue complete
#pragma HLS ARRAY_PARTITION variable=negative_hue complete
    for(unsigned row=0;row<N;++row) {
#pragma HLS UNROLL
        for(unsigned col=0;col<N;++col) {
#pragma HLS UNROLL
            int nx=int(cx)+int(col)-int(RADIUS), ny=int(cy)+int(row)-int(RADIUS);
            bool inside=nx>=0 && ny>=0 && nx<int(w) && ny<int(h);
            // Reuse four rays (24 taps); off-ray pigment datapaths only fed
            // the weak support count and cost 24 redundant classifiers.
            bool aligned=row==RADIUS || col==RADIUS || row==col || row+col==N-1;
            if(aligned && inside && (row!=RADIUS || col!=RADIUS)) {
                uint16_t sample=win[row][col];
                int strength=0;
                for(unsigned c=0;c<3;++c) {
#pragma HLS UNROLL
                    strength=maximum(strength,int(AREA)*channel(sample,c)-sums[c]);
                }
                unsigned p=strength>=int(weak*AREA)?pigment(sample,surface,delta,margin):0;
                // Along four directions: two independent samples, never one
                // adjacent seed, and never a flood fill across other strokes.
                // Span two independent pixels on each side where available;
                // compact weak 2x2 clusters cannot certify a five-pixel stroke.
                int dy=int(row)-int(RADIUS),dx=int(col)-int(RADIUS);
                for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
                    bool along=d==0?!dy:(d==1?!dx:(d==2?dx==dy:dx==-dy));
                    if(along && absolute(dx)<=3 && absolute(dy)<=3) {
                        int distance=d==0?dx:dy;
                        unsigned slot=distance<0?unsigned(-distance-1):unsigned(distance+2);
                        ray_labels[d][slot]=p;
                    }
                    if(along && p) {
                        bool soft_red=soft_hue(sample,2),soft_blue=soft_hue(sample,3);
                        if(p==1 && !soft_red && !soft_blue) ++white_direction[d];
                        for(unsigned hue=0;hue<2;++hue) {
#pragma HLS UNROLL
                            unsigned wanted=hue+2,other=3-hue;
                            if(p==wanted || (p==1 && (hue==0?soft_red:soft_blue))) {
                                ++hue_direction[hue][d];
                                int along_sign=d==0?dx:dy;
                                if(along_sign>0) positive_hue[hue]|=1u<<d;
                                else negative_hue[hue]|=1u<<d;
                            }
                            if(p==other || p==4 || (p==1 && (hue==0?soft_blue:soft_red)))
                                ++opposed_direction[hue][d];
                        }
                    }
                }
                if(p && absolute(dx)<=2 && absolute(dy)<=2) {
                    if(!dy) ++directions[0];
                    if(!dx) ++directions[1];
                    if(dx==dy) ++directions[2];
                    if(dx==-dy) ++directions[3];
                }
            }
        }
    }
    for(unsigned c=1;c<=7;++c) {
#pragma HLS UNROLL
        uint8_t terms[32]={0};
#pragma HLS ARRAY_PARTITION variable=terms complete
        for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
            for(unsigned k=0;k<6;++k) {
#pragma HLS UNROLL
                terms[d*6+k]=ray_labels[d][k]==c;
            }
        }
        votes[c]=balanced_sum<uint8_t,32>(terms);
    }
    support=(unsigned(votes[1])+votes[2])+(unsigned(votes[3])+votes[4])+
            (unsigned(votes[5])+votes[6])+votes[7];
    bool directional=false;
    for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
        directional|=directions[d]>=3 || ((shadow || contrast>=int(delta*AREA))&&directions[d]>=2);
    }
    bool dot=contrast>=int(2*delta*AREA) && residual(center,surface)>=144;
    if(!directional && !dot) return 0;
    // Correct a one/two-pixel color island inside a continuous chalk stroke.
    // Demand a unique >=4/6 pigment certificate, spanning both sides, and
    // at most one incompatible neighbor on that same line. A coherent center
    // pigment on another line protects real differently colored crossings.
    unsigned coherent=0;
    bool coherent_conflict=false,own_span=false;
    for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
        uint8_t count[8]={0,0,0,0,0,0,0,0};
        uint8_t positive=0,negative=0,total=0;
#pragma HLS ARRAY_PARTITION variable=count complete
        wb_scene_detail::ray_tally(ray_labels[d],count,positive,negative,total);
        for(unsigned c=1;c<=7;++c) {
#pragma HLS UNROLL
            bool span=(positive & negative & (1u<<c))!=0;
            if(own==c && count[c]>=3 && span) own_span=true;
            if(count[c]>=4 && total-count[c]<=1 && span) {
                if(coherent && coherent!=c) coherent_conflict=true;
                coherent=c;
            }
        }
    }
    // A bright achromatic center is actual white-chalk evidence, including
    // white punctuation over colored ink; local hue votes must not dye it.
    int center_low=channel(center,0)<channel(center,1)?channel(center,0):channel(center,1);
    center_low=center_low<channel(center,2)?center_low:channel(center,2);
    bool bright_white=own==1 && center_low>=112;
    // A local ink-color estimate suppresses RGB565 color speckles in both
    // directions: white strokes become neutral; blue/red strokes keep hue.
    // Require neutral evidence before whitening. A <=12-level center tint
    // cannot borrow adjacent color, preserving dim white crossings.
    // Saturated centers and bright white centers retain the prior safeguards.
    int cr=channel(center,0),cg=channel(center,1),cb=channel(center,2);
    int chroma=maximum(cr,maximum(cg,cb))-center_low;
    unsigned blue_support=maximum(hue_direction[1][0],maximum(hue_direction[1][1],
        maximum(hue_direction[1][2],hue_direction[1][3])));
    unsigned red_support=maximum(hue_direction[0][0],maximum(hue_direction[0][1],
        maximum(hue_direction[0][2],hue_direction[0][3])));
    unsigned neutral_support=maximum(white_direction[0],maximum(white_direction[1],
        maximum(white_direction[2],white_direction[3])));
    if(support>=4 && chroma<64 && !bright_white) {
        if(blue_support>=3 && blue_support>red_support+1 && chroma>12 && cb>=cr+8 && cb>=cg+4) return 3;
        if(red_support>=3 && red_support>blue_support+1 && chroma>12 && cr>=cb+8 && cr>=cg+4) return 2;
        if(neutral_support>=3 && blue_support<=1 && red_support<=1 && own!=4) return 1;
    }
    if(coherent && !coherent_conflict && !own_span && !bright_white) return coherent;
    unsigned propagated=0;bool hue_conflict=false;
    for(unsigned hue=0;hue<2;++hue) {
#pragma HLS UNROLL
        unsigned wanted=hue+2;
        if(WB_FUSION_HUE && WB_FUSION_DARK && (own==1 || own==wanted) && soft_hue(center,wanted)) {
            for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
                // Three independent compatible samples along the SAME stroke.
                if(hue_direction[hue][d]>=3 && !white_direction[d] && !opposed_direction[hue][d]) {
                    if(propagated && propagated!=wanted) hue_conflict=true;
                    propagated=wanted;
                }
            }
        }
    }
    if(propagated && !hue_conflict) return propagated;
    if(WB_FUSION_HUE && WB_FUSION_DARK && own==1) {
        int lo=channel(center,0)<channel(center,1)?channel(center,0):channel(center,1);
        lo=lo<channel(center,2)?lo:channel(center,2);
        bool white_span=false;
        for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
            white_span|=white_direction[d]>=3;
        }
        propagated=0;hue_conflict=false;
        for(unsigned hue=0;hue<2;++hue) {
#pragma HLS UNROLL
            for(unsigned d=0;d<4;++d) {
#pragma HLS UNROLL
                // A dim hole needs one hue on BOTH sides. White spans veto;
                // incompatible red/blue certificates never win by loop order.
                if(lo<112 && !white_span && hue_direction[hue][d]>=3 && white_direction[d]<=1 &&
                        !opposed_direction[hue][d] && (positive_hue[hue]&negative_hue[hue]&(1u<<d))) {
                    if(propagated && propagated!=hue+2) hue_conflict=true;
                    propagated=hue+2;
                }
            }
        }
        if(propagated && !hue_conflict) return propagated;
    }
    if(own>=1 && own<=7) {
        int r=channel(center,0),g=channel(center,1),b=channel(center,2);
        int lo=r<g?(r<b?r:b):(g<b?g:b);
        int hi=maximum(r,maximum(g,b));
        if(own==1 && votes[1]<2 && (lo<112 || hi-lo>8)) {
            // Low-luma neutral is ambiguous gray, not confirmed white pigment.
            // Only a unique multi-seed hue may bridge it; white stroke support
            // or a bright neutral center always prevents recoloring.
            for(unsigned c=2;c<=7;++c) {
#pragma HLS UNROLL
                bool compatible=(c==2 && r>=g+16 && r>=b+16) ||
                    (c==3 && b>=r+8 && b>=g+4) ||
                    (c==4 && g>=r+16 && g>=b+16) ||
                    (c==5 && r>=g+16 && g>=b+8) ||
                    (c==6 && r>=b+16 && g>=b+16 && absolute(r-g)<=32) ||
                    (c==7 && r>=g+16 && b>=g+16) || (lo<112 && hi-lo<=8);
                bool unique=true;
                for(unsigned other=2;other<=7;++other) {
#pragma HLS UNROLL
                    if(other!=c && votes[c]<=votes[other]) unique=false;
                }
                if(compatible && votes[c]>=2 && unique) return c;
            }
        }
        if(own>=2 && own<=7 && votes[own]<2 && votes[1]>=2) {
            // Even a saturated isolated colored sample cannot overrule a
            // neutral stroke without independent support for its own pigment.
            return 1;
        }
        // Bright isolated punctuation survives; weaker isolated speckles do not.
        return support>=2 || residual(center,surface)>=144 ? own : 0;
    }
    if(support<2) return 0;
    unsigned chosen=0, best=1;
    for(unsigned c=1;c<=7;++c) {
#pragma HLS UNROLL
        if(votes[c]>best) { chosen=c; best=votes[c]; }
    }
    // Ambiguous gray may inherit a coherent hue; red/blue ties stay unresolved.
    for(unsigned c=1;c<=7;++c) {
#pragma HLS UNROLL
        if(chosen && c!=chosen && votes[c]==best) chosen=0;
    }
    return chosen;
}
}


namespace {
// One owner per AXI bundle. Independent burst readers/writers sharing a
// bundle can hold the channel while waiting for each other's finite FIFOs.
void read_inputs(const uint32_t* src, const uint32_t* canvas, const uint32_t* metadata,
                 scene::stream<uint32_t>& raw, scene::stream<uint32_t>& cells,
                 scene::stream<uint32_t>& tiles, unsigned width, unsigned height, unsigned control) {
#pragma HLS INLINE off
    if(control&WB_SCENE_HOLD) {
        for(unsigned i=0;i<width*height/8;++i) {
#pragma HLS PIPELINE II=1
            cells.write(canvas[i]);
        }
        return;
    }
    for(unsigned y=0;y<height+RADIUS;++y) {
        if(y>=RADIUS && ((y-RADIUS)&15)==0) {
            for(unsigned bx=0;bx<width/16;++bx) {
#pragma HLS PIPELINE II=1
                tiles.write(metadata[((y-RADIUS)/16)*(width/16)+bx]);
            }
        }
        for(unsigned x=0;x<width;x+=128) {
            unsigned pixels=width-x<128?width-x:128;
            if(y<height) for(unsigned i=0;i<pixels/2;++i) {
#pragma HLS PIPELINE II=1
                raw.write(src[y*(width/2)+x/2+i]);
            }
            if(y>=RADIUS) for(unsigned i=0;i<pixels/8;++i) {
#pragma HLS PIPELINE II=1
                cells.write(canvas[(y-RADIUS)*(width/8)+x/8+i]);
            }
        }
    }
}
void write_outputs(uint32_t* canvas, uint32_t* dst, unsigned width, unsigned height, unsigned stride,
                   scene::stream<uint32_t>& cells, scene::stream<uint32_t>& pixels) {
#pragma HLS INLINE off
    for(unsigned y=0;y<height;++y) for(unsigned x=0;x<width;x+=128) {
        unsigned count=width-x<128?width-x:128;
        for(unsigned i=0;i<count/2;++i) {
#pragma HLS PIPELINE II=1
            dst[y*(stride/4)+x/2+i]=pixels.read();
        }
        for(unsigned i=0;i<count/8;++i) {
#pragma HLS PIPELINE II=1
            canvas[y*(width/8)+x/8+i]=cells.read();
        }
    }
}
void scan(scene::stream<uint32_t>& input, scene::stream<uint32_t>& tiles,
          scene::stream<uint16_t>& verdicts, unsigned width, unsigned height,
          unsigned control, unsigned order, unsigned ink_delta, unsigned erase_delta, unsigned color_margin) {
#pragma HLS INLINE off
    const unsigned gw=width>>4;
    if(control&WB_SCENE_HOLD) return;
    uint16_t lines[N-1][MAX_W], win[N][N];
    uint32_t tile_row[120];
#pragma HLS ARRAY_PARTITION variable=lines complete dim=1
// R6 moves the six deep spatial line banks to spare URAM; this releases BRAM
// tiles and prevents the line store from falling back into CLBM/LUTRAM.
#pragma HLS BIND_STORAGE variable=lines type=ram_t2p impl=uram
#pragma HLS ARRAY_PARTITION variable=win complete dim=0
#pragma HLS BIND_STORAGE variable=tile_row type=ram_1p impl=lutram
    for(unsigned x=0;x<width;++x) {
#pragma HLS PIPELINE II=1
        for(unsigned r=0;r<N-1;++r) {
#pragma HLS UNROLL
            lines[r][x]=0;
        }
    }
    uint32_t source_word=0;
    for(unsigned y=0;y<height+RADIUS;++y) {
        // Cache one grid row; metadata is not fetched once per pixel.
        if(y>=RADIUS && ((y-RADIUS)&15)==0 && y-RADIUS<height) {
            for(unsigned bx=0;bx<gw;++bx) {
#pragma HLS PIPELINE II=1
                tile_row[bx]=tiles.read();
            }
        }
        for(unsigned x=0;x<width+RADIUS;++x) {
#pragma HLS PIPELINE II=1
            uint16_t pixel=0;
            if(y<height && x<width) {
                if(!(x&1)) source_word=input.read();
                pixel=uint16_t(source_word>>(16*(x&1)));
                if(order&1) pixel=wb_swap565(pixel);
            }
            uint16_t column[N];
#pragma HLS ARRAY_PARTITION variable=column complete
            for(unsigned r=0;r<N-1;++r) {
#pragma HLS UNROLL
                column[r]=x<width?lines[r][x]:0;
                if(x<width) lines[r][x]=r==N-2?pixel:lines[r+1][x];
            }
            column[N-1]=pixel;
            for(unsigned r=0;r<N;++r) {
#pragma HLS UNROLL
                for(unsigned c=0;c<N-1;++c) {
#pragma HLS UNROLL
                    win[r][c]=x?win[r][c+1]:0;
                }
                win[r][N-1]=column[r];
            }
            if(y>=RADIUS && x>=RADIUS) {
                unsigned cx=x-RADIUS, cy=y-RADIUS;
                uint32_t meta=tile_row[cx>>4];
                uint16_t surface=uint16_t(meta);
                bool visible=(meta&WB_SCENE_VISIBLE) && (meta&WB_SCENE_SURFACE_VALID) && !(meta&WB_SCENE_OCCLUDED);
                unsigned noise=(meta>>24)&31;
                unsigned erase_limit=erase_delta;
                if(dark_material(win[RADIUS][RADIUS],surface)) {
                    int board=maximum(channel(surface,0),maximum(channel(surface,1),channel(surface,2)));
                    int scaled=maximum(4,int(erase_delta)*board/80);
                    if(scaled<int(erase_limit)) erase_limit=scaled;
                }
                // A shadow stroke admitted below the old absolute threshold
                // must not simultaneously count as bare material on a weak
                // structure frame. Keep independent positive erasure evidence.
                bool bare=residual(win[RADIUS][RADIUS],surface)<=int(erase_limit+noise);
                // Pure spatial verdict: never depends on a preceding pixel's
                // run label or canvas state. HLS can pipeline the full window
                // computation without putting it on a one-cycle feedback path.
                unsigned full=0,center_pigment=0;
                if(visible && !bare) {
                    center_pigment=pigment(win[RADIUS][RADIUS],surface,ink_delta+noise,color_margin);
                    full=stroke(win,surface,ink_delta+noise,color_margin,cx,cy,width,height);
                }
                bool reveal=(meta&WB_SCENE_REVEAL_OBSERVATION) &&
                    (meta&WB_SCENE_SURFACE_VALID) && !(meta&WB_SCENE_OCCLUDED);
                uint16_t packet=uint16_t(full | (center_pigment<<4) | (unsigned(bare)<<8) |
                    (unsigned(visible)<<9) | (unsigned(bool(meta&WB_SCENE_INITIALIZE))<<10) |
                    (unsigned(reveal)<<11));
                verdicts.write(packet);
            }
        }
    }

}
// Preserve R6 run reuse, palette and temporal state exactly, after the
// independent window pipeline. Only short mux/counter paths feed back here.
void apply_verdicts(scene::stream<uint16_t>& verdicts, scene::stream<uint32_t>& canvas,
                    scene::stream<uint32_t>& cells, scene::stream<uint32_t>& pixels,
                    unsigned width,unsigned height,unsigned control,unsigned order) {
#pragma HLS INLINE off
    if(control&WB_SCENE_HOLD) {
        for(unsigned i=0;i<width*height/8;++i) {
            uint32_t value=canvas.read()&0x77777777u;
            cells.write(value);
            for(unsigned k=0;k<4;++k) {
#pragma HLS PIPELINE II=1
                unsigned a=(value>>(8*k))&7, b=(value>>(8*k+4))&7;
                pixels.write(palette(a,order)|(uint32_t(palette(b,order))<<16));
            }
        }
        return;
    }
    uint32_t old_cells=0,new_cells=0,out_pair=0;
    unsigned run_label=0,run_left=0;
    for(unsigned y=0;y<height;++y) {
        for(unsigned cx=0;cx<width;++cx) {
#pragma HLS PIPELINE II=1
            uint16_t packet=verdicts.read();
            unsigned shift=4*(cx&7);
            if(!(cx&7)) {old_cells=canvas.read();new_cells=0;}
            unsigned old=(old_cells>>shift)&15,next=old&7;
            unsigned full=packet&7,center_pigment=(packet>>4)&7;
            bool bare=(packet&256)!=0,visible=(packet&512)!=0;
            if(visible) {
                unsigned observed=0;
                if(bare) {run_label=0;run_left=0;}
                else {
                    bool conflict=center_pigment && center_pigment!=run_label;
                    if(run_left && run_label && !conflict) {observed=run_label;--run_left;}
                    else {
                        observed=full;
                        if(observed) {run_label=observed;run_left=3;}
                        else {run_label=0;run_left=0;}
                    }
                }
                unsigned state_old=(packet&1024)?0u:old;
                next=color_vote_next(state_old,observed,bare,true);
            } else if((packet&2048) && (old&7)>0 && bare) next=(old&7)|8;
            new_cells|=uint32_t(next)<<shift;
            uint16_t output=palette(next&7,order);
            if(!(cx&1)) out_pair=output;
            else pixels.write(out_pair|(uint32_t(output)<<16));
            if((cx&7)==7) cells.write(new_cells);
        }
    }
}
void render(const uint32_t* src, const uint32_t* canvas_in, uint32_t* canvas_out,
            const uint32_t* metadata, uint32_t* dst, unsigned width, unsigned height,
            unsigned stride, unsigned control, unsigned order, unsigned ink_delta, unsigned erase_delta, unsigned color_margin) {
#pragma HLS DATAFLOW
    scene::stream<uint32_t> raw, old_cells, tiles, cells, pixels;
    scene::stream<uint16_t> verdicts;
#pragma HLS STREAM variable=verdicts depth=64
#pragma HLS BIND_STORAGE variable=verdicts type=fifo impl=lutram
#pragma HLS STREAM variable=raw depth=64
#pragma HLS STREAM variable=old_cells depth=64
#pragma HLS STREAM variable=tiles depth=64
#pragma HLS STREAM variable=cells depth=64
#pragma HLS STREAM variable=pixels depth=64
#pragma HLS BIND_STORAGE variable=raw type=fifo impl=lutram
#pragma HLS BIND_STORAGE variable=old_cells type=fifo impl=lutram
#pragma HLS BIND_STORAGE variable=tiles type=fifo impl=lutram
#pragma HLS BIND_STORAGE variable=cells type=fifo impl=lutram
#pragma HLS BIND_STORAGE variable=pixels type=fifo impl=lutram
#ifdef WB_SCENE_BOUNDED
    std::thread reader([&](){read_inputs(src,canvas_in,metadata,raw,old_cells,tiles,width,height,control);});
    std::thread scanner([&](){scan(raw,tiles,verdicts,width,height,control,order,ink_delta,erase_delta,color_margin);});
    std::thread applier([&](){apply_verdicts(verdicts,old_cells,cells,pixels,width,height,control,order);});
    std::thread writer([&](){write_outputs(canvas_out,dst,width,height,stride,cells,pixels);});
    reader.join();scanner.join();applier.join();writer.join();
#else
    read_inputs(src,canvas_in,metadata,raw,old_cells,tiles,width,height,control);
    scan(raw,tiles,verdicts,width,height,control,order,ink_delta,erase_delta,color_margin);
    apply_verdicts(verdicts,old_cells,cells,pixels,width,height,control,order);
    write_outputs(canvas_out,dst,width,height,stride,cells,pixels);
#endif
}
}

extern "C" uint32_t wb_scene_abi() { return WB_SCENE_ABI; }

extern "C" uint32_t board_scene_quantize(
    const uint32_t* src, const uint32_t* canvas_in, uint32_t* canvas_out,
    const uint32_t* metadata, uint32_t* dst,
    unsigned width, unsigned height, unsigned dst_stride,
    unsigned frame_cookie, unsigned metadata_cookie, unsigned control,
    unsigned order, unsigned ink_delta, unsigned erase_delta, unsigned color_margin) {
#pragma HLS INTERFACE m_axi port=src offset=slave bundle=gmem0 depth=1036800 max_read_burst_length=64 num_read_outstanding=8
#pragma HLS INTERFACE m_axi port=canvas_in offset=slave bundle=gmem0 depth=259200 max_read_burst_length=64
#pragma HLS INTERFACE m_axi port=metadata offset=slave bundle=gmem0 depth=8160 max_read_burst_length=64
#pragma HLS INTERFACE m_axi port=canvas_out offset=slave bundle=gmem1 depth=259200 max_write_burst_length=64
#pragma HLS INTERFACE m_axi port=dst offset=slave bundle=gmem1 depth=1658880 max_write_burst_length=64 num_write_outstanding=8
#pragma HLS INTERFACE s_axilite port=src bundle=control
#pragma HLS INTERFACE s_axilite port=canvas_in bundle=control
#pragma HLS INTERFACE s_axilite port=canvas_out bundle=control
#pragma HLS INTERFACE s_axilite port=metadata bundle=control
#pragma HLS INTERFACE s_axilite port=dst bundle=control
#pragma HLS INTERFACE s_axilite port=width bundle=control
#pragma HLS INTERFACE s_axilite port=height bundle=control
#pragma HLS INTERFACE s_axilite port=dst_stride bundle=control
#pragma HLS INTERFACE s_axilite port=frame_cookie bundle=control
#pragma HLS INTERFACE s_axilite port=metadata_cookie bundle=control
#pragma HLS INTERFACE s_axilite port=control bundle=control
#pragma HLS INTERFACE s_axilite port=order bundle=control
#pragma HLS INTERFACE s_axilite port=ink_delta bundle=control
#pragma HLS INTERFACE s_axilite port=erase_delta bundle=control
#pragma HLS INTERFACE s_axilite port=color_margin bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control
    if(width<16 || width>MAX_W || width%16 || !height || height>1080 ||
       dst_stride<2*width || dst_stride>6144 || dst_stride%4 || order>3 || control>1 ||
       !ink_delta || ink_delta>128 || !erase_delta || erase_delta>=ink_delta ||
       !color_margin || color_margin>128) return 1;
    if(!frame_cookie || frame_cookie!=metadata_cookie) return 2;
    // Host range checks are mandatory; native exact-alias checks are a second
    // tripwire and are not part of the synthesized memory datapath.
#ifdef WHITEBOARD_NATIVE
    if(canvas_in==canvas_out || reinterpret_cast<const void*>(dst)==src ||
       reinterpret_cast<const void*>(dst)==canvas_in || dst==canvas_out) return 3;
#endif

    // HOLD reuses burst canvas/scanout IO and never reads A or metadata.
    render(src,canvas_in,canvas_out,metadata,dst,width,height,dst_stride,control,order,ink_delta,erase_delta,color_margin);
    return 0;
}
