#include <inttypes.h>
#include <stdlib.h>

typedef struct {
    volatile uint16_t bootm[1024/2];
    volatile uint16_t datam[4096/2];
    uint8_t _main[59 * 1024];
    volatile uint16_t boots[32/2];
    volatile uint16_t datas[128/2];
    uint8_t _spare[8032];
    uint8_t _rsvd1[24 * 1024];
    uint8_t _rsvd2[8 * 1024];
    uint8_t _rsvd3[16 * 1024];

    /* registers */
    volatile uint16_t manufacturer_id;
    volatile uint16_t device_id;
    volatile uint16_t version_id;
    volatile uint16_t data_buffer_size;
    volatile uint16_t boot_buffer_size;
    volatile uint16_t amount_of_buffers;
    volatile uint16_t technology;
    uint16_t _rsvd4[249];
    volatile uint16_t start_address_1;
    volatile uint16_t start_address_2;
    uint16_t _rsvd5[5];
    volatile uint16_t start_address_8;
    uint16_t _rsvd6[248];
    volatile uint16_t start_buffer;
    uint16_t _rsvd7[31];
    volatile uint16_t command;
    volatile uint16_t system_configuration_1;
    uint16_t _rsvd8[14];
    uint16_t _rsvd9[16];
    volatile uint16_t controller_status;
    volatile uint16_t interrupt;
    uint16_t _rsvd10[10];
    volatile uint16_t start_block_address;
    uint16_t _rsvd11;
    volatile uint16_t write_protection_status;
    uint16_t _rsvd12[3249];
    volatile uint16_t ecc_status_register_1;
    volatile uint16_t ecc_status_register_2;
    volatile uint16_t ecc_status_register_3;
    volatile uint16_t ecc_status_register_4;
} onenand_t;

onenand_t *onenand = (void*)KT_onenand_addr;

#define WITH_DDP(x, ddp) ((ddp) ? ((1 << 15) | x) : (x))

static void _onenand_cmd(int ddp, uint32_t block, uint32_t page, uint32_t cmd) {
    onenand->start_address_1 = WITH_DDP(block, ddp);
    onenand->start_address_2 = WITH_DDP(0, ddp);
    onenand->start_address_8 = page << 2;

    onenand->start_buffer = (1 << 3) << 8;

    onenand->interrupt = 0;
    onenand->command = cmd;

    while ((onenand->interrupt & 0x80) != 0x80)
    {}
}

static void _onenand_readout(uint32_t read_off, uint32_t read_sz, uint16_t *data16) {
    for (size_t i = 0; i < read_sz/2; ++i)
        data16[i] = ((uint16_t*)onenand + read_off/2)[i];
}

static void onenand_read_4k(int ddp, uint32_t block, uint32_t page, uint16_t *data16) {
    _onenand_cmd(ddp, block, page, 0x00); // READ
    _onenand_readout(0x400, 4096, data16);
    _onenand_readout(0x10020, 128, data16 + 4096/2);
}

static void onenand_read_2k(int ddp, uint32_t block, uint32_t page, uint16_t *data16) {
    _onenand_cmd(ddp, block, page, 0x00); // READ
    _onenand_readout(0x400, 2048, data16);
    _onenand_cmd(ddp, block, page, 0x13); // READ SPARE
    _onenand_readout(0x10020, 64, data16 + 2048/2);
}
