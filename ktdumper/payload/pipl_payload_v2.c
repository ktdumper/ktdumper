#include <inttypes.h>
#include <stddef.h>

#include "lib/payload.c"

int (*payload_receiver)() = (void*)KT_usb_receive;
int (*respfunc_send_ep)() = (void*)KT_usb_send;

uint32_t payload_sz_pre, payload_sz, resp_sz;
uint8_t payload_pre[0x100];

static void unmask_payload(void) {
    payload[0] = 0;

    if (payload_sz_pre <= 9)
        while(1){};

    payload_sz = payload_sz_pre - 9;
    for (int i = 0; i < payload_sz; ++i)
        payload[i] = payload_pre[i + 9];

    uint8_t ck = 0;
    for (size_t i = 0; i < payload_sz_pre; ++i)
        ck += payload_pre[i];

    if (ck != 0)
        while(1){};
}

void receive_msg(void) {
    payload_sz_pre = 0;
    payload_receiver(&payload_sz_pre, payload_pre);
    unmask_payload();
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
#define KT_chunk 48
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

    respfunc_send_ep(sizeof(data), data);
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

void main(void) {
    payload_main_loop();
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

    "b main\n"
);
