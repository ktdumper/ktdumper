import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_rw_access import NecRwAccess


NAND_CMD_READID = 0x90


class NecNandDumperLpViaPoke(NecRwAccess):

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

    def gpio_out(self, num, val):
        goe = 0x10000 << num
        gos = (1 << num) if val else 0
        self.writew(goe | gos, 0xc0050008)

    def execute(self, dev, output):
        super().execute(dev, output)

        # self.writeb(NAND_CMD_READID, self.nand_cmd)
        # self.writeb(0, self.nand_addr)

        # print("flash id: 0x{:X} 0x{:X} 0x{:X} 0x{:X} 0x{:X}".format(
        #     self.readh(self.nand_data), self.readh(self.nand_data), self.readh(self.nand_data), self.readh(self.nand_data), self.readh(self.nand_data)))

        # self.gpio_out(0xF, 1)

        for page in range(1024, 2048):
            print(self.nand_dump_page(page).hex())
