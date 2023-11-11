#include <inttypes.h>
#include <stddef.h>

void start() {
    uint8_t *command = (void*)0x33ee5198;
    uint8_t *data = (void*)0x33ef51e2; // comes from cmd_read
    uint8_t *datasz = (void*)0x33ef51dc; // also from cmd_read
    void (*respfunc)() = (void*)0x519c;

    uint32_t addr = (command[10] << 0) | (command[11] << 8) | (command[12] << 16) | (command[13] << 24);
    uint16_t sz = (command[14] << 0) | (command[15] << 8);

    uint8_t *inbuf = (void*)addr;

    for (size_t i = 0; i < sz; ++i)
        data[i] = inbuf[i];

    sz += 5;
    datasz[0] = sz;
    datasz[1] = sz >> 8;

    respfunc(0xd, 0x0);
}
