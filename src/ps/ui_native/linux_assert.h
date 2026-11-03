#ifndef BOARD_LINUX_ASSERT_H
#define BOARD_LINUX_ASSERT_H
#include <stdio.h>
#include <stdlib.h>
#define LV_ASSERT_HANDLER do { \
    fprintf(stderr,"LVGL assertion failed at %s:%d\n",__FILE__,__LINE__); \
    abort(); \
} while(0);
#endif
