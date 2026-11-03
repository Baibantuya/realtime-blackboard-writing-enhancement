#include "local_sum_tree.h"
#include <random>
#include <cstdio>
static unsigned cases=0;
static bool check(const uint8_t w[7][7]) {
    unsigned ref=0; for(unsigned r=0;r<7;r++)for(unsigned c=0;c<7;c++)ref+=w[r][c];
    unsigned got=wb_local_sum(w); ++cases;
    if(ref!=got){std::printf("FAIL case=%u expected=%u got=%u\n",cases,ref,got);return false;}
    return true;
}
int main(){
    uint8_t w[7][7]={};
    for(unsigned value=0;value<256;value++){
        for(auto &row:w)for(auto &v:row)v=value;
        if(!check(w))return 1;
    }
    for(unsigned pos=0;pos<49;pos++)for(unsigned value=0;value<256;value++){
        for(auto &row:w)for(auto &v:row)v=0;
        w[pos/7][pos%7]=value;if(!check(w))return 1;
    }
    std::mt19937 rng(0x20261027u);
    for(unsigned n=0;n<200000;n++){
        for(auto &row:w)for(auto &v:row)v=rng()&255;
        if(!check(w))return 1;
    }
    std::printf("PASS %u windows; exact uint16 reduction, seed=0x20261027\n",cases);
}
