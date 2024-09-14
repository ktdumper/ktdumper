#include <inttypes.h>

#include "lib/payload.c"

void dis_int();

int (*usb_getch)() = (void*)KT_usb_getch;
int (*usb_send)() = (void*)KT_usb_send;
int (*usb_send_commit)() = (void*)KT_usb_send_commit;

size_t resp_sz;

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

/* something is busted with our gcc config */
__asm__(
".global dis_int\n"
"dis_int:\n"
".word 0xe10f0000, 0xe1a01000, 0xe3811080, 0xe12ff001, 0xe1a0f00e\n"
);

void runner(void) {
    static uint8_t nandbuf[2112];

    while (1) {
        dis_int();
        uint8_t ch = usb_getch();
        if (ch == 0x42) {
            /* handshake */
            uint8_t resp = 0x43;
            dis_int();
            usb_send(&resp, 1);
            usb_send_commit();

            break;
        }
    }

    payload_main_loop();
}

int main(void) {
    /* restore IRQ so that we don't enter here again */
    *(uint32_t*)0x20 = KT_usb_interrupt;

    /* change fatal_err to jump to runner() */
    uint32_t *hook = (void*)KT_fatal_err;
    *hook++ = 0xe51ff004;
    *hook++ = (uint32_t)runner;

    /* clean dcache line for hook */
    __asm__ volatile ("MCR p15, 0, %0, c7, c10, 1\n" :: "r" ((uint32_t)KT_fatal_err) : "memory");
    __asm__ volatile ("MCR p15, 0, %0, c7, c10, 1\n" :: "r" ((uint32_t)KT_fatal_err+4) : "memory");
    /* invalidate all icache */
    __asm__ volatile ("MCR p15, 0, %0, c7, c5, 0\n" :: "r" (0) : "memory");
}

__asm__(
".section .text.start\n"
".global start\n"
"start:\n"
    // prepare space for chainloaded PC
"    sub sp, #4\n"
"    stmdb sp!,{r0,r1,r2,r3,r4,r5,r12,lr}\n"

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

"    bl main\n"

    // chainload to the real usb interrupt
"    mov r0, #0x20\n"
"    ldr r0, [r0]\n"
"    str r0, [sp,#32]\n"

"    ldmia sp!,{r0,r1,r2,r3,r4,r5,r12,lr,pc}\n"
);
