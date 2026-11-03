#include "ray_tally.h"
#include <cstdio>
#include <cstring>

// Oracle retains the original nested conditional accumulator, not the new tree.
static void reference(const uint8_t labels[6], uint8_t count[8],
                      uint8_t &positive, uint8_t &negative, uint8_t &total) {
    for(unsigned side=0;side<2;++side) {
        bool connected=true;
        for(unsigned k=0;k<3;++k) {
            unsigned label=labels[side*3+k];
            connected=connected && label!=0;
            if(connected && label<=7) {
                ++total;
                for(unsigned c=1;c<=7;++c) if(label==c) ++count[c];
                if(side) positive|=1u<<label;
                else negative|=1u<<label;
            }
        }
    }
}
static bool check(const uint8_t labels[6]) {
    uint8_t a[8]={},b[8]={};
    uint8_t ap=0,an=0,at=0,bp=0,bn=0,bt=0;
    reference(labels,a,ap,an,at);
    wb_scene_detail::ray_tally(labels,b,bp,bn,bt);
    if(std::memcmp(a,b,sizeof(a)) || ap!=bp || an!=bn || at!=bt) {
        std::printf("FAIL labels=%u,%u,%u,%u,%u,%u\n",labels[0],labels[1],labels[2],labels[3],labels[4],labels[5]);
        return false;
    }
    return true;
}
int main() {
    // Labels 0..7 plus 8 representing invalid nonzero labels; six positions.
    for(unsigned code=0;code<531441;++code) {
        unsigned n=code;
        uint8_t labels[6];
        for(unsigned j=0;j<6;++j) {labels[j]=uint8_t(n%9);n/=9;}
        if(!check(labels)) return 1;
    }
    uint32_t state=0x20261027;
    for(unsigned trial=0;trial<100000;++trial) {
        uint8_t labels[6];
        for(unsigned j=0;j<6;++j) {
            state^=state<<13;state^=state>>17;state^=state<<5;
            labels[j]=(trial&1)?uint8_t(state):uint8_t(state%10);
        }
        if(!check(labels)) return 1;
    }
    std::puts("PASS: 531441 exhaustive label-class cases + 100000 seeded byte-label cases");
    return 0;
}
