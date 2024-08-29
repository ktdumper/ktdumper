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

    // TODO: checksum as well?
}

static void receive_msg(void) {
    payload_sz_pre = 0;
    payload_receiver(&payload_sz_pre, payload_pre);
    unmask_payload();
}

static void mask_payload(const void *addr, size_t len) {
    const uint8_t *caddr = addr;

    resp[0] = 0xFF;
    resp_sz = 1;

    for (size_t i = 0; i < len; ++i) {
        if (caddr[i] == 0xFD || caddr[i] == 0xFE || caddr[i] == 0xFF) {
            resp[resp_sz++] = 0xFD;
            resp[resp_sz++] = caddr[i] ^ 0x10;
        } else {
            resp[resp_sz++] = caddr[i];
        }
    }

    resp[resp_sz++] = 0xFE;
}

static void send_msg(const void *addr, size_t len) {
    mask_payload(addr, len);
    // TODO: checksum response?

    respfunc_send_ep(resp_sz, resp);
}

#define XADDR(_arr, _off) ((_arr[_off]) | (_arr[_off+1] << 8) | (_arr[_off+2] << 16) | (_arr[_off+3] << 24))

void main(void) {
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
