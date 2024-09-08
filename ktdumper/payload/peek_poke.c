#include <inttypes.h>
#include <stddef.h>

#include "nec_usb_sender.h"

#define BASE %base%

void start() {
    unsigned char *command = (void*)(BASE + 0x400);
    unsigned *data = (void*)(BASE + 0x800);

    unsigned is_wr = command[0];
    unsigned size = command[1];
    unsigned addr = (command[2] << 0) | (command[3] << 8) | (command[4] << 16) | (command[5] << 24);
    unsigned val = (command[6] << 0) | (command[7] << 8) | (command[8] << 16) | (command[9] << 24);
    if (is_wr == 1) {
        switch(size) {
        case 1:
            *(volatile unsigned char*)addr = val;
            break;
        case 2:
            *(volatile unsigned short*)addr = val;
            break;
        case 4:
            *(volatile unsigned*)addr = val;
            break;
        }
    } else if (is_wr == 0) {
        switch(size) {
        case 1:
            *data = *(volatile unsigned char*)addr;
            break;
        case 2:
            *data = *(volatile unsigned short*)addr;
            break;
        case 4:
            *data = *(volatile unsigned*)addr;
            break;
        }
    }
}
