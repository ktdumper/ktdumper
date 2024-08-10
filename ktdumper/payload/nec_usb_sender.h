#pragma once

#define USB_SEND(addr, sz) { \
    uint8_t *_data = (void*)KT_usb_data; \
    uint8_t *_datasz = (void*)KT_usb_datasz; \
    void (*respfunc)() = (void*)KT_usb_respfunc; \
\
    uint8_t *_inbuf = (void*)addr; \
\
    for (size_t i = 0; i < sz; ++i) \
        _data[i] = _inbuf[i]; \
\
    uint32_t _sz = sz + 5; \
    _datasz[0] = _sz; \
    _datasz[1] = _sz >> 8; \
\
    respfunc(0xd, 0x0); \
}
