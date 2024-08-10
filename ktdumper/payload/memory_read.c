#include <inttypes.h>
#include <stddef.h>

#include "nec_usb_sender.h"

void start() {
#if %patch%
    #include "nec_smc_patcher.inc"
#endif

    uint8_t *command = (void*)%usb_command%;

    uint32_t addr = (command[10] << 0) | (command[11] << 8) | (command[12] << 16) | (command[13] << 24);
    uint16_t sz = (command[14] << 0) | (command[15] << 8);

    USB_SEND(addr, sz);
}
