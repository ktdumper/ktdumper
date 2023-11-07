#define BASE %base%
#define NAND_PHYS %nand%

void start() {
    unsigned char *command = (void*)(BASE + 0x400);
    unsigned *data = (void*)(BASE + 0x800);
    unsigned short *data16 = (void*)(BASE + 0x800);

    volatile unsigned *EMIFS_CONFIG_REG = (void*)0xFFFECC0C;
    volatile unsigned char *NAND = (void*)NAND_PHYS;
    volatile unsigned char *NAND_CMD = NAND+0x800;
    volatile unsigned char *NAND_ADDR = NAND+0x400;
    volatile unsigned char *NAND_DATA = NAND;

    unsigned page = (command[0] << 0) | (command[1] << 8) | (command[2] << 16) | (command[3] << 24);
    unsigned half = command[4];

    unsigned prev = *EMIFS_CONFIG_REG;
    *EMIFS_CONFIG_REG = prev|1;

    /* READ0 */
    *NAND_CMD = (half == 2 ? 0x50 : 0x00);

    /* column */
    *NAND_ADDR = (half == 1 ? 128 : 0);

    /* page */
    *NAND_ADDR = page & 0xFF;
    *NAND_ADDR = (page >> 8) & 0xFF;
    *NAND_ADDR = (page >> 16) & 0xFF;

    *EMIFS_CONFIG_REG = prev;

    for (volatile int x = 0; x < 100; ++x)
    {}

    int read_amount = (half == 2 ? 16 : 256);
    for (int i = 0; i < read_amount/2; ++i) {
        unsigned short read = *(volatile unsigned short*)NAND_DATA;
        data16[i] = read;
    }
}
