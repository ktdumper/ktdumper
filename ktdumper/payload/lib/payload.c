#include <inttypes.h>

#include "lib/onenand.c"

/* these are the two APIs that the main payload driver has to implement */
void receive_msg(void);
void send_msg(const void *addr, size_t len);

uint8_t payload[0x100], resp[0x4000];

#define XADDR(_arr, _off) ((_arr[_off]) | (_arr[_off+1] << 8) | (_arr[_off+2] << 16) | (_arr[_off+3] << 24))

void payload_main_loop(void) {
    static uint16_t onenand_buf[(4096+128)/2];

    while (1) {
        receive_msg();

        uint8_t ch = payload[0];
        if (ch == 0x42) {
            /* handshake */
            uint32_t magic = 0x52535455;
            send_msg(&magic, sizeof(magic));
        } else if (ch == 0x10 || ch == 0x11 || ch == 0x12) {
            /* read */
            uint32_t addr = XADDR(payload, 1);
            uint32_t resp, resplen;

            switch (ch) {
            case 0x10:
                resp = *(volatile uint8_t*)addr;
                resplen = 1;
                break;
            case 0x11:
                resp = *(volatile uint16_t*)addr;
                resplen = 2;
                break;
            case 0x12:
                resp = *(volatile uint32_t*)addr;
                resplen = 4;
                break;
            }

            send_msg(&resp, resplen);
        } else if (ch == 0x20 || ch == 0x21 || ch == 0x22) {
            /* write */
            uint32_t addr = XADDR(payload, 1);

            int wlen = 1 << (ch & 0xF);
            uint8_t datab[4] = { 0 };
            for (int i = 0; i < wlen; ++i)
                datab[i] = payload[5 + i];
            uint32_t data = datab[0] | (datab[1] << 8) | (datab[2] << 16) | (datab[3] << 24);

            switch (wlen) {
            case 1:
                *(volatile uint8_t*)addr = data;
                break;
            case 2:
                *(volatile uint16_t*)addr = data;
                break;
            case 4:
                *(volatile uint32_t*)addr = data;
                break;
            }
        } else if (ch == 0x60) {
            /* read 64 bytes */
            uint32_t addr = XADDR(payload, 1);
            send_msg((void*)addr, 64);
        } else if (ch == 0x70) {
            /* read onenand 4096b page + 128b oob */
            uint32_t block = XADDR(payload, 1);
            uint32_t page = XADDR(payload, 5);

            onenand_read_4k(block, page, onenand_buf);
            send_msg(onenand_buf, 4096+128);
        } else if (ch == 0x71) {
            /* check if the block is likely SLC or MLC by comparing if first and second 64 pages inside are the same or different */
            uint32_t block = XADDR(payload, 1);
            uint8_t likely_slc = 1;
            uint8_t *scratchbuf = resp;
            for (size_t page = 0; page < 64; ++page) {
                onenand_read_4k(block, page, (void*)scratchbuf);
                onenand_read_4k(block, 64 + page, (void*)(scratchbuf + 4096 + 128));

                for (size_t x = 0; x < 4096+128; ++x) {
                    if (scratchbuf[x] != scratchbuf[4096+128+x]) {
                        likely_slc = 0;
                        break;
                    }
                }

                if (!likely_slc)
                    break;
            }

            send_msg(&likely_slc, 1);
        } else if (ch == 0x72) {
            /* read onenand 2048b page + 64b oob */
            uint32_t block = XADDR(payload, 1);
            uint32_t page = XADDR(payload, 5);

            onenand_read_2k(block, page, onenand_buf);
            send_msg(onenand_buf, 2048+64);
        }
    }
}
