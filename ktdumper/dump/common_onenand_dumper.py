import tqdm
import struct

from dump.common_rw_access import CommonRwAccess
from util.payload_builder import PayloadBuilder


class CommonOnenandDumper(CommonRwAccess):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        assert opts["size"] % 2048 == 0
        self.num_pages = opts["size"] // 2048
        self.onenand_addr = opts["onenand_addr"]

        self.onenand_REG_START_ADDRESS1 = self.onenand_addr + 2*0xF100
        self.onenand_REG_START_ADDRESS2 = self.onenand_addr + 2*0xF101
        self.onenand_REG_START_ADDRESS8 = self.onenand_addr + 2*0xF107
        self.onenand_REG_START_BUFFER = self.onenand_addr + 2*0xF200
        self.onenand_REG_INTERRUPT = self.onenand_addr + 2*0xF241
        self.onenand_REG_COMMAND = self.onenand_addr + 2*0xF220
        self.onenand_DATARAM = self.onenand_addr + 2*0x200
        self.onenand_SPARERAM = self.onenand_addr + 2*0x8010

    def _onenand_read(self, page, cmd, read_ptr, read_sz):
        self.writeh(page // 64, self.onenand_REG_START_ADDRESS1)
        self.writeh(0, self.onenand_REG_START_ADDRESS2)
        self.writeh((page % 64) << 2, self.onenand_REG_START_ADDRESS8)

        self.writeh((1 << 3) << 8, self.onenand_REG_START_BUFFER)

        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(cmd, self.onenand_REG_COMMAND)

        # NOTE: not listening for the interrupt/read to complete, assume usb is slow enough it's not needed

        return self.read(read_ptr, read_sz)

    def onenand_read_page(self, page):
        return self._onenand_read(page, 0x00, self.onenand_DATARAM, 0x800)

    def onenand_read_oob(self, page):
        return self._onenand_read(page, 0x13, self.onenand_SPARERAM, 64)

    def execute(self, dev, output):
        super().execute(dev, output)

        print("Dumping OneNAND")
        with output.mkfile("onenand.bin") as outf:
            with tqdm.tqdm(total=2048*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    outf.write(self.onenand_read_page(page))
                    bar.update(2048)

        print("Dumping OOB")
        with output.mkfile("onenand.oob") as outf:
            with tqdm.tqdm(total=64*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    outf.write(self.onenand_read_oob(page))
                    bar.update(64)
