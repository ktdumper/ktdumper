import struct
import time
import usb.core
import sys
import zlib

from dump.dumper import Dumper
from util.payload_builder import PayloadBuilder


FOMA_VID = 0x04c5
FOMA_PID = 0x10ca
PAYLOAD_BASE = 0xE0000000
EXTRA_BUILD_ARGS = ["-ffixed-r4", "-ffixed-r5"]
AP_BASE = 0xe6c20000


def make_srec_s3(dst, data):
    payload_sz = 1 + 4 + len(data)
    assert payload_sz < 0x100

    payload = bytearray(payload_sz)
    payload[0] = payload_sz
    payload[1:5] = struct.pack(">I", dst)
    payload[5:] = data

    assert len(payload) == payload_sz

    return "S3" + payload.hex() + bytes([~(sum(payload) & 0xFF) & 0xFF]).hex()


def make_s7(dst):
    payload_sz = 1 + 4
    assert payload_sz < 0x100

    payload = bytearray(payload_sz)
    payload[0] = payload_sz
    payload[1:5] = struct.pack(">I", dst)

    assert len(payload) == payload_sz

    return "S7" + payload.hex() + bytes([~(sum(payload) & 0xFF) & 0xFF]).hex()


def mask_packet(pkt):
    out = []
    for ch in pkt:
        if ch in [0xFF, 0xFE]:
            out.append(0xFE)
            out.append(ch ^ 0x10)
        else:
            out.append(ch)
    out.append(0xFF)
    return bytearray(out)


def unmask_resp(resp):
    out = []
    x = 0
    while x < len(resp):
        if resp[x] == 0x99:
            out.append(resp[x+1] ^ 0x10)
            x += 2
        else:
            out.append(resp[x])
            x += 1
    return bytearray(out)


