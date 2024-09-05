#include <inttypes.h>


volatile uint16_t *NAND_DATA = (void*)KT_nand_data;
volatile uint8_t *NAND_ADDR = (void*)KT_nand_addr;
volatile uint8_t *NAND_CMD = (void*)KT_nand_cmd;

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

int mlba_nand_read_mda(uint32_t page, void *dst) {
	uint8_t *cdst = dst;

	*NAND_CMD = 0x0A;
	*NAND_ADDR = 0x01; // num blocks lo
	*NAND_ADDR = 0x00; // num blocks hi
	*NAND_ADDR = page & 0xFF;
	*NAND_ADDR = (page >> 8) & 0xFF;
	*NAND_ADDR = (page >> 16) & 0xFF;
	*NAND_CMD = 0x30;

	int ret = nand_wait();

	*NAND_CMD = 0x00;

	for (int i = 0; i < 256 + 8; ++i) { // +16 bytes or 8 words for spare
		uint16_t data = *NAND_DATA;
		cdst[2 * i] = data & 0xFF;
		cdst[2 * i + 1] = data >> 8;
	}

    return ret;
}

int mlba_nand_read_sda(uint32_t page, void *dst) {
	uint8_t *cdst = dst;

	*NAND_CMD = 0x00;
	*NAND_ADDR = 0x01; // num blocks lo
	*NAND_ADDR = 0x00; // num blocks hi
	*NAND_ADDR = page & 0xFF;
	*NAND_ADDR = (page >> 8) & 0xFF;
	*NAND_ADDR = (page >> 16) & 0xFF;
	*NAND_CMD = 0x30;

	int ret = nand_wait();

	*NAND_CMD = 0x00;

	for (int i = 0; i < 256 + 8; ++i) { // +16 bytes or 8 words for spare
		uint16_t data = *NAND_DATA;
		cdst[2 * i] = data & 0xFF;
		cdst[2 * i + 1] = data >> 8;
	}

    return ret;
}
