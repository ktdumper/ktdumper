from dump.sony.sony_protocol_v2 import SonyProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2


class SonyProbeMdoc_v2(RwAccess_v2, SonyProtocol_v2):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.sweep_start = opts["sweep_start"]

    def read_id(self, base):
        addr_chip_id = base + 0x1400
        addr_chip_id_flip = addr_chip_id + 0x22

        chip_id = self.readh(addr_chip_id)
        chip_id_flip = self.readh(addr_chip_id_flip)

        s = "CID : 0x{:04X} | ~CID : 0x{:04X}".format(chip_id, chip_id_flip)
        if chip_id == (~chip_id_flip & 0xFFFF):
            s += " => possible match"
        return s

    def execute(self, dev, output):
        super().execute(dev, output)

        for addr in range(self.sweep_start, 2**32, 0x01000000):
            print("0x{:08X} :: {}".format(addr, self.read_id(addr)))
