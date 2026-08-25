import struct
from dump.v2.mdoc_dumper_v2 import MdocDumper_v2
from dump.sony.sony_protocol_v2 import SonyProtocol_v2


class MdocDumper_v2(SonyProtocol_v2):

    def read_sector(self, part, sector):
        self.usb_send(struct.pack("<BBI", 0x80, part, sector))
        data = self.usb_receive()
        return data