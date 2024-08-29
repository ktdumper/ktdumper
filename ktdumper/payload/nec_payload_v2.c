#include <inttypes.h>
#include <stddef.h>

int (*payload_receiver)() = (void*)KT_usb_receive;
int (*respfunc_send_ep)() = (void*)KT_usb_send;

uint32_t payload_sz_pre, payload_sz, resp_sz;
uint8_t payload_pre[0x100], payload[0x100], resp[0x4000];

static void unmask_payload(void) {
    payload_sz = 0;
    for (int i = 0; i < sizeof(payload); ++i)
        payload[i] = 0;

    for (int idx = 0; idx < payload_sz_pre; ++idx) {
        if (payload_pre[idx] == 0xFF || payload_pre[idx] == 0xFE) {
            continue;
        } else if (payload_pre[idx] == 0xFD) {
            payload[payload_sz++] = payload_pre[++idx] ^ 0x10;
        } else {
            payload[payload_sz++] = payload_pre[idx];
        }
    }

    uint8_t ck = 0;
    for (size_t i = 0; i < payload_sz; ++i)
        ck += payload[i];

    if (ck != 0 || payload_sz == 0) {
        while (1)
        {}
    }
}

static void receive_msg(void) {
    payload_sz_pre = 0;
    payload_receiver(&payload_sz_pre, payload_pre);
    unmask_payload();
}

static void mask_payload(const void *addr, size_t len) {
    const uint8_t *caddr = addr;

    for (size_t i = 0; i < len; ++i) {
        if (caddr[i] == 0xFD || caddr[i] == 0xFE || caddr[i] == 0xFF) {
            resp[resp_sz++] = 0xFD;
            resp[resp_sz++] = caddr[i] ^ 0x10;
        } else {
            resp[resp_sz++] = caddr[i];
        }
    }
}

static void send_msg(const void *addr, size_t len) {
    const uint8_t *caddr = addr;
    uint8_t ck = 0;
    for (size_t i = 0; i < len; ++i)
        ck += caddr[i];
    ck = -ck;

    resp[0] = 0xFF;
    resp_sz = 1;
    mask_payload(addr, len);
    mask_payload(&ck, 1);
    resp[resp_sz++] = 0xFE;

    respfunc_send_ep(resp_sz, resp);
}

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

static void onenand_read(uint32_t block, uint32_t page, uint16_t *data16) {
    onenand->start_address_1 = block;
    onenand->start_address_2 = 0;
    onenand->start_address_8 = page << 2;

    onenand->start_buffer = (1 << 3) << 8;

    onenand->interrupt = 0;
    onenand->command = 0; // READ

    while ((onenand->interrupt & 0x80) != 0x80)
    {}

    // data16[0] = onenand->ecc_status_register_1;
    // data16[1] = onenand->ecc_status_register_2;
    // data16[2] = onenand->ecc_status_register_3;
    // data16[3] = onenand->ecc_status_register_4;
    // data16[4] = onenand->controller_status;
    // data16[5] = onenand->interrupt;

    for (size_t i = 0; i < 4096/2; ++i)
        data16[i] = onenand->datam[i];
    for (size_t i = 0; i < 128/2; ++i)
        data16[4096/2+i] = onenand->datas[i];
}

#define XADDR(_arr, _off) ((_arr[_off]) | (_arr[_off+1] << 8) | (_arr[_off+2] << 16) | (_arr[_off+3] << 24))

void main(void) {
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

            onenand_read(block, page, onenand_buf);
            // TODO: configurable chunking
            for (uint8_t *sender = (void*)onenand_buf; sender < (uint8_t*)onenand_buf+sizeof(onenand_buf); sender += 64) {
                send_msg(sender, 64);
            }
        } else if (ch == 0x71) {
            /* check if the block is likely SLC or MLC by comparing if first and second 64 pages inside are the same or different */
            uint32_t block = XADDR(payload, 1);
            uint8_t likely_slc = 1;
            uint8_t *scratchbuf = resp;
            for (size_t page = 0; page < 64; ++page) {
                onenand_read(block, page, (void*)scratchbuf);
                onenand_read(block, 64 + page, (void*)(scratchbuf + 4096 + 128));

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
        }
    }
}

__asm__(
".section .text.start\n"
".global start\n"
"start:\n"
    /* disable mmu which got enabled by the jumper */
    "mrc p15, 0, r0, c1, c0, 0\n"
    "bic r0, r0, #0x1\n"
    "bic r0, r0, #0x2\n"
    "bic r0, r0, #0x4\n"
    "mcr p15, 0, r0, c1, c0, 0\n"
    "b main\n"
);
