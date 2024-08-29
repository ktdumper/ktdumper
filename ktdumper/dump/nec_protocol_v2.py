from dump.nec_protocol import NecProtocol, mask_packet
from util.payload_builder import PayloadBuilder


class NecProtocol_v2(NecProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.payload_base = opts["payload_base"]

        self.f_usb_receive = opts.get("usb_receive")
        self.f_usb_send = opts.get("usb_send")

    def usb_send(self, data):
        # TODO: mask_packet currently appends checksum but this needs to be changed after it stops doing it
        masked = mask_packet(data)

        # print("=> {}".format(masked.hex()))
        self.dev.write(0x8, masked)

    def usb_receive(self):
        data = self.read_resp()
        # print("<= {}".format(data.hex()))

        # checksum is the last byte
        ck = (-sum(data[:-1])) & 0xFF
        assert data[-1] == ck
        return data[:-1]

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
        )

        self.cmd_write(self.payload_base, payload)
        self.cmd_exec()

        self.magic_handshake()

        print("!! Restart the phone before running another payload !!")
