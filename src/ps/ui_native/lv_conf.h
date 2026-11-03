#ifndef LV_CONF_H
#define LV_CONF_H
#define LV_COLOR_FORMAT_DEFAULT LV_COLOR_FORMAT_ARGB8888
#define LV_USE_OS LV_OS_NONE
#define LV_USE_LOG 0
/* Immediate state colors avoid low-contrast intermediate disabled frames. */
#define LV_THEME_DEFAULT_TRANSITION_TIME 0
#define LV_USE_ASSERT_NULL 1
#define LV_USE_ASSERT_MALLOC 1
#define LV_USE_ASSERT_STYLE 1
#define LV_USE_ASSERT_OBJ 1
#define LV_USE_ASSERT_HANDLER 1
#if defined(__linux__) || defined(_WIN32)
/* Desktop redraws and modal state changes exceed LVGL's 64 KiB default. */
#define LV_MEM_SIZE (512 * 1024)
/* A failed desktop assertion must report its source and exit, never spin forever. */
#define LV_ASSERT_USE_CUSTOM_INCLUDE 1
#define LV_ASSERT_CUSTOM_INCLUDE "linux_assert.h"
#endif
#define LV_FONT_MONTSERRAT_14 1
#define LV_FONT_DEFAULT &lv_font_montserrat_14
#define LV_USE_SPINBOX 1
#define LV_USE_DROPDOWN 1
#endif
