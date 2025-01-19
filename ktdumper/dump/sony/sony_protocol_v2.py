import struct
import time
import zlib

from dump.dumper import Dumper
from util.payload_builder import PayloadBuilder


CODE_BASE = 0x40210000


def make_micropayload(cmd, subcmd, payload=b""):
    return struct.pack(">BBBBI", cmd, subcmd, 0, 0, len(payload)) + payload


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


class SonyProtocol_v2(Dumper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = []

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.payload_base = CODE_BASE
        self.f_recv_ch = opts["recv_ch"]
        self.f_usb_send = opts["usb_send"]

        self.nand_data = opts.get("nand_data", 0)
        if not self.nand_data:
            self.nand_data = opts.get("mdoc_base", 0)
        self.nand_addr = opts.get("nand_addr", 0)
        self.nand_cmd = opts.get("nand_cmd", 0)

        self.onenand_addr = opts.get("onenand_addr", 0)

    def _read_fully(self, sz):
        data = b""
        while len(data) < sz:
            data += self.dev.read(0x82, 512)
        if sz != len(data):
            print("_read_fully: requested={} got={}".format(sz, len(data)))
            print("data dump => {}".format(data.hex()))
        assert len(data) == sz
        return data

    def execute(self, dev, output):
        self.output = output
        self.dev = dev

        # handshake
        assert bytearray(self.dev.read(0x82, 64)) == bytes.fromhex("a3 a9 63")

        # enter the D7 00 mode
        self.dev.write(3, bytes.fromhex("ff e9e342 0800 00 00 D7 00 fe"))
        self.dev.read(0x82, 64)

        payload = PayloadBuilder("sony_v2.c").build(
            base=self.payload_base,
            recv_ch=self.f_recv_ch,
            usb_send=self.f_usb_send,

            nand_data=self.nand_data,
            nand_cmd=self.nand_cmd,
            nand_addr=self.nand_addr,
            onenand_addr=self.onenand_addr,
        )

        # for cache burst
        payload += b"\x00" * (0x40000 - len(payload))

        # write payload in memory
        chunk = 256
        for off in range(0, len(payload), chunk):
            self.dev.write(3, make_micropayload(0x74, 0xE9, struct.pack(">I", self.payload_base + off) + payload[off:off+chunk] + b"\x00\x00"))
            self.dev.read(0x82, 64)

        # and jump to it
        self.dev.write(3, make_micropayload(0x75, 0xE9, struct.pack(">I", self.payload_base)))

        time.sleep(0.5)

        self.dev.write(3, b"\x42")
        data = bytearray(self.dev.read(0x82, 1))
        assert data == b"\x43"

        # self.dev.write(3, b"\xAA")
        # print("leaking", bytearray(self.dev.read(0x82, 512)).hex())

    def usb_send(self, data):
        ck = (-sum(data)) & 0xFF
        pkt = mask_packet(bytearray(data) + bytes([ck]))
        # print("usb_send: {}".format(pkt.hex()))
        assert self.dev.write(3, pkt) == len(pkt)

    def _usb_readch(self):
        while not len(self.buffer):
            resp = self.dev.read(0x82, 64)
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
