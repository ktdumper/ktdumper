#include <inttypes.h>
#include <stddef.h>

int (*reboot)() = (void*)0xe0601938;

void main(void) {
    /* reset a specific bit set by the jumper */
    *(volatile uint16_t*)0x39060412 |= 8;

    /* restart in a mode where AP isn't started by BB */
    *(volatile uint32_t*)0x7ffc = 0x72646c46;
    reboot();

    while (1) {}
}

__asm__(
".section .text.start\n"
".global start\n"
"start:\n"
    // clean data cache and flush icache before jumping to rest of payload
    // hopefully increase stability bc we only need 1-2 cache lines to hit
"    ldr r0, =%base%\n"
"    ldr r1, =%base%+0x10000\n"
"loop:\n"
"    mcr p15, 0, r0, c7, c10, 1\n"
"    add r0, r0, #32\n"
"    cmp r0, r1\n"
"    bne loop\n"
"    mov r0, #0\n"
"    mcr p15, 0, r0, c7, c5, 0\n"

"    b main\n"
);
