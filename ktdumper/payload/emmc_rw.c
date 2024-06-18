#include <inttypes.h>

#define PAGE_SIZE 512

void start() {
    uint8_t *command = (void*)%usb_command%;
    uint8_t *data = (void*)%usb_data%;
    uint8_t *datasz = (void*)%usb_datasz%;
    uint8_t *tmpbuf = (void*)(%base%+0x800);
    void (*respfunc)() = (void*)%usb_respfunc%;

    int (*emmc_read_and_dcache)() = (void*)(%emmc_read_and_dcache%);
    int (*emmc_inv_dcache_and_write)() = (void*)(%emmc_inv_dcache_and_write%);

    uint8_t direction = command[10]; /* 0=read, 1=write */
    uint32_t page = (command[11] << 0) | (command[12] << 8) | (command[13] << 16) | (command[14] << 24);

    uint32_t sz = 5;

    if (direction == 0) {
        if (emmc_read_and_dcache(0, page, 1, tmpbuf) != 0)
            __builtin_trap();
        for (unsigned i = 0; i < PAGE_SIZE; ++i)
            data[i] = tmpbuf[i];

        sz += PAGE_SIZE;
    } else if (direction == 1) {
        for (int i = 0; i < PAGE_SIZE; ++i)
            tmpbuf[i] = command[15 + i];

        uint32_t bufaddr =  ((uint32_t)tmpbuf) & ~31;
        for (uint32_t addr = bufaddr; addr < bufaddr + 0x1000; addr += 32) {
            __asm__ volatile ("mcr p15, 0, %0, c7, c11, 1" :: "r"(addr));
        }

        if (emmc_inv_dcache_and_write(0, page, 1, tmpbuf) != 0)
            __builtin_trap();
    }

    datasz[0] = sz;
    datasz[1] = sz >> 8;

    respfunc(0xd, 0x0);
}
