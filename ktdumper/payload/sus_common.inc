#include <stdint.h>

#define UsbPollEvent  ((int (*)(void))KT_usb_poll)
#define UsbReadBytes  ((int (*)(int, void *, int))KT_usb_read)
#define UsbWriteBytes ((int (*)(int, const void *, int))KT_usb_write)

static void send(uint8_t b)
{
    UsbWriteBytes(0, &b, 1);
}

static void usb_send(const uint8_t *p, uint32_t sz)
{
    UsbWriteBytes(0, p, sz);
}

static uint8_t recv(void)
{
    uint8_t b;
    do {
        UsbPollEvent();
    } while (UsbReadBytes(0, &b, 1) != 1);
    return b;
}
