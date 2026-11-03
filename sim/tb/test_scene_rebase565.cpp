#include "whiteboard_restore.h"
#include "rgb565.h"
#include "scene_rebase.h"
#include <vector>
#include <cstdio>
int main(){
 const int w=64,h=32,words=w*h/2,groups=w*h/4,count=w/16*((h+15)/16);
 std::vector<uint32_t> in(WB_FRAME_WORDS),out(WB_FRAME_WORDS),bg(WB_FRAME_WORDS),prev(WB_FRAME_WORDS),quiet(WB_QUIET_WORDS),state(WB_MAX_BLOCKS+5,0xdeadbeef);
 std::vector<uint8_t> roi(WB_MAX_BLOCKS,1);
 const uint16_t board=wb_pack565(25|(80<<8)|(35<<16)),person=wb_pack565(160|(30<<8)|(30<<16));
 const unsigned ctl=2|4|(3<<8)|(4<<16);
 auto run=[&](unsigned flags){return whiteboard_restore(in.data(),out.data(),bg.data(),prev.data(),quiet.data(),state.data(),roi.data(),w,h,flags,0,24,16,5,2,6,3,2,100,55,100,55,6);};
 auto fill=[&](uint16_t value){for(int i=0;i<words;i++)in[i]=value|(uint32_t(value)<<16);};
 auto box=[&](uint16_t value){for(int y=0;y<16;y++)for(int x=16;x<32;x++){int a=(y*w+x)/2,s=(x&1)*16;in[a]=(in[a]&~(0xffffu<<s))|(uint32_t(value)<<s);}};
 auto epoch=[&](){return state[count+2];};
 #define CHECK(x) do{if(!(x)){printf("SCENE_FAIL line=%d epoch=%u reasons=%x\n",__LINE__,epoch(),state[count+3]);return 1;}}while(0)
 fill(board);CHECK(run(ctl|1)==0);CHECK(epoch()==0);
 for(int f=0;f<12;f++)CHECK(run(ctl)==0);CHECK(epoch()==0); // one-shot, no needless periodic resets
 box(person);for(int f=0;f<16;f++){CHECK(run(ctl)==0);CHECK(epoch()==0);} // stationary person
 fill(board);for(int f=0;f<24;f++)CHECK(run(ctl)==0);CHECK(epoch()==1);
 for(int i=0;i<count;i++)CHECK(state[i]==(3u<<16));
 for(int f=0;f<12;f++)CHECK(run(ctl)==0);CHECK(epoch()==1);
 box(0xffff);for(int f=0;f<16;f++){CHECK(run(ctl)==0);CHECK(epoch()==1);} // large white shirt
 fill(board);for(int f=0;f<16;f++)CHECK(run(ctl&~4u)==0);CHECK(epoch()==1); // untrusted photometry/geometry
 // Write a thin line before rebase. It must be copied into the new reference.
 for(int x=4;x<60;x++){int i=(20*w+x)/2,s=(x&1)*16;in[i]=(in[i]&~(0xffffu<<s))|(0xffffu<<s);}
 for(int f=0;f<24;f++)CHECK(run(ctl)==0);CHECK(epoch()==2);
 CHECK(((bg[(20*w+20)/2])&65535)==65535);
 CHECK(bg==in&&prev==in&&out==in);
 CHECK(state[count+4]==0xdeadbeef); // ABI tail guard
 // No uninitialized v15 metadata may enable the new feature.
 state[count]=0;CHECK(run(ctl)==4);
 CHECK(run(8)==1); // reserved flag rejection, no memory writes
 printf("SCENE_REBASE565 PASS static_person white_shirt trusted_frames one_shot epochs=2 tail_guard\n");
}
