size_t resp_sz;

void receive_msg(void) {
    size_t sz = 0;

    while (1) {
        uint8_t ch = recv();
        if (ch == 0xFF) {
            break;
        } else if (ch == 0xFE) {
            ch = recv() ^ 0x10;
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

    usb_send(data, sizeof(data));

    /* SYNC */
    if (!is_last) {
        recv();
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
