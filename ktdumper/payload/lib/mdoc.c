#include <inttypes.h>
#include <stdlib.h>

#define DOCH_ATA_REGS_OFFSET_8KB 0x0800

#define DOCH_ATA_ERROR 0x02
#define DOCH_ATA_NSECTOR 0x04
#define DOCH_SECTOR_NO_REG 0x06
#define DOCH_CYLINDER_LOW_REG 0x08
#define DOCH_CYLINDER_HIGH_REG 0x0A
#define DOCH_DRIVE_HEAD_REG 0x0C
#define DOCH_ATA_STATUS 0x0E
#define DOCH_ATA_FEATURE DOCH_ATA_ERROR
#define DOCH_ATA_COMMAND DOCH_ATA_STATUS

#define DOCH_VSCMD_READ_PARTITION 0x82
#define DOCH_LBA 0x40

volatile uint8_t *reg_DOCH_ATA_NSECTOR = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_NSECTOR);
volatile uint8_t *reg_DOCH_SECTOR_NO_REG = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_SECTOR_NO_REG);
volatile uint8_t *reg_DOCH_CYLINDER_LOW_REG = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_CYLINDER_LOW_REG);
volatile uint8_t *reg_DOCH_CYLINDER_HIGH_REG = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_CYLINDER_HIGH_REG);
volatile uint8_t *reg_DOCH_ATA_FEATURE = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_FEATURE);
volatile uint8_t *reg_DOCH_DRIVE_HEAD_REG = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_DRIVE_HEAD_REG);
volatile uint8_t *reg_DOCH_ATA_COMMAND = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_COMMAND);
volatile uint16_t *reg_DOCH_ATA_DATA = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB);
volatile uint8_t *reg_DOCH_ATA_STATUS = (void*)(KT_nand_data + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_STATUS);

static void mdoc_wait() {
    while (1) {
        uint8_t ret = *reg_DOCH_ATA_STATUS;
        if (ret == 0x58 || ret == 0x50)
            break;
    }
}

void mdoc_read(int part, uint32_t sector, void *dst) {
    uint16_t *dst16 = dst;

    mdoc_wait();
    *reg_DOCH_ATA_NSECTOR = 1;
    *reg_DOCH_SECTOR_NO_REG = sector & 0xFF;
    *reg_DOCH_CYLINDER_LOW_REG = (sector >> 8) & 0xFF;
    *reg_DOCH_CYLINDER_HIGH_REG = (sector >> 16) & 0xFF;
    *reg_DOCH_ATA_FEATURE = part;
    *reg_DOCH_DRIVE_HEAD_REG = ((sector >> 24) & 0x0F) | DOCH_LBA;
    *reg_DOCH_ATA_COMMAND = DOCH_VSCMD_READ_PARTITION;
    mdoc_wait();

    for (int i = 0; i < 256; ++i)
        dst16[i] = *reg_DOCH_ATA_DATA;
}