class ShG1Protocol(Dumper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = []

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts.get("nand_data", 0)
        self.nand_addr = opts.get("nand_addr", 0)
        self.nand_cmd = opts.get("nand_cmd", 0)

        self.f_reboot = opts.get("reboot", 0xe0601938)
        self.f_usb_reset = opts.get("usb_reset", 0xe0603318)
        self.f_usb_getch = opts.get("usb_getch", 0xe0602c9c)
        self.f_usb_send = opts.get("usb_send", 0xe0602f58)
        self.f_usb_send_commit = opts.get("usb_send_commit", 0xe06029f0)

    def wait_for_srec(self):
        time.sleep(0.5)
        while True:
            dev = usb.core.find(idVendor=FOMA_VID, idProduct=FOMA_PID)
            if dev is not None:
                time.sleep(0.5)
                return usb.core.find(idVendor=FOMA_VID, idProduct=FOMA_PID)
            print("Waiting for srec mode...")
            time.sleep(1)

    def wait_for_reconnect(self):
        print("Waiting for the device to disconnect...")
        while True:
            dev = usb.core.find(idVendor=FOMA_VID, idProduct=FOMA_PID)
            if dev is None:
                break
            time.sleep(0.01)

        print("Waiting for the device to reconnect...")
        while True:
            dev = usb.core.find(idVendor=FOMA_VID, idProduct=FOMA_PID)
            if dev is not None:
                time.sleep(1)
                dev = usb.core.find(idVendor=FOMA_VID, idProduct=FOMA_PID)
                break
            time.sleep(0.01)
        return dev

    def run_payload(self, payload, twoway_handshake=False):
        self.dev.ctrl_transfer(0x41, 0x62, 0x00, 0, b"\x02\xC0")
        time.sleep(0.5)
        self.dev.ctrl_transfer(0x41, 0x60, 0xC0, 0)
        time.sleep(0.5)

        if twoway_handshake:
            self.dev.write(3, bytes.fromhex("FF 55 00 42 00 01 01 FE"))

        handshake = bytearray(self.dev.read(0x82, 4096))
        assert handshake == bytes.fromhex("4442800000000008")

        for x in range(0, len(payload), 0x80):
            data = make_srec_s3(PAYLOAD_BASE + x, payload[x:x+0x80])
            assert self.dev.write(3, data) == len(data)

        self.dev.write(3, make_s7(PAYLOAD_BASE))

    def _read_fully(self, sz):
        data = b""
        while len(data) < sz:
            data += self.dev.read(0x82, 512)
        if sz != len(data):
            print("_read_fully: requested={} got={}".format(sz, len(data)))
            print("data dump => {}".format(data.hex()))
        assert len(data) == sz
        return data

    def usb_send(self, data):
        ck = (-sum(data)) & 0xFF
        pkt = mask_packet(bytearray(data) + bytes([ck]))
        assert self.dev.write(3, pkt) == len(pkt)

    def _usb_readch(self):
        while not len(self.buffer):
            resp = self.dev.read(0x82, 512)
            # print("_usb_readch: {}".format(bytearray(resp).hex()))
            for b in resp:
                self.buffer.append(b)

        return self.buffer.pop(0)

    def usb_receive(self):
        resp = []

        over = False
        while not over:
            # start retrieving chunk, first ch=9B
            ch = self._usb_readch()
            assert ch == 0x9B

            # retrieve body of the chunk
            while True:
                ch = self._usb_readch()

                # 9D = chunk is over
                if ch == 0x9D:
                    # SYNC
                    self.dev.write(3, b"\xAA")
                    break
                # 9C = whole payload is over
                elif ch == 0x9C:
                    over = True
                    break
                # 9A = padding
                elif ch == 0x9A:
                    pass
                else:
                    resp.append(ch)

        data = bytearray(unmask_resp(resp))
        # print("<= {}".format(data.hex()))

        # checksum is the last 4 bytes
        crc = struct.unpack("<I", data[-4:])[0]
        assert zlib.crc32(data[:-4]) == crc

        return data[:-4]

    def readb(self, addr):
        self.usb_send(struct.pack("<BI", 0x10, addr))
        return struct.unpack("B", self.usb_receive())[0]

    def readh(self, addr):
        self.usb_send(struct.pack("<BI", 0x11, addr))
        return struct.unpack("<H", self.usb_receive())[0]

    def readw(self, addr):
        self.usb_send(struct.pack("<BI", 0x12, addr))
        return struct.unpack("<I", self.usb_receive())[0]

    def writeb(self, val, addr):
        self.usb_send(struct.pack("<BIB", 0x20, addr, val))

    def writeh(self, val, addr):
        self.usb_send(struct.pack("<BIH", 0x21, addr, val))

    def writew(self, val, addr):
        self.usb_send(struct.pack("<BII", 0x22, addr, val))

    def read64(self, addr):
        self.usb_send(struct.pack("<BI", 0x60, addr))
        return self.usb_receive()

    def read2048(self, addr):
        self.usb_send(struct.pack("<BI", 0x61, addr))
        return self.usb_receive()

    def read(self, addr, size):
        assert size % 64 == 0
        orig = size

        data = b""
        while size > 0:
            if size >= 2048:
                data += self.read2048(addr)
                addr += 2048
                size -= 2048
            else:
                data += self.read64(addr)
                addr += 64
                size -= 64

        assert len(data) == orig
        return data

    def execute(self, dev, output):
        self.output = output

        print("Enter maker mode...")

        # validate support for mode =0xC0
        data = bytearray(dev.ctrl_transfer(0x41, 0x62, 0x00, 0, b"\x02\xC0"))
        dev.read(0x81, 256)

        # set ep to mode 0xC0
        dev.ctrl_transfer(0x41, 0x60, 0xC0, 0)
        dev.read(0x81, 256)

        # enter maker mode
        dev.write(3, bytes.fromhex("FF 56 55 42 00 03 C1 01 00 FE"))

        time.sleep(0.5)

        print("Enter srec mode...")
        dev.write(3, bytes.fromhex("FF 55 56 42 00 01 01 FE"))

        self.dev = self.wait_for_srec()
        print("Got srec mode, stage 1...")

        payload = PayloadBuilder("g1_reset.c", EXTRA_BUILD_ARGS).build(base=PAYLOAD_BASE, reboot=self.f_reboot)
        payload += b"\x00" * (32 * 1024 - len(payload))
        self.run_payload(payload)

        self.dev = self.wait_for_reconnect()
        print("Got srec mode, stage 2...")

        ap_payload = PayloadBuilder("g1_ap.c").build(base=AP_BASE, nand_data=self.nand_data, nand_cmd=self.nand_cmd, nand_addr=self.nand_addr)
        assert len(ap_payload) < 0x800
        payload = PayloadBuilder("g1_payload.c", EXTRA_BUILD_ARGS).build(
            base=PAYLOAD_BASE,
            shellcode=",".join(hex(x) for x in ap_payload),
            usb_reset=self.f_usb_reset,
            usb_getch=self.f_usb_getch,
            usb_send=self.f_usb_send,
            usb_send_commit=self.f_usb_send_commit,
        )
        payload += b"\x00" * (32 * 1024 - len(payload))
        self.run_payload(payload, twoway_handshake=True)

        self.dev = self.wait_for_reconnect()
        print("Got payload mode, stage 3...")
        # now communicating with out payload, check handshake
        self.dev.write(3, b"\x42")
        data = bytearray(self._read_fully(1))
        assert data == b"\x43"

        print("Validating...")

        # validate payload set up correctly
        self.writew(0xDEADBEEF, AP_BASE+0x1800)
        assert self.readw(AP_BASE+0x1800) == 0xDEADBEEF
        self.writeh(0xEE, AP_BASE+0x1800)
        assert self.readw(AP_BASE+0x1800) == 0xDEAD00EE

        print("Completed!")
