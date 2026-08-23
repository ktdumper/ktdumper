#include <stdint.h>

#define QueueTx     ((int (*)(uint8_t *, uint16_t, void *))0x1214Cu)
#define ArmRx       ((void (*)(uint8_t *))0x12550u)
#define CancelTimer ((void (*)(uint32_t))0x0EABCu)
#define TIMER_PTR    (*(volatile uint32_t *)0x101Cu)

#define TXQ_STATE   (*(volatile uint8_t *)0x3952u)
#define TXQ_WRITE   (*(volatile uint8_t *)0x39A4u)
#define TXQ_READ    (*(volatile uint8_t *)0x39A5u)

#define MAX_CHUNK 48

static uint8_t tx_byte_buf;
static uint8_t tx_done;

static uint8_t volatile *rx_frame;
static uint16_t rx_consumed;

static void send(uint8_t b)
{
    tx_byte_buf = b;
    QueueTx(&tx_byte_buf, 1u, &tx_done);
    while (TXQ_WRITE != TXQ_READ || TXQ_STATE != 3u)
        ;
}

static uint8_t tx_block_buf[64];
static uint8_t tx_block_done;

static void usb_send(const uint8_t *p, uint32_t sz)
{
    uint8_t i;
    for (i = 0; i < sz; i++)
        tx_block_buf[i] = p[i];
    QueueTx(tx_block_buf, sz, &tx_block_done);
    while (TXQ_WRITE != TXQ_READ || TXQ_STATE != 3u)
        ;
}

#define RX_ARM() \
    do { rx_consumed = 0; ArmRx((uint8_t *)rx_frame); } while (0)

static uint8_t recv(void)
{
    for (;;) {
        uint32_t avail = *(volatile uint32_t *)(rx_frame + 0x810u);
        if (rx_consumed < avail) {
            uint8_t b = rx_frame[0x002u + rx_consumed];
            rx_consumed++;
            if (rx_consumed == avail)
                RX_ARM();
            return b;
        }
    }
}
