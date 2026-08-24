#include <stdint.h>

#define UsbPollEvent  ((int (*)(void))0xA071089Du)
#define UsbReadBytes  ((int (*)(int, void *, int))0xA07109B7u)
#define UsbWriteBytes ((int (*)(int, const void *, int))0xA0710A4Fu)

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
