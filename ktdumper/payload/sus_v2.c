#include "sus_common.inc"

#include "lib/payload.c"

#define KT_chunk 48

#include "ext/chunked_protocol.inc"

__attribute__((section(".text.start"), used))
void start(void)
{
    UsbPollEvent();

    send(0x50);
    if (recv() != 0x51)
        while (1) {}

    payload_main_loop();
}
