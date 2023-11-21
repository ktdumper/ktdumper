import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.common_rw_access import CommonRwAccess


NAND_CMD_READID = 0x90


class NecNandId(CommonRwAccess, NecProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts["nand_data"]
        self.nand_addr = opts["nand_addr"]
        self.nand_cmd = opts["nand_cmd"]

    def execute(self, dev, output):
        super().execute(dev, output)

        self.writeb(NAND_CMD_READID, self.nand_cmd)
        self.writeb(0, self.nand_addr)

        print("flash id: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format(
            self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data)))
