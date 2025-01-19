import struct
from dump.sony.sony_mdoc_dumper_slow_v2 import SonyMdocDumperSlow_v2


class SonyMdocDumper_v2(SonyMdocDumperSlow_v2):

    def read_sector(self, part, sector):
        self.usb_send(struct.pack("<BBI", 0x80, part, sector))
        data = self.usb_receive()
        return data
