#include <inttypes.h>

#include "g1_ap.h"

#define AP_STS (*(volatile uint32_t*)0xe6c21ffc)
#define AP_CMD (*(volatile uint32_t*)0xe6c21ff8)
#define AP_ARG (*(volatile uint32_t*)0xe6c21ff0)
#define AP_ARGS ((volatile uint32_t*)0xe6c21ff0)

#define NAND_BASE (0x08000000)
#define off_NAND_DATA 0x0
#define off_NAND_ADDR 0x1000000
#define off_NAND_CMD 0x2000000

volatile uint16_t *NAND_DATA = (void*)(NAND_BASE + off_NAND_DATA);
volatile uint8_t *NAND_ADDR = (void*)(NAND_BASE + off_NAND_ADDR);
volatile uint8_t *NAND_CMD = (void*)(NAND_BASE + off_NAND_CMD);

int nand_wait() {
	while (1) {
		uint16_t data;
		*NAND_CMD = 0x70;
		data = *NAND_DATA;
		if (data & 0x40) {
			return data;
		}
	}
}

int nand_read_lp(uint32_t page, void *dst) {
	uint8_t *cdst = dst;

    *NAND_CMD = 0x00;

    *NAND_ADDR = 0x00;
    *NAND_ADDR = 0x00;
    *NAND_ADDR = page & 0xFF;
    *NAND_ADDR = (page >> 8) & 0xFF;
    *NAND_ADDR = (page >> 16) & 0xFF;

    *NAND_CMD = 0x30;

    int ret = nand_wait();

    *NAND_CMD = 0x00;

    for (int i = 0; i < 0x420; ++i) {
		uint16_t data = *NAND_DATA;
		cdst[2 * i] = data & 0xFF;
		cdst[2 * i + 1] = data >> 8;
	}

    return ret;
}

void fatal(void) {
    while (1) {}
}

int main() {
    AP_CMD = 0;
    AP_STS = 0xBBBAAA;

    volatile uint8_t *dstbuf = (void*)0xe6c21000;

    while (1) {
        uint32_t cmd = AP_CMD;
        if (!cmd)
            continue;
        AP_CMD = 0;

        switch (cmd) {
        case CMD_AP_READ8: {
            volatile uint8_t *ptr = (void*)AP_ARG;
            AP_ARG = *ptr;
            break;
        }
        case CMD_AP_READ16: {
            volatile uint16_t *ptr = (void*)AP_ARG;
            AP_ARG = *ptr;
            break;
        }
        case CMD_AP_READ32: {
            volatile uint32_t *ptr = (void*)AP_ARG;
            AP_ARG = *ptr;
            break;
        }

        case CMD_AP_WRITE8: {
            volatile uint8_t *ptr = (void*)AP_ARGS[0];
            uint8_t data = AP_ARGS[1];
            *ptr = data;
            break;
        }
        case CMD_AP_WRITE16: {
            volatile uint16_t *ptr = (void*)AP_ARGS[0];
            uint16_t data = AP_ARGS[1];
            *ptr = data;
            break;
        }
        case CMD_AP_WRITE32: {
            volatile uint32_t *ptr = (void*)AP_ARGS[0];
            uint32_t data = AP_ARGS[1];
            *ptr = data;
            break;
        }

        case CMD_AP_READ: {
            volatile uint8_t *ptr = (void*)AP_ARG;
            for (int i = 0; i < 64; ++i)
                dstbuf[i] = ptr[i];
            break;
        }

        default:
            fatal();
        }

        AP_STS = 1;
    }
}

__asm__(
".section .text.start\n"
".global start\n"
"start:\n"
"b Reset\n"
"b UndefinedInstruction\n"
"b SoftwareInterrupt\n"
"b PrefetchAbort\n"
"b DataAbort\n"

"UndefinedInstruction:\n"
"SoftwareInterrupt:\n"
"PrefetchAbort:\n"
"DataAbort:\n"
"infloop: b infloop\n"

"Reset:\n"
"    ldr r0, =0xE6C21000\n"
"    mov sp, r0\n"
"    b main\n"
);
