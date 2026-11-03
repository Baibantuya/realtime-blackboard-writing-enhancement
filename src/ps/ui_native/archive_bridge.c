/* Single-owner LVGL. View commands never touch PL restoration state. */
#include "lvgl.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
extern const lv_font_t board_ui_cjk20, board_ui_cjk24;
static lv_display_t *display;
static lv_indev_t *pointer;
static lv_obj_t *bar,*opener,*page_label,*fps_label,*notice_label,*scope_label,*buttons[8];
static uint8_t *pixels,*draw;
static int initialized,collapsed,px,py,pressed,focus,replay;
static int queue[16],head,tail;
static uint32_t activity,revision;
static const char *modes[]={"原图","初步增强","深度增强"};
static const char *titles[]={"原图","初步增强","深度增强","上一版面","下一版面","记录当前版面","手动重置（初始化）","收起"};
static const int commands[]={0xF1,0xF2,0xF3,0xF4,0xF5,0xF6,0xF7,0xF9};
static void flush(lv_display_t *d,const lv_area_t *a,uint8_t *p) {
    int w=a->x2-a->x1+1;
    for(int y=a->y1;y<=a->y2;++y)
        memcpy(pixels+((size_t)y*1920+a->x1)*4,p+(size_t)(y-a->y1)*w*4,(size_t)w*4);
    revision++;lv_display_flush_ready(d);
}
static void read_pointer(lv_indev_t *d,lv_indev_data_t *v) {
    (void)d;v->point.x=px;v->point.y=py;v->state=pressed?LV_INDEV_STATE_PRESSED:LV_INDEV_STATE_RELEASED;
}
static void set_collapsed(int yes) {
    collapsed=yes;activity=lv_tick_get();
    if(yes){lv_obj_add_flag(bar,LV_OBJ_FLAG_HIDDEN);lv_obj_remove_flag(opener,LV_OBJ_FLAG_HIDDEN);}
    else {lv_obj_remove_flag(bar,LV_OBJ_FLAG_HIDDEN);lv_obj_add_flag(opener,LV_OBJ_FLAG_HIDDEN);}
}
static void enqueue(int command) {
    activity=lv_tick_get();
    if(command==0xF9){set_collapsed(!collapsed);return;}
    if(command<0xF1||command>0xF7)return;
    if((tail+1)%16!=head){queue[tail]=command;tail=(tail+1)%16;}
}
static void clicked(lv_event_t *event){enqueue((int)(intptr_t)lv_event_get_user_data(event));}
static lv_obj_t *box(lv_obj_t *parent,int x,int y,int w,int h,uint32_t color) {
    lv_obj_t *o=lv_obj_create(parent);lv_obj_remove_style_all(o);
    lv_obj_set_pos(o,x,y);lv_obj_set_size(o,w,h);lv_obj_remove_flag(o,LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_style_bg_color(o,lv_color_hex(color),0);lv_obj_set_style_bg_opa(o,255,0);lv_obj_set_style_radius(o,18,0);return o;
}
static lv_obj_t *label(lv_obj_t *parent,const char *text,const lv_font_t *font,uint32_t color) {
    lv_obj_t *o=lv_label_create(parent);lv_obj_set_style_text_font(o,font,0);
    lv_obj_set_style_text_color(o,lv_color_hex(color),0);lv_label_set_text(o,text);return o;
}
static void arrow(lv_obj_t *parent,int up) {
    static const lv_point_precise_t above[]={{0,10},{12,0},{24,10}},below[]={{0,0},{12,10},{24,0}};
    lv_obj_t *o=lv_line_create(parent);lv_line_set_points(o,up?above:below,3);
    lv_obj_set_style_line_width(o,3,0);lv_obj_set_style_line_color(o,lv_color_hex(0x263445),0);lv_obj_center(o);
}
int ps_init(void) {
    if(initialized)return 0;
    pixels=calloc((size_t)1920*320,4);draw=calloc((size_t)1920*32,4);
    if(!pixels||!draw){free(pixels);free(draw);return 0;}
    lv_init();display=lv_display_create(1920,320);lv_display_set_color_format(display,LV_COLOR_FORMAT_ARGB8888);
    lv_display_set_flush_cb(display,flush);lv_display_set_buffers(display,draw,NULL,(size_t)1920*32*4,LV_DISPLAY_RENDER_MODE_PARTIAL);
    lv_obj_t *root=lv_screen_active();lv_obj_remove_style_all(root);lv_obj_remove_flag(root,LV_OBJ_FLAG_SCROLLABLE);lv_obj_set_style_bg_opa(root,0,0);
    bar=box(root,32,142,1856,166,0xEEEAE2);
    page_label=label(bar,"实时 · 深度增强",&board_ui_cjk24,0x263445);lv_obj_set_pos(page_label,24,12);
    notice_label=label(bar,"",&board_ui_cjk20,0x805C41);lv_obj_set_pos(notice_label,500,16);
    fps_label=label(bar,"画面 0.0 FPS",&board_ui_cjk20,0x5E5967);lv_obj_align(fps_label,LV_ALIGN_TOP_RIGHT,-24,16);
    scope_label=label(bar,"",&board_ui_cjk20,0x5E5967);lv_obj_set_pos(scope_label,24,132);
    lv_obj_t *mode_group=box(bar,24,52,774,82,0xD9D4E0);
    lv_obj_t *page_group=box(bar,830,52,452,82,0xDDD9D0);
    const int widths[]={242,242,242,208,208,198,210,100};
    for(int i=0;i<8;++i){
        lv_obj_t *parent=i<3?mode_group:i<5?page_group:bar;
        int x=i<3?12+i*254:i<5?12+(i-3)*220:i==5?1296:i==6?1506:1732;
        buttons[i]=box(parent,x,i<5?6:58,widths[i],70,i==5?0x896447:i==6?0xD7C7B8:i<3?0xD9D4E0:0xEEEAE2);
        if(i==6){lv_obj_set_style_border_width(buttons[i],2,0);lv_obj_set_style_border_color(buttons[i],lv_color_hex(0xA58A73),0);lv_obj_set_style_border_opa(buttons[i],255,0);}
        lv_obj_add_flag(buttons[i],LV_OBJ_FLAG_CLICKABLE);lv_obj_add_event_cb(buttons[i],clicked,LV_EVENT_CLICKED,(void*)(intptr_t)commands[i]);
        if(i==7)arrow(buttons[i],0);
        else {
            lv_obj_t *t=label(buttons[i],titles[i],i==6?&board_ui_cjk20:&board_ui_cjk24,i==5?0xFFFFFF:0x263445);lv_obj_align(t,LV_ALIGN_TOP_MID,0,1);
            char key[8];snprintf(key,sizeof(key),"F%d",i+1);
            t=label(buttons[i],key,&board_ui_cjk20,i==5?0xEEEAE2:0x5E5967);lv_obj_align(t,LV_ALIGN_BOTTOM_MID,0,-3);
        }
    }
    opener=box(root,1804,260,84,48,0xEEEAE2);arrow(opener,1);
    lv_obj_add_flag(opener,LV_OBJ_FLAG_CLICKABLE);lv_obj_add_event_cb(opener,clicked,LV_EVENT_CLICKED,(void*)(intptr_t)0xF9);
    pointer=lv_indev_create();lv_indev_set_type(pointer,LV_INDEV_TYPE_POINTER);lv_indev_set_read_cb(pointer,read_pointer);
    initialized=1;head=tail=focus=replay=pressed=0;set_collapsed(1);return 1;
}
void ps_tick(unsigned ms){lv_tick_inc(ms);lv_timer_handler();if(!collapsed&&lv_tick_elaps(activity)>=10000)set_collapsed(1);}
void ps_key(int key){enqueue(key);}
void ps_nav(int key){
    activity=lv_tick_get();
    if(key==4)set_collapsed(0);
    else if(key==5||key==8)set_collapsed(1);
    else if(key==1||key==2||key==6||key==7){
        if(collapsed)set_collapsed(0);
        focus=(focus+((key==2||key==6)?7:1))%8;
        for(int i=0;i<8;++i){lv_obj_set_style_outline_width(buttons[i],i==focus?2:0,0);lv_obj_set_style_outline_color(buttons[i],lv_color_hex(0x263445),0);}
    }else if(key==3){if(collapsed)set_collapsed(0);else enqueue(commands[focus]);}
}
void ps_pointer(int x,int y,int down){
    if(x<0||x>=1920||y<760||y>=1080){pressed=0;lv_indev_reset(pointer,NULL);return;}
    if(x!=px||y-760!=py||down!=pressed)activity=lv_tick_get();
    px=x;py=y-760;pressed=down;lv_indev_read(pointer);
}
int ps_take(void){if(head==tail)return 0;int k=queue[head];head=(head+1)%16;return k;}
void ps_state(int mode,int page,int count,double fps,int can_record,int notice){
    char text[160];if(mode<0||mode>2)mode=2;
    if(page)snprintf(text,sizeof(text),"版面 %d / %d · %s",page,count,modes[mode]);else snprintf(text,sizeof(text),"实时 · %s",modes[mode]);
    lv_label_set_text(page_label,text);snprintf(text,sizeof(text),page?"实时处理 %.1f FPS":"画面 %.1f FPS",fps);lv_label_set_text(fps_label,text);lv_obj_align(fps_label,LV_ALIGN_TOP_RIGHT,-24,16);
    const char *messages[]={"","已记录当前版面","暂无可记录的实时画面","版面已满（32 个）","正在切换画面","请先完成板面定位"};
    lv_label_set_text(notice_label,notice>=0&&notice<6?messages[notice]:"");
    lv_label_set_text(scope_label,replay?"离线验证 · 无板卡":"F4 / F5 切换版面 · 上 / 下键展开或收起");
    for(int i=0;i<3;++i)lv_obj_set_style_bg_color(buttons[i],lv_color_hex(i==mode?0xF2EDF8:0xD9D4E0),0);
    if(can_record)lv_obj_remove_state(buttons[5],LV_STATE_DISABLED);else lv_obj_add_state(buttons[5],LV_STATE_DISABLED);
    lv_obj_set_style_bg_opa(buttons[5],can_record?255:120,0);
}
void ps_scope(int value){replay=value;}
int ps_collapsed(void){return collapsed;}
void ps_render(uint8_t *out){lv_refr_now(display);memcpy(out,pixels,(size_t)1920*320*4);}
void ps_close(void){if(!initialized)return;lv_deinit();free(pixels);free(draw);pixels=draw=NULL;initialized=0;}

unsigned ps_native_abi(void){return 0x20;}
unsigned ps_render_changed(uint8_t *out,unsigned previous){
    lv_refr_now(display);
    if(previous==revision)return 0;
    memcpy(out,pixels,(size_t)1920*320*4);return revision;
}
void ps_rates(int mode,int page,int guiding,double source,double presented){
    char text[160];const char *names[]={"CAP","RECT","ENH"};
    if(mode<0||mode>2)mode=2;
    if(page)snprintf(text,sizeof(text),"STATIC | ENH %.1f FPS",source);
    else if(guiding)snprintf(text,sizeof(text),"CAP %.1f | LOCATING",source);
    else snprintf(text,sizeof(text),"%s %.1f | DISP %.1f FPS",names[mode],source,presented);
    lv_label_set_text(fps_label,text);lv_obj_align(fps_label,LV_ALIGN_TOP_RIGHT,-24,16);
}

/* Optional extension: measured compute-only equivalent rate, separate scanout FPS. */
void ps_rectify_compute(double equivalent_fps,int available,double presented){
    char text[160];
    if(available==1 && equivalent_fps>0.0)
        snprintf(text,sizeof(text),"RECT COORD EQ %.1f | DISP %.1f FPS",equivalent_fps,presented);
    else if(available<0)
        snprintf(text,sizeof(text),"RECT COORD: NO COUNTER | DISP %.1f",presented);
    else if(available==2)
        snprintf(text,sizeof(text),"RECT COORD: STALE | DISP %.1f",presented);
    else
        snprintf(text,sizeof(text),"RECT COORD: WAIT | DISP %.1f",presented);
    lv_label_set_text(fps_label,text);lv_obj_align(fps_label,LV_ALIGN_TOP_RIGHT,-24,16);
}
