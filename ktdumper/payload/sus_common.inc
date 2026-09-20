#include <stdint.h>

#define UsbPollEvent  ((int (*)(void))KT_usb_poll)

#if KT_legacy_usb
static int UsbReadBytes(int port, void *p, int size)
{
    uint16_t count = 0;
    int status = ((int (*)(int, void *, int, uint16_t *))KT_usb_read)(port, p, size, &count);
    return status == 0 ? count : 0;
}

static int UsbWriteBytes(int port, const void *p, int size)
{
    int status;
    do {
        UsbPollEvent();
        status = ((int (*)(int, const void *, int))KT_usb_write)(port, p, size);
    } while (status == 3);
    if (status != 0)
        while (1) {}
    while (UsbPollEvent() != 13) {}
    return size;
}
#else
#define UsbReadBytes  ((int (*)(int, void *, int))KT_usb_read)
#define UsbWriteBytes ((int (*)(int, const void *, int))KT_usb_write)
#endif

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
