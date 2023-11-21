import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.common_rw_access import CommonRwAccess


NAND_CMD_READID = 0x90


class NecNandDumperLpViaPoke(CommonRwAccess, NecProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts["nand_data"]
        self.nand_addr = opts["nand_addr"]
        self.nand_cmd = opts["nand_cmd"]

    def nand_dump_page(self, page):
        # READ0
        self.writeh(0x00, self.nand_cmd)

        self.writeh(0x00, self.nand_addr)
        self.writeh(0x00, self.nand_addr)
        self.writeh(page & 0xFF, self.nand_addr)
        self.writeh((page >> 8) & 0xFF, self.nand_addr)
        self.writeh((page >> 16) & 0xFF, self.nand_addr)

        # READSTART
        self.writeh(0x30, self.nand_cmd)

        # we don't check for interrupt because usb protocol is very slow

        out = b""
        for x in range(0x420):
            data = self.readh(self.nand_data)
            out += struct.pack("<H", data)
        return out

    def execute(self, dev, output):
        super().execute(dev, output)

        for page in range(0, 2 ** 32):
            print(self.nand_dump_page(page).hex())
