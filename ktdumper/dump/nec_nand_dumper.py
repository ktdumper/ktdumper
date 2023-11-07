import tqdm
import struct

from dump.nec_protocol import NecProtocol
from util.payload_builder import PayloadBuilder


class NecNandDumper(NecProtocol):

    def __init__(self, size, payload_base=0x10000000, nand_addr=0x04000000, quirks=0):
        super().__init__(quirks)
        assert size % 512 == 0
        self.num_pages = size // 512
        self.payload_base = payload_base
        self.nand_addr = nand_addr

        self.payload_COMMAND = self.payload_base+0x400
        self.payload_OUTPUT = self.payload_base+0x800

    def nand_read_page(self, page):
        data = b""

        self.write(self.payload_COMMAND, struct.pack("<IB", page, 0))
        self.cmd_exec()
        data += self.read(self.payload_OUTPUT, 256)

        self.write(self.payload_COMMAND, struct.pack("<IB", page, 1))
        self.cmd_exec()
        data += self.read(self.payload_OUTPUT, 256)

        return data

    def nand_read_oob(self, page):
        self.write(self.payload_COMMAND, struct.pack("<IB", page, 2))
        self.cmd_exec()
        return self.read(self.payload_OUTPUT, 16)

    def execute(self, dev, output):
        super().execute(dev, output)

        payload = PayloadBuilder("nec_dump_nand.c").build(base=self.payload_base, nand=self.nand_addr)
        self.cmd_write(self.payload_base, payload)

        print("Dumping NAND")
        with output.mkfile("nand.bin") as outf:
            with tqdm.tqdm(total=512*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    outf.write(self.nand_read_page(page))
                    bar.update(512)

        print("Dumping OOB")
        with output.mkfile("nand.oob") as outf:
            with tqdm.tqdm(total=16*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    outf.write(self.nand_read_oob(page))
                    bar.update(16)
