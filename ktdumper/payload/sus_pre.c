#include "sus_common.inc"

static uint32_t recv32(void)
{
    uint32_t v = 0;
    for (uint32_t i = 0; i < 4; i++)
        v |= (uint32_t)recv() << (i * 8);
    return v;
}

__attribute__((section(".text.start"), used))
void start(void)
{
    UsbPollEvent();

    send(0x42);
    if (recv() != 0x43)
        while (1) {}

    uint32_t size = recv32();
    send(0x44);
    for (uint32_t i = 0; i < size; ++i) {
        *(uint8_t *)(KT_target_addr + i) = recv();
        send(0x45);
    }

    void (*jump)(void) = (void *)(KT_target_addr | 1);
    jump();
}
