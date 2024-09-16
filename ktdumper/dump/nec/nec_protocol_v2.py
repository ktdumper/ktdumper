import zlib
import struct

from dump.nec.nec_protocol import NecProtocol
from util.payload_builder import PayloadBuilder


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


class NecProtocol_v2(NecProtocol):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.buffer = []

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.payload_base = opts["payload_base"]

        self.f_usb_receive = opts.get("usb_receive")
        self.f_usb_send = opts.get("usb_send")

    def usb_send(self, data):
        # TODO: mask_packet currently appends checksum but this needs to be changed after it stops doing it
        masked = self.mask_packet(data)

        # print("=> {}".format(masked.hex()))
        self.dev.write(0x8, masked)

    def _usb_readch(self):
        while not len(self.buffer):
            resp = self.dev.read(0x87, 64)
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

    def magic_handshake(self):
        self.usb_send(bytes([0x42]))
        data = self.usb_receive()
        assert data == bytes.fromhex("55545352")

    def execute(self, dev, output):
        super().execute(dev, output)

        payload = PayloadBuilder("nec_payload_v2.c").build(
            base=self.payload_base,
            usb_receive=self.f_usb_receive,
            usb_send=self.f_usb_send,
            onenand_addr=self.opts.get("onenand_addr", -1),
            nand_data=self.opts.get("nand_data", -1),
            nand_addr=self.opts.get("nand_addr", -1),
            nand_cmd=self.opts.get("nand_cmd", -1),
        )

        self.cmd_write(self.payload_base, payload)
        self.cmd_exec()

        self.magic_handshake()

        print("!! Restart the phone before running another payload !!")
