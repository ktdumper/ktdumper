#include <inttypes.h>
#include <stddef.h>

#define ONENAND (%onenand_addr%)

void start() {
    uint8_t *command = (void*)%usb_command%;
    uint8_t *data = (void*)%usb_data%; // comes from cmd_read
    uint16_t *data16 = (void*)%usb_data%;
    uint8_t *datasz = (void*)%usb_datasz%; // also from cmd_read
    void (*respfunc)() = (void*)%usb_respfunc%;

    volatile uint16_t *onenand_REG_START_ADDRESS1 = (volatile uint16_t *)(ONENAND + 2*0xF100);
    volatile uint16_t *onenand_REG_START_ADDRESS2 = (volatile uint16_t *)(ONENAND + 2*0xF101);
    volatile uint16_t *onenand_REG_START_ADDRESS8 = (volatile uint16_t *)(ONENAND + 2*0xF107);
    volatile uint16_t *onenand_REG_START_BUFFER = (volatile uint16_t *)(ONENAND + 2*0xF200);
    volatile uint16_t *onenand_REG_INTERRUPT = (volatile uint16_t *)(ONENAND + 2*0xF241);
    volatile uint16_t *onenand_REG_COMMAND = (volatile uint16_t *)(ONENAND + 2*0xF220);
    volatile uint16_t *onenand_DATARAM = (volatile uint16_t *)(ONENAND + 2*0x200);
    volatile uint16_t *onenand_SPARERAM = (volatile uint16_t *)(ONENAND + 2*0x8010);

    /* assume 4k page size, 128b oob size, 64 pages per block */

    uint8_t subcmd = command[10];
    if (subcmd == 0) {
        /* subcommand: read OneNAND page and send first 0x100 piece */
        uint32_t page = (command[11] << 0) | (command[12] << 8) | (command[13] << 16) | (command[14] << 24);

        *onenand_REG_START_ADDRESS1 = (page >> 6);
        *onenand_REG_START_ADDRESS2 = 0;
        *onenand_REG_START_ADDRESS8 = (page & 0x3F) << 2;

        *onenand_REG_START_BUFFER = (1 << 3) << 8;

        *onenand_REG_INTERRUPT = 0;
        *onenand_REG_COMMAND = 0; // READ

        while ((*onenand_REG_INTERRUPT & 0x80) != 0x80)
        {}

        /* now transfer the first 256 bytes back to the client */
        for (size_t i = 0; i < 4096/2; ++i)
            data16[i] = onenand_DATARAM[i];
        for (size_t i = 0; i < 128/2; ++i)
            data16[4096/2+i] = onenand_SPARERAM[i];

        uint16_t sz = 4096 + 128 + 5;
        datasz[0] = sz;
        datasz[1] = sz >> 8;

        respfunc(0xd, 0x0);
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
