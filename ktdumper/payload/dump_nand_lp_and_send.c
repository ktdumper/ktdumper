#include <inttypes.h>
#include <stddef.h>

void start() {
    uint8_t *command = (void*)%usb_command%;
    uint8_t *data = (void*)%usb_data%; // comes from cmd_read
    uint8_t *datasz = (void*)%usb_datasz%; // also from cmd_read
    void (*respfunc)() = (void*)%usb_respfunc%;
    uint16_t *scratchbuf16 = (void*)(%base%+0x1000);

    volatile uint16_t *nand_cmd = (void*)%nand_cmd%;
    volatile uint16_t *nand_data = (void*)%nand_data%;
    volatile uint16_t *nand_addr = (void*)%nand_addr%;

    uint8_t subcmd = command[10];
    if (subcmd == 0) {
        /* subcommand: read NAND page */
        uint32_t page = (command[11] << 0) | (command[12] << 8) | (command[13] << 16) | (command[14] << 24);

        /* READ0 */
        *nand_cmd = 0x00;

        *nand_addr = 0x00;
        *nand_addr = 0x00;
        *nand_addr = page & 0xFF;
        *nand_addr = (page >> 8) & 0xFF;
        *nand_addr = (page >> 16) & 0xFF;

        /* READSTART */
        *nand_cmd = 0x30;

        for (volatile int i = 0; i < 0x100; ++i) {}

        for (int i = 0; i < 0x420; ++i)
            scratchbuf16[i] = *nand_data;
    } else {
        /* subcommand: transfer data */
        uint32_t addr = (command[11] << 0) | (command[12] << 8) | (command[13] << 16) | (command[14] << 24);
        uint16_t sz = (command[15] << 0) | (command[16] << 8);

        uint8_t *inbuf = (void*)addr;

        for (size_t i = 0; i < sz; ++i)
            data[i] = inbuf[i];

        sz += 5;
        datasz[0] = sz;
        datasz[1] = sz >> 8;

        respfunc(0xd, 0x0);
    }
}
