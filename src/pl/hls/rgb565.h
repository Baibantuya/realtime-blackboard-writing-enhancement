#ifndef WB_RGB565_H
#define WB_RGB565_H
#include <stdint.h>
// Shared little-endian RGB565 contract; calculations use replicated 8-bit channels.
static inline uint32_t wb_expand565(uint16_t p) {
    unsigned r=(p>>11)&31,g=(p>>5)&63,b=p&31;
    return ((r<<3)|(r>>2)) | (((g<<2)|(g>>4))<<8) | (((b<<3)|(b>>2))<<16);
}
static inline uint16_t wb_pack565(uint32_t rgb) {
    return ((rgb&0xf8)<<8) | ((rgb>>5)&0x7e0) | ((rgb>>19)&31);
}
static inline uint16_t wb_swap565(uint16_t p) {
    return (p&0x7e0) | ((p&31)<<11) | ((p>>11)&31);
}
#endif
