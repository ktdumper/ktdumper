#include <inttypes.h>

#define PAGE_SIZE 512
#define PAGES_PER_CMD 32

void start() {
    uint8_t *command = (void*)%usb_command%;
    uint8_t *data = (void*)%usb_data%; // comes from cmd_read
    uint8_t *datasz = (void*)%usb_datasz%; // also from cmd_read
    uint8_t *tmpbuf = (void*)(%base%+0x800);
    void (*respfunc)() = (void*)%usb_respfunc%;

    int (*emmc_read_and_dcache)() = (void*)(%emmc_read_and_dcache%);

    uint32_t page = (command[10] << 0) | (command[11] << 8) | (command[12] << 16) | (command[13] << 24);
    if (emmc_read_and_dcache(0, page, PAGES_PER_CMD, tmpbuf) != 0)
        __builtin_trap();
    for (unsigned i = 0; i < PAGE_SIZE*PAGES_PER_CMD; ++i)
        data[i] = tmpbuf[i];

    uint32_t sz = PAGE_SIZE*PAGES_PER_CMD + 5;
    datasz[0] = sz;
    datasz[1] = sz >> 8;

    respfunc(0xd, 0x0);
}
