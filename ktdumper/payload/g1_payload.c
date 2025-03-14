#include <inttypes.h>
#include <stddef.h>

#include "g1_ap.h"

__asm__(
    ".global dis_int\n"
    "dis_int:\n"
    ".word 0xe10f0000, 0xe1a01000, 0xe3811080, 0xe12ff001, 0xe1a0f00e\n"
);
void dis_int(void);

int (*usb_reset)() = (void*)0xe0603318;
int (*usb_getch)() = (void*)0xe0602c9c;
int (*usb_send)() = (void*)0xe0602f58;
int (*usb_send_commit)() = (void*)0xe06029f0;

void send(void *buf, size_t sz) {
    usb_send(buf, sz);
    usb_send_commit();
}

uint8_t shellcode[0x2000] = { %shellcode% };

#define AP_STS ((*(volatile uint32_t*)0x50401ffc))
#define AP_CMD ((*(volatile uint32_t*)0x50401ff8))
#define AP_ARG ((*(volatile uint32_t*)0x50401ff0))
#define AP_ARGS (((volatile uint32_t*)0x50401ff0))

uint8_t ap_read8(uint32_t addr) {
    AP_STS = 0;
    AP_ARG = addr;
    AP_CMD = CMD_AP_READ8;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

uint16_t ap_read16(uint32_t addr) {
    AP_STS = 0;
    AP_ARG = addr;
    AP_CMD = CMD_AP_READ16;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

uint32_t ap_read32(uint32_t addr) {
    AP_STS = 0;
    AP_ARG = addr;
    AP_CMD = CMD_AP_READ32;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

void ap_write8(uint8_t val, uint32_t addr) {
    AP_STS = 0;
    AP_ARGS[0] = addr;
    AP_ARGS[1] = val;
    AP_CMD = CMD_AP_WRITE8;
    while (1) {
        if (AP_STS)
            return;
    }
}

void ap_write16(uint16_t val, uint32_t addr) {
    AP_STS = 0;
    AP_ARGS[0] = addr;
    AP_ARGS[1] = val;
    AP_CMD = CMD_AP_WRITE16;
    while (1) {
        if (AP_STS)
            return;
    }
}

void ap_write32(uint32_t val, uint32_t addr) {
    AP_STS = 0;
    AP_ARGS[0] = addr;
    AP_ARGS[1] = val;
    AP_CMD = CMD_AP_WRITE32;
    while (1) {
        if (AP_STS)
            return;
    }
}

uint32_t ap_read(uint32_t addr) {
    AP_STS = 0;
    AP_ARG = addr;
    AP_CMD = CMD_AP_READ;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

uint32_t ap_read2048(uint32_t addr) {
    AP_STS = 0;
    AP_ARG = addr;
    AP_CMD = CMD_AP_READ2048;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

uint32_t ap_readnand(uint32_t page) {
    AP_STS = 0;
    AP_ARG = page;
    AP_CMD = CMD_AP_READNAND;
    while (1) {
        if (AP_STS)
            return AP_ARG;
    }
}

void start_ap(void) {
    volatile uint16_t *DAT_39060410 = (void*)0x39060410;
    volatile uint32_t *DAT_50401ff8 = (void*)0x50401ff8;
    volatile uint32_t *DAT_51000038 = (void*)0x51000038;
    volatile uint32_t *DAT_70000000 = (void*)0x70000000;
    volatile uint32_t *DAT_66180014 = (void*)0x66180014;
    volatile uint32_t *DAT_50800004 = (void*)0x50800004;
    volatile uint16_t *DAT_50800000 = (void*)0x50800000;

    AP_STS = 0;

    *DAT_39060410 &= 0xFFFE;
    *DAT_39060410 |= 2;
    while (1) {
        *DAT_50800004 = 0x80;
        if ((*DAT_50800004 & 0xC0) == 0)
            break;
        for (volatile int i = 0; i < 2000; ++i) {}
    }

    uint8_t *dst = (uint8_t*)0x50400000;
    for (size_t i = 0; i < sizeof(shellcode); ++i) {
        dst[i] = shellcode[i];
    }

    *DAT_50401ff8 |= 0x101;

    do {
        *DAT_51000038 &= 0xffffff0f;
    } while ((*DAT_51000038 & 0xF0) != 0);

    *DAT_70000000 = 0xe0000000;

    *DAT_66180014 = *DAT_66180014 & 0xfff | 0xe6c20000;

    do {
        *DAT_51000038 &= 0xfffffbff;
    } while ((*DAT_51000038 & 0x400) != 0);

    *DAT_50800004 = 0x80;
    *DAT_50800000 &= 0xff3f;

    while (1) {
        if (AP_STS == 0xBBBAAA)
            break;
        for (volatile int i = 0; i < 1000; ++i) {}
    }
}

size_t resp_sz;
uint8_t payload[0x100], resp[0x4000];

void receive_msg(void) {
    size_t sz = 0;

    while (1) {
        dis_int();
        uint8_t ch = usb_getch();
        if (ch == 0xFF) {
            break;
        } else if (ch == 0xFE) {
            dis_int();
            ch = usb_getch() ^ 0x10;
        }
        payload[sz++] = ch;
    }

    uint8_t ck = 0;
    for (size_t i = 0; i < sz; ++i)
        ck += payload[i];

    if (ck != 0 || sz == 0) {
        while (1) {}
    }
}

static void mask_payload(const void *addr, size_t len) {
    const uint8_t *caddr = addr;

    for (size_t i = 0; i < len; ++i) {
        if (caddr[i] == 0x99 || caddr[i] == 0x9A || caddr[i] == 0x9B || caddr[i] == 0x9C || caddr[i] == 0x9D) {
            resp[resp_sz++] = 0x99;
            resp[resp_sz++] = caddr[i] ^ 0x10;
        } else {
            resp[resp_sz++] = caddr[i];
        }
    }
}

#ifndef KT_chunk
#define KT_chunk 64
#endif

#define CHUNK (KT_chunk - 2)

#define XADDR(_arr, _off) ((_arr[_off]) | (_arr[_off+1] << 8) | (_arr[_off+2] << 16) | (_arr[_off+3] << 24))

static void send_chunked_entry(const void *addr, size_t sz, int is_last) {
    const uint8_t *caddr = addr;

    uint8_t data[CHUNK+2];
    for (size_t i = 0; i < sizeof(data); ++i)
        data[i] = 0x9A;

    data[0] = 0x9B;
    for (size_t i = 0; i < sz; ++i)
        data[1 + i] = caddr[i];
    data[sizeof(data)-1] = is_last ? 0x9C : 0x9D;

    dis_int();
    usb_send(data, sizeof(data));
    usb_send_commit();

    /* SYNC */
    if (!is_last) {
        dis_int();
        usb_getch();
    }
}

static void send_chunked(const void *addr, size_t sz) {
    const uint8_t *caddr = addr;

    for (size_t off = 0; off < sz; off += CHUNK) {
        size_t chunk = CHUNK;
        if (chunk > sz - off)
            chunk = sz - off;
        send_chunked_entry(caddr + off, chunk, sz == off+chunk);
    }
}

/* https://web.archive.org/web/20190108202303/http://www.hackersdelight.org/hdcodetxt/crc.c.txt */
uint32_t crc32b(const uint8_t *message, size_t sz) {
   uint32_t byte, crc, mask;

   crc = 0xFFFFFFFF;
   for (size_t i = 0; i < sz; ++i) {
      byte = message[i];            // Get next byte.
      crc = crc ^ byte;
      for (int j = 7; j >= 0; j--) {    // Do eight times.
         mask = -(crc & 1);
         crc = (crc >> 1) ^ (0xEDB88320 & mask);
      }
   }
   return ~crc;
}

void send_msg(const void *addr, size_t len) {
    const uint8_t *caddr = addr;
    uint32_t crc = crc32b(caddr, len);

    resp_sz = 0;
    mask_payload(addr, len);
    mask_payload(&crc, sizeof(crc));

    send_chunked(resp, resp_sz);
}

void go(void) {
    uint8_t *dstbuf = (uint8_t*)0x50401000;

    while (1) {
        receive_msg();

        uint8_t ch = payload[0];
        if (ch == 0x10 || ch == 0x11 || ch == 0x12) {
            /* read */
            uint32_t addr = XADDR(payload, 1);
            uint32_t resp, resplen;

            switch (ch) {
            case 0x10:
                resp = ap_read8(addr);
                resplen = 1;
                break;
            case 0x11:
                resp = ap_read16(addr);
                resplen = 2;
                break;
            case 0x12:
                resp = ap_read32(addr);
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
                ap_write8(data, addr);
                break;
            case 2:
                ap_write16(data, addr);
                break;
            case 4:
                ap_write32(data, addr);
                break;
            }
        } else if (ch == 0x60) {
            /* read 64 bytes from AP */
            uint32_t addr = XADDR(payload, 1);
            ap_read(addr);
            send_msg(dstbuf, 64);
        } else if (ch == 0x61) {
            /* read 2048 bytes from AP */
            uint32_t addr = XADDR(payload, 1);
            ap_read2048(addr);
            send_msg(dstbuf, 2048);
        } else if (ch == 0x52) {
            /* nand_LP_read */
            uint32_t page = XADDR(payload, 1);
            ap_readnand(page);
            send_msg(dstbuf, 0x841);
        }
    }
}

void main(void) {
    *(volatile uint16_t*)0x39060412 |= 8;
    for (volatile int i = 0; i < 1000000; ++i) {}
    usb_reset();
    for (volatile int i = 0; i < 100000; ++i) {}

    start_ap();

    int ch = usb_getch();
    if (ch == 0x42) {
        uint8_t handshake = 0x43;
        send(&handshake, sizeof(handshake));
        go();
    }

    while (1) {}
}

__asm__(
".section .text.start\n"
".global start\n"
"start:\n"
    // clean data cache and flush icache before jumping to rest of payload
    // hopefully increase stability bc we only need 1-2 cache lines to hit
"    ldr r0, =%base%\n"
"    ldr r1, =%base%+0x10000\n"
"loop:\n"
"    mcr p15, 0, r0, c7, c10, 1\n"
"    add r0, r0, #32\n"
"    cmp r0, r1\n"
"    bne loop\n"
"    mov r0, #0\n"
"    mcr p15, 0, r0, c7, c5, 0\n"

"    b main\n"
);
