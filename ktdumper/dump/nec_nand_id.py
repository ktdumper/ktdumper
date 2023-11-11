import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_rw_access import NecRwAccess


NAND_CMD_READID = 0x90


class NecNandId(NecRwAccess):

    def __init__(self, payload_base, nand_data, nand_addr, nand_cmd, quirks=0):
        super().__init__(payload_base, quirks)

        self.nand_data = nand_data
        self.nand_addr = nand_addr
        self.nand_cmd = nand_cmd

    def execute(self, dev, output):
        super().execute(dev, output)

        self.writeb(NAND_CMD_READID, self.nand_cmd)
        self.writeb(0, self.nand_addr)

        print("flash id: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format(
            self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data), self.readb(self.nand_data)))
