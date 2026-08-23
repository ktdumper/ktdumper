#include "infineon_common.inc"

static uint32_t recv32(void)
{
    uint32_t v = 0, i;
    for (i = 0; i < 4; i++)
        v |= (uint32_t)recv() << (i * 8);
    return v;
}

__attribute__((section(".text.start"))) void start(void)
{
    uint8_t rxbuf[0x818] __attribute__((aligned(4)));

    CancelTimer(TIMER_PTR);

    rx_frame = rxbuf;
    RX_ARM();

    send(0x42);
    uint8_t handshake = recv();
    if (handshake != 0x43)
        while(1) {}

    uint32_t size = recv32();
    send(0x44);
    for (uint32_t i = 0; i < size; ++i) {
        uint8_t b = recv();
        *(uint8_t*)(KT_target_addr + i) = b;
        send(0x45);
    }

    void (*jump)() = (void*)KT_target_addr;
    jump();
}
