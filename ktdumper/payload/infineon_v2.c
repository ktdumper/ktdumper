#include "infineon_common.inc"

#include "lib/payload.c"
#include "ext/chunked_protocol.inc"

__attribute__((section(".text.start"))) void start(void)
{
    uint8_t rxbuf[0x818] __attribute__((aligned(4)));

    rx_frame = rxbuf;
    RX_ARM();

    send(0x50);
    uint8_t handshake = recv();
    if (handshake != 0x51)
        while(1) {}

    payload_main_loop();
}
